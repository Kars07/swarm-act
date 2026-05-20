import modal
import json
import random

# Define the app and connect to your existing storage volume
app = modal.App("bct-swarm-prep")
storage_volume = modal.Volume.from_name("bct-swarm-storage")

DATA_DIR = "/workspace/data/processed"

@app.function(volumes={"/workspace/data": storage_volume})
def prep_phase3_data():
    input_file = f"{DATA_DIR}/agent_alpha_sft.jsonl"
    eval_file = f"{DATA_DIR}/eval_set.jsonl"
    grpo_file = f"{DATA_DIR}/grpo_prompts.jsonl"

    SAMPLE_SIZE = 1000

    print(f"Loading dataset from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Randomly sampling {SAMPLE_SIZE} rows...")
    random.seed(42) # Keep it reproducible
    sampled_lines = random.sample(lines, SAMPLE_SIZE)

    # 1. Save the Eval Set (Includes the ground-truth answers for scoring)
    print(f"Writing Eval Set to {eval_file}...")
    with open(eval_file, 'w', encoding='utf-8') as f:
        for line in sampled_lines:
            f.write(line)

    # 2. Save the GRPO Prompts (Strips out the assistant's answer)
    print(f"Writing GRPO Prompts to {grpo_file}...")
    with open(grpo_file, 'w', encoding='utf-8') as f:
        for line in sampled_lines:
            data = json.loads(line)

            # Extract the raw text and split it right where the assistant is supposed to answer
            text = data.get("text", "")

            # This isolates the prompt and leaves the "<|im_start|>assistant\n" hook
            prompt_only = text.split("<|im_start|>assistant")[0] + "<|im_start|>assistant\n"

            # For GRPO, trl expects a list of dictionaries with a "prompt" key
            f.write(json.dumps({"prompt": prompt_only}) + "\n")

    print("✅ Data preparation complete!")

    # Optional: Let's explicitly commit the volume changes just to be safe
    storage_volume.commit()

@app.local_entrypoint()
def main():
    prep_phase3_data.remote()
