import modal
from fastapi import Request

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("vllm", "fastapi", "ninja", "safetensors")
    .env({
        "VLLM_USE_FLASHINFER_SAMPLER": "0", 
        "VLLM_WORKER_MULTIPROC_METHOD": "spawn",
        "VLLM_FP8_KERNEL_BACKEND": "none",
        "VLLM_SKIP_WARMUP": "1"  # <--- THIS IS THE CRITICAL KILL-SWITCH
    })
)

app = modal.App("bct-beta-service")
storage_volume = modal.Volume.from_name("bct-swarm-storage")

@app.cls(
    image=image,
    volumes={"/workspace/data": storage_volume},
    gpu="H100",
    min_containers=0,
    max_containers=1,
    scaledown_window=1800,
    startup_timeout=600  
)
class BetaService:
    @modal.enter()
    def initialize_engine(self):
        import json
        import os
        import torch
        from safetensors import safe_open
        from safetensors.torch import save_file
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.engine.async_llm_engine import AsyncLLMEngine
        from transformers import AutoTokenizer
        
        self.original_adapter_dir = "/workspace/data/adapters/beta_grpo_final"
        self.vllm_adapter_dir = "/workspace/data/adapters/beta_grpo_vllm_safe"
        
        # =====================================================================
        # SANITIZER: Create a vLLM-compatible adapter by stripping 'lm_head'
        # =====================================================================
        if not os.path.exists(self.vllm_adapter_dir):
            print("🔧 Creating vLLM-compatible Beta adapter...")
            os.makedirs(self.vllm_adapter_dir, exist_ok=True)
            
            with open(os.path.join(self.original_adapter_dir, "adapter_config.json"), "r") as f:
                cfg = json.load(f)
            if "target_modules" in cfg and isinstance(cfg["target_modules"], list):
                cfg["target_modules"] = [m for m in cfg["target_modules"] if "lm_head" not in m]
            with open(os.path.join(self.vllm_adapter_dir, "adapter_config.json"), "w") as f:
                json.dump(cfg, f, indent=4)
                
            safetensors_path = os.path.join(self.original_adapter_dir, "adapter_model.safetensors")
            bin_path = os.path.join(self.original_adapter_dir, "adapter_model.bin")
            
            if os.path.exists(safetensors_path):
                tensors = {}
                with safe_open(safetensors_path, framework="pt", device="cpu") as f:
                    for k in f.keys():
                        if "lm_head" not in k:
                            tensors[k] = f.get_tensor(k)
                save_file(tensors, os.path.join(self.vllm_adapter_dir, "adapter_model.safetensors"))
                
            elif os.path.exists(bin_path):
                tensors = torch.load(bin_path, map_location="cpu")
                filtered_tensors = {k: v for k, v in tensors.items() if "lm_head" not in k}
                torch.save(filtered_tensors, os.path.join(self.vllm_adapter_dir, "adapter_model.bin"))
                
            print("✅ Sanitized Beta adapter successfully saved.")

        # =====================================================================
        # BOOT THE VLLM ENGINE
        # =====================================================================
        with open(os.path.join(self.vllm_adapter_dir, "adapter_config.json"), "r") as f:
            adapter_config = json.load(f)
            
        base_model_path = adapter_config.get("base_model_name_or_path")
        print(f"🎯 Discovered Base Model: {base_model_path}")
        print("⚡ Mounting Agent-Beta via vLLM on H100...")

        engine_args = AsyncEngineArgs(
            model=base_model_path,
            tensor_parallel_size=1,
            gpu_memory_utilization=0.85,
            max_model_len=4096,
            enforce_eager=True,  
            enable_lora=True,
            max_loras=1,
            max_lora_rank=128,
            gdn_prefill_backend="triton"  
        )
        
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        self.tokenizer = AutoTokenizer.from_pretrained(self.original_adapter_dir)

    @modal.fastapi_endpoint(method="POST")
    async def generate(self, req: Request):
        import json
        import re
        import uuid
        from vllm import SamplingParams
        from vllm.lora.request import LoRARequest

        data = await req.json()
        
        messages = [
            {"role": "system", "content": "You are a reasoning recommendation system. You must output an internal monologue inside <thinking>...</thinking> tags, followed by a valid JSON object containing the key 'ranked_items'."},
            {"role": "user", "content": f"Request: {data['prompt']}\nAlpha Analysis Input: {json.dumps(data['alpha_insight'])}"}
        ]
        
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        # Max tokens increased to 1024 to accommodate reasoning tags
        sampling_params = SamplingParams(
            temperature=0.15,
            repetition_penalty=1.15,
            max_tokens=1024,
            stop_token_ids=[self.tokenizer.eos_token_id]
        )
        
        request_id = str(uuid.uuid4())
        lora_request = LoRARequest("beta_adapter", 1, self.vllm_adapter_dir)
        
        results_generator = self.engine.generate(
            prompt, 
            sampling_params, 
            request_id,
            lora_request=lora_request
        )
        
        final_output = ""
        async for request_output in results_generator:
            final_output = request_output.outputs[0].text
            
        raw_gen = final_output.strip()
        
        parsed = {}
        try:
            # Isolate the JSON part strictly after the thinking tags
            json_area = raw_gen.split("</thinking>")[-1].strip() if "</thinking>" in raw_gen else raw_gen
            start_idx = json_area.find('{')
            end_idx = json_area.rfind('}')
            if start_idx != -1 and end_idx != -1:
                parsed = json.loads(json_area[start_idx:end_idx+1])
        except Exception as e:
            print(f"Extraction parsing warning: {e}")
            
        return {"raw_output": raw_gen, "parsed_json": parsed}