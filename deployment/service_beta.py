import modal
from fastapi import Request

# Restored the NVIDIA Devel image so the compiler is present
image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install("git", "build-essential")
    .pip_install("vllm", "fastapi", "ninja", "safetensors")
    # Explicitly disable FlashInfer sampling to prevent C++ JIT crashes
    .env({"VLLM_USE_FLASHINFER_SAMPLER": "0", "VLLM_WORKER_MULTIPROC_METHOD": "spawn"})
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
            gpu_memory_utilization=0.90,
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
        
        # Max tokens increased to 2048 to accommodate longer reasoning tags
        sampling_params = SamplingParams(
            temperature=0.15,
            repetition_penalty=1.15,
            max_tokens=2048,
            stop_token_ids=[self.tokenizer.eos_token_id],
            stop=["<|im_end|>", "<|im_start|>", "<|eot_id|>", "<|end_of_text|>", "\n<|im_start|>", "\nuser\n", "\nassistant\n", "\nuser:", "\nassistant:"]
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
        
        # Robust JSON repair and parse function
        def repair_and_parse_json(text: str) -> dict:
            try:
                return json.loads(text)
            except Exception:
                pass
                
            start_idx = text.find('{')
            if start_idx == -1:
                return {}
            
            candidate = text[start_idx:].strip()
            
            end_idx = candidate.rfind('}')
            if end_idx != -1:
                try:
                    return json.loads(candidate[:end_idx+1])
                except Exception:
                    pass
                    
            if candidate.endswith(']'):
                try:
                    return json.loads(candidate + '}')
                except Exception:
                    pass
                    
            open_braces = candidate.count('{')
            close_braces = candidate.count('}')
            open_brackets = candidate.count('[')
            close_brackets = candidate.count(']')
            
            repaired = candidate
            quotes = repaired.count('"')
            if quotes % 2 != 0:
                repaired += '"'
                
            if open_brackets > close_brackets:
                repaired = repaired.rstrip(', \n\r')
                if not repaired.endswith('"') and not repaired.endswith(']'):
                    last_quote = repaired.rfind('"')
                    if last_quote != -1:
                        repaired = repaired[:last_quote+1]
                repaired += ']'
                
            open_braces = repaired.count('{')
            close_braces = repaired.count('}')
            if open_braces > close_braces:
                repaired += '}' * (open_braces - close_braces)
                
            try:
                return json.loads(repaired)
            except Exception as e:
                print(f"Failed to repair JSON: {repaired}. Error: {e}")
                return {}

        def extract_ranked_items_fallback(text: str) -> list:
            # 1. Strip thinking tags
            clean_text = text
            for tag in ["</thinking>", "</think>"]:
                if tag in clean_text:
                    clean_text = clean_text.split(tag)[-1]
                    break
                    
            # 2. Search for the LAST occurrence of "ranked_items" or "<ranking_result>"
            target_area = clean_text
            matches = list(re.finditer(r'"ranked_items"\s*:\s*', clean_text, re.IGNORECASE))
            if matches:
                target_area = clean_text[matches[-1].end():]
                # Find matching brackets if possible
                start_bracket = target_area.find('[')
                if start_bracket != -1:
                    bracket_count = 0
                    end_bracket = -1
                    for i, char in enumerate(target_area[start_bracket:]):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_bracket = start_bracket + i
                                break
                    if end_bracket != -1:
                        target_area = target_area[start_bracket:end_bracket+1]
                    else:
                        target_area = target_area[start_bracket:]
            else:
                tag_matches = list(re.finditer(r'<ranking_result>', clean_text, re.IGNORECASE))
                if tag_matches:
                    target_area = clean_text[tag_matches[-1].end():]
                    end_tag = re.search(r'</ranking_result>', target_area, re.IGNORECASE)
                    if end_tag:
                        target_area = target_area[:end_tag.start()]

            # Extract all possible candidates (both quoted strings and raw words)
            candidates = []
            
            # Extract quoted strings
            quoted = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', target_area)
            # Also extract raw words that look like base64 IDs or preset IDs
            raw_words = re.findall(r'\b[a-zA-Z0-9_\-]{10,40}\b', target_area)
            
            potential_ids = quoted + raw_words
            
            # Filter candidates by length and structure
            for q in potential_ids:
                q_clean = q.strip()
                if not q_clean:
                    continue
                # Check if it matches a standard 22-char base64 Yelp ID
                is_base64_id = len(q_clean) == 22 and re.match(r'^[a-zA-Z0-9_\-]{22}$', q_clean)
                # Check if it matches a preset target ID pattern (e.g. ramen_shop_992, cafe_cafe_883)
                is_preset_id = re.match(r'^[a-zA-Z0-9]+_[a-zA-Z0-9_]+_\d+$', q_clean)
                
                if is_base64_id or is_preset_id:
                    candidates.append(q_clean)
                    
            # Remove duplicates while preserving order
            seen = set()
            final_candidates = []
            for c in candidates:
                if c not in seen:
                    seen.add(c)
                    final_candidates.append(c)
                    
            return final_candidates

        def extract_and_parse_beta_json(text: str) -> dict:
            # 1. Strip any thinking blocks to avoid monologue interference
            clean_text = text
            for tag in ["</thinking>", "</think>"]:
                if tag in clean_text:
                    parts = clean_text.split(tag)
                    clean_text = parts[-1]
            
            clean_text = clean_text.strip()
            
            # 2. Find all '{' positions in reverse order (from end to start)
            brace_indices = [i for i, char in enumerate(clean_text) if char == '{']
            
            # Try from the last '{' to the first
            for idx in reversed(brace_indices):
                candidate_area = clean_text[idx:].strip()
                parsed_candidate = repair_and_parse_json(candidate_area)
                if parsed_candidate and "ranked_items" in parsed_candidate:
                    # Post-process and sanitize ranked_items to extract string IDs and strip monologue pollution
                    raw_items = parsed_candidate["ranked_items"]
                    sanitized_items = []
                    if isinstance(raw_items, list):
                        for item in raw_items:
                            # If it's a dictionary structure (like {"rank": 0, "item_id": "..."})
                            item_str = ""
                            if isinstance(item, dict):
                                item_str = item.get("item_id", item.get("ground_truth_item_id", ""))
                            elif isinstance(item, str):
                                item_str = item
                                
                            item_clean = item_str.strip()
                            # Check if the extracted string matches Yelp Base64 format or preset ID
                            is_base64_id = len(item_clean) == 22 and re.match(r'^[a-zA-Z0-9_\-]{22}$', item_clean)
                            is_preset_id = re.match(r'^[a-zA-Z0-9]+_[a-zA-Z0-9_]+_\d+$', item_clean)
                            if is_base64_id or is_preset_id:
                                sanitized_items.append(item_clean)
                                
                    parsed_candidate["ranked_items"] = sanitized_items
                    return parsed_candidate
                    
            # Fallback to standard repair on the clean text if no reverse matches succeeded
            return repair_and_parse_json(clean_text)

        parsed = {}
        try:
            parsed = extract_and_parse_beta_json(raw_gen)
        except Exception as e:
            print(f"Extraction parsing warning: {e}")
            
        if not parsed or "ranked_items" not in parsed or not parsed["ranked_items"]:
            try:
                fallback_items = extract_ranked_items_fallback(raw_gen)
                if fallback_items:
                    parsed = {"ranked_items": fallback_items}
            except Exception as e:
                print(f"Fallback parsing warning: {e}")
            
        return {"raw_output": raw_gen, "parsed_json": parsed}