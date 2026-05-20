import modal

# Re-use our battle-tested, cached SFT image
grpo_image = (
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
        "trl==0.14.0", # The Goldilocks version for GRPO on Torch 2.5.1
        "accelerate",
        "datasets",
        "peft==0.13.2",
        "xformers",
        "unsloth-zoo",
        extra_index_url="https://download.pytorch.org/whl/cu124"
    )
    .run_commands(
        "pip install --no-deps git+https://github.com/unslothai/unsloth-zoo.git git+https://github.com/unslothai/unsloth.git"
    )
)

app = modal.App("bct-swarm-grpo")
storage_volume = modal.Volume.from_name("bct-swarm-storage")

CACHE_DIR = "/workspace/data/model_cache"
DATA_DIR = "/workspace/data/processed"
ADAPTER_DIR = "/workspace/data/adapters"

@app.function(
    image=grpo_image,
    volumes={"/workspace/data": storage_volume},
    gpu="H100",
    timeout=43200
)
def run_grpo_alignment(agent_name: str):
    import json
    import re
    import torch
    import torch._dynamo
    import os
    from datasets import load_dataset
    from unsloth import FastLanguageModel, PatchFastRL
    from trl import GRPOTrainer, GRPOConfig
    from transformers import TrainerCallback

    # Max out both the per-function and global accumulator cache limits to completely avoid CacheLimitExceeded
    torch._dynamo.config.cache_size_limit = 100000
    torch._dynamo.config.accumulated_cache_size_limit = 100000

    # Patch Unsloth for optimized RLHF generation memory management
    PatchFastRL("GRPO", FastLanguageModel)

    print(f"\n{'='*50}\n🚀 INITIATING GRPO ALIGNMENT FOR: {agent_name.upper()}\n{'='*50}")

    # Configure directory path for checkpoint scanning
    output_dir = f"{ADAPTER_DIR}/{agent_name}_grpo_temp"
    latest_checkpoint = None
    
    # Scan for existing checkpoints on the volume to resume cleanly from advanced weights
    if os.path.exists(output_dir):
        checkpoints = [d for d in os.listdir(output_dir) if d.startswith("checkpoint")]
        if checkpoints:
            checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
            latest_checkpoint = os.path.join(output_dir, checkpoints[-1])

    # 1. Load the Model Weights (Prioritizing Checkpoints via Safetensors)
    if latest_checkpoint:
        print(f"Found clean weights at {latest_checkpoint}. Loading adapter weights directly to skip broken state tracking...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = latest_checkpoint,
            max_seq_length = 1024,
            dtype = None,
            load_in_4bit = True,
        )
    else:
        adapter_path = f"{ADAPTER_DIR}/{agent_name}_sft_final"
        print(f"No active checkpoints found. Loading Base SFT Model from {adapter_path}...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = adapter_path,
            max_seq_length = 1024,
            dtype = None,
            load_in_4bit = True,
        )

    # 2. Load the Unlabelled Prompts
    prompts_path = f"{DATA_DIR}/grpo_prompts.jsonl"
    print(f"Loading unlabelled prompts from {prompts_path}...")
    dataset = load_dataset("json", data_files=prompts_path, split="train")

    # =====================================================================
    # 3. THE REWARD JUDGES (The Kill Squad)
    # =====================================================================

    def task_a_enforcer(prompts, completions, **kwargs):
        """Kills the Task B Identity Crisis & verifies exact JSON keys."""
        rewards = []
        for completion in completions:
            if "ranked_items" in completion:
                rewards.append(-3.0)
                continue

            try:
                json_match = re.search(r"\{.*\}", completion, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    if "predicted_rating" in parsed and "predicted_review" in parsed:
                        rewards.append(2.0)
                    else:
                        rewards.append(-1.0)
                else:
                    rewards.append(-2.0)
            except:
                rewards.append(-2.0)
        return rewards
    def task_b_enforcer(prompts, completions, **kwargs):
        """Kills the Task A Identity Crisis for Beta & verifies exact JSON keys."""
        rewards = []
        for completion in completions:
            # Punish Beta if it tries to output Alpha's review schema
            if "predicted_rating" in completion or "predicted_review" in completion:
                rewards.append(-3.0)
                continue

            try:
                json_match = re.search(r"\{.*\}", completion, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    # Reward Beta for correctly outputting Task B's schema
                    if "ranked_items" in parsed:
                        rewards.append(2.0)
                    else:
                        rewards.append(-1.0)
                else:
                    rewards.append(-2.0)
            except:
                rewards.append(-2.0)
        return rewards

    def amnesia_enforcer(prompts, completions, **kwargs):
        """Kills the EOS loop. Penalizes hallucinated conversational turns."""
        rewards = []
        for completion in completions:
            if "<|im_start|>" in completion or "assistant\n" in completion or "user\n" in completion:
                rewards.append(-2.0)
            else:
                rewards.append(0.5)
        return rewards

    def markdown_enforcer(prompts, completions, **kwargs):
        """Kills the chatty preamble and markdown code block wrappers."""
        rewards = []
        for completion in completions:
            text = completion.strip()
            if text.startswith("```") or text.endswith("```"):
                rewards.append(-2.0)
            elif text.startswith("{") and text.endswith("}"):
                rewards.append(1.0)
            else:
                rewards.append(-1.0)
        return rewards

    def reasoning_enforcer(prompts, completions, **kwargs):
        """(Beta Only) Rewards the explicit use of thinking tags before JSON."""
        rewards = []
        for completion in completions:
            if "<thinking>" in completion and "</thinking>" in completion:
                json_idx = completion.find('{')
                think_idx = completion.find('</thinking>')
                if json_idx != -1 and think_idx < json_idx:
                    rewards.append(1.5)
                else:
                    rewards.append(-1.0)
            else:
                rewards.append(-2.0)
        return rewards

    if agent_name == "alpha":
        reward_funcs = [task_a_enforcer, amnesia_enforcer, markdown_enforcer]
        print("-> Injected Task A Enforcer for Agent-Alpha.")
    elif agent_name == "beta":
        reward_funcs = [task_b_enforcer, amnesia_enforcer, markdown_enforcer, reasoning_enforcer]
        print("-> Injected Task B & Reasoning Enforcers for Agent-Beta.")

    # 4. GRPO CONFIGURATION
    training_args = GRPOConfig(
        output_dir=output_dir,
        learning_rate=5e-6,
        logging_steps=10,
        max_steps=100,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_generations=4,
        max_prompt_length=512,
        max_completion_length=512,
        beta=0.1,
        report_to="none",
        save_strategy="steps",
        save_steps=25,
        save_total_limit=2,
    )

    # Inject the runtime dictionary TRL requires to avoid the Unsloth auto_model AttributeError
    if getattr(model, "warnings_issued", None) is None:
        model.warnings_issued = {}
    if hasattr(model, "base_model") and getattr(model.base_model, "warnings_issued", None) is None:
        model.base_model.warnings_issued = {}

    # Custom callback ensuring every single checkpoint interval is instantly synchronized to the storage volume
    class ModalVolumeCommitCallback(TrainerCallback):
        def on_save(self, args, state, control, **kwargs):
            print(f"Checkpoint saved at step {state.global_step}. Committing Modal volume to prevent data loss...")
            storage_volume.commit()

    trainer = GRPOTrainer(
        model=model,
        reward_funcs=reward_funcs,
        args=training_args,
        train_dataset=dataset,
        callbacks=[ModalVolumeCommitCallback()]
    )

    print("Commencing GRPO Rollouts...")
    trainer.train()

    # 5. Save the final aligned model safely to the volume
    final_output_path = f"{ADAPTER_DIR}/{agent_name}_grpo_final"
    print(f"Alignment complete! Saving production-ready adapter to {final_output_path}")
    model.save_pretrained(final_output_path)
    tokenizer.save_pretrained(final_output_path)

    # Flush the volume to ensure it saves
    storage_volume.commit()
    print(f"--- GRPO PIPELINE FINISHED FOR {agent_name.upper()} ---")

@app.local_entrypoint()
def main():
    # Run Alpha's alignment
    # run_grpo_alignment.remote(agent_name="alpha")

    # Run Beta's alignment
    run_grpo_alignment.remote(agent_name="beta")