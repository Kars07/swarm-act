import modal
import os

eval_image = (
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
        "peft==0.13.2",
        "xformers",
        "unsloth-zoo",
        extra_index_url="https://download.pytorch.org/whl/cu124"
    )
    .run_commands(
        "pip install --no-deps git+https://github.com/unslothai/unsloth-zoo.git git+https://github.com/unslothai/unsloth.git"
    )
)

app = modal.App("bct-swarm-eval-beta")
storage_volume = modal.Volume.from_name("bct-swarm-storage")

CACHE_DIR = "/workspace/data/model_cache"
DATA_DIR = "/workspace/data/processed"
ADAPTER_DIR = "/workspace/data/adapters"

@app.function(
    image=eval_image,
    volumes={"/workspace/data": storage_volume},
    gpu="H100",
    timeout=3600
)
def run_beta_evaluation():
    import json
    import re
    from unsloth import FastLanguageModel
    import torch
    import torch._dynamo

    # Bypass the PyTorch cache limit crash
    torch._dynamo.config.cache_size_limit = 1024

    print(f"--- STARTING SFT EVALUATION FOR AGENT: BETA ---")

    # Point to Beta's final GRPO weights
    adapter_path = f"{ADAPTER_DIR}/beta_grpo_final"

    if not os.path.exists(adapter_path):
        print(f"CRITICAL ERROR: Could not find Beta's adapter at {adapter_path}. Did the training finish?")
        return

    print("Loading optimized model & fine-tuned adapters...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = adapter_path,
        max_seq_length = 4096,
        dtype = None,
        load_in_4bit = True,
    )
    FastLanguageModel.for_inference(model)
    text_tokenizer = getattr(tokenizer, "tokenizer", tokenizer)

    # Note: Ensure you point this to Beta's specific eval dataset if it has a separate one!
    # For now, we will assume it's stored in the same place or has a specific beta_eval_set.jsonl
    eval_path = f"{DATA_DIR}/eval_set.jsonl" 
    print(f"Reading evaluation dataset from {eval_path}...")

    prompts = []
    
    # We are just going to grab the prompts from the eval set for generation
    with open(eval_path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            full_text = row.get("text", "")
            parts = full_text.split("<|im_start|>assistant\n")
            if len(parts) >= 2:
                prompts.append(parts[0] + "<|im_start|>assistant\n")
            
            # Let's cap it at 100 for a fast Beta benchmark
            if len(prompts) >= 100:
                break

    print(f"Running generation loop for {len(prompts)} Beta prompts...")

    predictions = []
    batch_size = 32

    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i+batch_size]
        inputs = text_tokenizer(batch_prompts, return_tensors="pt", padding=True).to("cuda")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                use_cache=True,
                temperature=0.15,
                top_p=0.9,
                repetition_penalty=1.15,
                pad_token_id=text_tokenizer.pad_token_id,
                eos_token_id=text_tokenizer.eos_token_id
            )

        for j, out in enumerate(outputs):
            input_len = inputs.input_ids[j].shape[0]
            gen_text = text_tokenizer.decode(out[input_len:], skip_special_tokens=True).strip()
            predictions.append(gen_text)

        print(f"Processed completions: {len(predictions)} / {len(prompts)}")

    successful_parses = 0
    successful_reasoning = 0
    failed_parses = 0

    print(f"Validating Beta's <thinking> tags and 'ranked_items' schema...")

    for pred_text in predictions:
        # Check for reasoning tags
        if "<thinking>" in pred_text and "</thinking>" in pred_text:
            successful_reasoning += 1

        try:
            # 1. Isolate the text after the thinking block
            if "</thinking>" in pred_text:
                raw_json_area = pred_text.split("</thinking>")[-1].strip()
            else:
                raw_json_area = pred_text

            # 2. Extract from the absolute first '{' to the absolute last '}'
            start_idx = raw_json_area.find('{')
            end_idx = raw_json_area.rfind('}')

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON payload block observed")

            clean_json_str = raw_json_area[start_idx:end_idx+1]
            pred_json = json.loads(clean_json_str)

            # 3. Verify Beta's specific schema
            if "ranked_items" not in pred_json:
                 raise ValueError(f"Missing 'ranked_items' key. Found keys: {list(pred_json.keys())}")

            successful_parses += 1

        except Exception as e:
            failed_parses += 1
            # Optional: 
            print(f"Parse error: {e}")

    print(f"\n==========================================")
    print(f"FINAL STRUCTURAL REPORT: AGENT-BETA")
    print(f"==========================================")
    print(f"Total Evaluated              : {len(prompts)}")
    print(f"Successfully Parsed JSON     : {successful_parses}")
    print(f"Successfully Used <thinking> : {successful_reasoning}")
    print(f"Failed / Malformed Outputs   : {failed_parses}")
    print(f"==========================================\n")

@app.local_entrypoint()
def main():
    run_beta_evaluation.remote()