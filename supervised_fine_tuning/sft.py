import modal
import os
from trl import SFTConfig


# Define the production app
app = modal.App("bct-swarm-sft")
# 1. Image Definition: The Fully Synced, Locked Matrix
sft_image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install("git", "build-essential")
    .env({"BNB_CUDA_VERSION": "124"})

    .pip_install(
        "torch==2.5.1",
        "torchvision==0.20.1",
        "torchaudio==2.5.1",
        "nvidia-nvjitlink",
        "nvidia-cuda-nvrtc",
        "git+https://github.com/huggingface/transformers.git",
        "torchao==0.6.1",
        "bitsandbytes",
        "trl<0.12.0",
        "accelerate",
        "datasets",
        "peft==0.13.2",         # <-- THE FIX: Pin PEFT to match the PyTorch 2.5.1 era
        "xformers",
        "unsloth-zoo",
        extra_index_url="https://download.pytorch.org/whl/cu124"
    )

    .run_commands(
        "pip install --no-deps git+https://github.com/unslothai/unsloth-zoo.git git+https://github.com/unslothai/unsloth.git"
    )
)
# 2. Storage Setup
storage_volume = modal.Volume.from_name("bct-swarm-storage")
CACHE_DIR = "/workspace/data/model_cache"
DATA_DIR = "/workspace/data/processed"
ADAPTER_DIR = "/workspace/data/adapters"

# 3. Training Function Factory
# We explicitly request a high-tier GPU. Modal supports H100s, A100s.
# Swap "H100" with "A100" if you need to manage your compute credits more aggressively.
@app.function(
    image=sft_image,
    volumes={"/workspace/data": storage_volume},
    gpu="H100",
    timeout=43200 # 4 hours max per run
)
def train_agent(agent_name: str, dataset_file: str, epochs: int = 3):

    import transformers.trainer
    import transformers.utils.import_utils

    def bypass_torch_load_check():
        pass

    transformers.utils.import_utils.check_torch_load_is_safe = bypass_torch_load_check
    transformers.trainer.check_torch_load_is_safe = bypass_torch_load_check
        # -----------------------------------
    from unsloth import FastLanguageModel
    from datasets import load_dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments
    import torch

    print(f"--- INITIALIZING SFT FOR {agent_name.upper()} ---")
    os.makedirs(ADAPTER_DIR, exist_ok=True)

    # Locate the 4B base model we cached in Phase 1
    model_id = "Qwen_Qwen3.5-4B"
    model_path = f"{CACHE_DIR}/{model_id}"

    max_seq_length = 4096 # Kept reasonable for SFT; we expand this in Phase 4

    # 1. Load Model with Unsloth Optimization
    print("Loading Base Model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_path,
        max_seq_length = max_seq_length,
        dtype = None, # Auto-detects bf16 for H100/A100
        load_in_4bit = True, # Use NF4 quantization
    )

    # 2. Apply Custom LoRA Strategy (From Architecture Doc)
    # Target Modules: Attention (Q/K/V/O), MLP (Gate/Up/Down), LM_Head
    print("Injecting LoRA Adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = 128, # High rank for complex behavioral capture
        target_modules = [
            "q_proj", "k_proj", "v_proj", "o_proj", # Attention
            "gate_proj", "up_proj", "down_proj",    # MLP
            "lm_head"                               # Task-specific head
        ],
        lora_alpha = 256,
        lora_dropout = 0, # 0 is required for Unsloth optimizations
        bias = "none",
        use_gradient_checkpointing = "unsloth", # Massive VRAM savings
        random_state = 3407,
    )

    # 3. Load Dataset
    print(f"Loading Dataset: {dataset_file}...")
    dataset = load_dataset("json", data_files=f"{DATA_DIR}/{dataset_file}", split="train")

    # Format standard ChatML using Unsloth's mapper
    def formatting_prompts_func(examples):
        return {"text": examples["text"]} # Our Phase 1 pipeline already formatted the chat template

    dataset = dataset.map(formatting_prompts_func, batched = True)

    from transformers import Trainer

    _original_init = Trainer.__init__
    def _patched_init(self, *args, **kwargs):
        if "tokenizer" in kwargs:
            kwargs["processing_class"] = kwargs.pop("tokenizer") # Rename it mid-flight
        _original_init(self, *args, **kwargs)
    Trainer.__init__ = _patched_init

    # Extract the pure text tokenizer (fixes the Base64 padding error)
    text_tokenizer = getattr(tokenizer, "tokenizer", tokenizer)


    # 4. SFT Trainer Setup
    print("Configuring Trainer...")
    trainer = SFTTrainer(
        model = model,
        tokenizer = text_tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False, # Set to False for ChatML formatting safety
        args = SFTConfig(
            per_device_train_batch_size = 4,
            gradient_accumulation_steps = 4,
            output_dir = f"/workspace/data/model_cache/{agent_name}_checkpoints", # Keep this one
            save_strategy = "steps",
            save_steps = 500,
            save_total_limit = 3,
            resume_from_checkpoint = True,
            warmup_steps = 50,
            num_train_epochs = epochs,
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 10,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            # (Deleted the duplicate output_dir here)
        ),
    )
    # 5. Smart Checkpoint Resumption
    checkpoint_dir = f"/workspace/data/model_cache/{agent_name}_checkpoints"
    resume = False

    # Check if the directory exists and actually contains 'checkpoint-X' folders
    if os.path.exists(checkpoint_dir):
        checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith("checkpoint")]
        if len(checkpoints) > 0:
            resume = True
            print(f"Found existing checkpoints. Resuming training...")
        else:
            print("No checkpoints found. Starting fresh...")

# THE FINAL CHECKPOINT HOTFIX: Force PyTorch to trust our local checkpoint files
    import torch
    _original_torch_load = torch.load
    def _patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False # Disable the strict NumPy block
        return _original_torch_load(*args, **kwargs)
    torch.load = _patched_torch_load

    # 5. Execute Training
    print(f"Starting Training Loop for {agent_name}...")
    trainer_stats = trainer.train(resume_from_checkpoint=resume)

    # 6. Save Final Adapter
    final_path = f"{ADAPTER_DIR}/{agent_name}_sft_final"
    model.save_pretrained(final_path) # Saves ONLY the LoRA weights (~500MB)
    tokenizer.save_pretrained(final_path)

    print(f"--- {agent_name.upper()} TRAINING COMPLETE ---")
    print(f"Adapter saved to {final_path}")

@app.local_entrypoint()
def main():
    # Execute sequentially on the cloud to avoid GPU contention
    # Agent-Alpha has a massive dataset, 1 epoch is plenty for initial SFT
    train_agent.remote(agent_name="alpha", dataset_file="agent_alpha_sft.jsonl", epochs=1)

    # Agent-Beta has a highly curated, smaller dataset. 3 epochs forces it to learn the reasoning schema.
    train_agent.remote(agent_name="beta", dataset_file="agent_beta_sft.jsonl", epochs=3)
