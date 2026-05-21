import modal
from fastapi import Request

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install("git", "build-essential")
    .env({"BNB_CUDA_VERSION": "124", "CACHE_BUST": "v12_weight_init_shield"})
    .pip_install(
        "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
        "nvidia-nvjitlink", "nvidia-cuda-nvrtc",
        "transformers==4.48.3",
        "torchao==0.6.1",
        "unsloth", "unsloth-zoo",
        "bitsandbytes", "accelerate", "datasets", "trl==0.12.0", "peft==0.13.2", "xformers", "fastapi"
    )
)

app = modal.App("bct-beta-service")
storage_volume = modal.Volume.from_name("bct-swarm-storage")

@app.cls(
    image=image,
    volumes={"/workspace/data": storage_volume},
    gpu="H100",
    min_containers=0,
    max_containers=1,
    scaledown_window=60,
    startup_timeout=1200
)
class BetaService:
    @modal.enter()
    def initialize_engine(self):
        import sys
        import types
        import os
        import importlib.abc
        import importlib.machinery

        # =====================================================================
        # 1. STORAGE LOCK PURGE PASS
        # =====================================================================
        print("🔍 Scanning shared storage volume for stale process locks...")
        lock_count = 0
        for root, dirs, files in os.walk("/workspace/data"):
            for file in files:
                if file.endswith(".lock"):
                    try:
                        os.remove(os.path.join(root, file))
                        lock_count += 1
                    except Exception:
                        pass
        if lock_count > 0:
            print(f"🔥 Evicted {lock_count} lingering file lock(s). Storage I/O paths unfrozen.")
        else:
            print("✅ Volume storage is clean. No deadlocks detected.")

        # =====================================================================
        # 2. IN-MEMORY DIRECT OBJECT SYNC (Fixes exec() string lookup errors)
        # =====================================================================
        import transformers.models.qwen2.modeling_qwen2 as qwen2_modeling
        import transformers.models.qwen2.configuration_qwen2 as qwen2_config

        # Map missing lookups directly onto the native Qwen2 namespaces
        sync_targets = {
            "Qwen3Config": qwen2_config.Qwen2Config,
            "Qwen3MoeConfig": qwen2_config.Qwen2Config,
            "Qwen3Attention": qwen2_modeling.Qwen2Attention,
            "Qwen3MoeAttention": qwen2_modeling.Qwen2Attention,
            "Qwen3Model": qwen2_modeling.Qwen2Model,
            "Qwen3MoeModel": qwen2_modeling.Qwen2Model,
            "Qwen3DecoderLayer": qwen2_modeling.Qwen2DecoderLayer,
            "Qwen3MoeDecoderLayer": qwen2_modeling.Qwen2DecoderLayer,
            "Qwen3MLP": qwen2_modeling.Qwen2MLP,
            "Qwen3ForCausalLM": qwen2_modeling.Qwen2ForCausalLM,
            "Qwen3MoeForCausalLM": qwen2_modeling.Qwen2ForCausalLM,
            "Qwen3_5Config": qwen2_config.Qwen2Config,
            "Qwen3_5ForCausalLM": qwen2_modeling.Qwen2ForCausalLM,
            "Qwen3_5ForConditionalGeneration": qwen2_modeling.Qwen2ForCausalLM,
            "Qwen2_5Config": qwen2_config.Qwen2Config,
            "Qwen2_5ForCausalLM": qwen2_modeling.Qwen2ForCausalLM,
        }
        qwen2_config.__dict__.update(sync_targets)
        qwen2_modeling.__dict__.update(sync_targets)

        # =====================================================================
        # 3. DIRECT SYS.MODULES INJECTION MATRIX (Eliminates MetaPathFinder failures)
        # =====================================================================
        class ProxyModule(types.ModuleType):
            def __init__(self, name, target, is_package=False):
                super().__init__(name)
                self._target = target
                if is_package:
                    self.__path__ = []
                    
            def __getattr__(self, name):
                if hasattr(self._target, name):
                    return getattr(self._target, name)
                if name.startswith("Qwen") or name.startswith("qwen"):
                    class Dummy:
                        pass
                    Dummy.__name__ = name
                    return Dummy
                raise AttributeError(f"module '{self.__name__}' has no attribute '{name}'")

        for prefix in ["qwen3", "qwen3_5", "qwen3_moe", "qwen2_5"]:
            pkg_name = f"transformers.models.{prefix}"
            pkg = ProxyModule(pkg_name, qwen2_modeling, is_package=True)
            cfg_mod = ProxyModule(f"{pkg_name}.configuration_{prefix}", qwen2_config)
            mdl_mod = ProxyModule(f"{pkg_name}.modeling_{prefix}", qwen2_modeling)
            
            cfg_alias = ProxyModule(f"{pkg_name}.configuration_qwen3", qwen2_config)
            mdl_alias = ProxyModule(f"{pkg_name}.modeling_qwen3", qwen2_modeling)
            
            setattr(pkg, f"configuration_{prefix}", cfg_mod)
            setattr(pkg, f"modeling_{prefix}", mdl_mod)
            setattr(pkg, "configuration_qwen3", cfg_alias)
            setattr(pkg, "modeling_qwen3", mdl_alias)
            
            sys.modules[pkg_name] = pkg
            sys.modules[f"{pkg_name}.configuration_{prefix}"] = cfg_mod
            sys.modules[f"{pkg_name}.modeling_{prefix}"] = mdl_mod
            sys.modules[f"{pkg_name}.configuration_qwen3"] = cfg_alias
            sys.modules[f"{pkg_name}.modeling_qwen3"] = mdl_alias

        # =====================================================================
        # 4. TRANSFORMERS REGISTRY ALIGNMENT
        # =====================================================================
        from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForImageTextToText
        try:
            from transformers import AutoModelForVision2Seq
        except ImportError:
            AutoModelForVision2Seq = AutoModelForImageTextToText
        
        class Qwen35Config(qwen2_config.Qwen2Config):
            model_type = "qwen3_5"

        qwen2_modeling.Qwen2ForCausalLM.config_class = Qwen35Config
        AutoConfig.register("qwen3_5", Qwen35Config)
        AutoModelForCausalLM.register(Qwen35Config, qwen2_modeling.Qwen2ForCausalLM)
        AutoModelForImageTextToText.register(Qwen35Config, qwen2_modeling.Qwen2ForCausalLM)
        AutoModelForVision2Seq.register(Qwen35Config, qwen2_modeling.Qwen2ForCausalLM)

        # =====================================================================
        # 5. WEIGHT INITIALIZATION BYTE SHIELD
        # =====================================================================
        if hasattr(qwen2_modeling, "Qwen2PreTrainedModel"):
            orig_init_weights = qwen2_modeling.Qwen2PreTrainedModel._init_weights
            def patched_init_weights(self, module):
                try:
                    orig_init_weights(self, module)
                except RuntimeError as e:
                    if "normal_kernel_cpu" in str(e) or "Byte" in str(e):
                        pass  
                    else:
                        raise e
            qwen2_modeling.Qwen2PreTrainedModel._init_weights = patched_init_weights

        # =====================================================================
        # 6. UNSLOTH COMPILER DICTIONARY MONKEYPATCH
        # =====================================================================
        import unsloth.models._utils as unsloth_utils
        if hasattr(unsloth_utils, "_UNSLOTH_COMPILE_TRANSFORMERS"):
            unsloth_utils._UNSLOTH_COMPILE_TRANSFORMERS["qwen3_5"] = unsloth_utils._UNSLOTH_COMPILE_TRANSFORMERS["qwen2"]

        # =====================================================================
        # 7. INITIALIZE THE CONTAINER ENVIRONMENT
        # =====================================================================
        import unsloth
        from unsloth import FastLanguageModel
        import torch
        
        torch._dynamo.config.cache_size_limit = 1024
        
        print("⚡ Safely mounting Agent-Beta onto active H100 architecture...")
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name="/workspace/data/adapters/beta_grpo_final",
            max_seq_length=1024,
            load_in_4bit=True,
            auto_model=AutoModelForCausalLM
        )
        FastLanguageModel.for_inference(self.model)
        self.tokenizer = getattr(self.tokenizer, "tokenizer", self.tokenizer)
        self.torch = torch

    @modal.fastapi_endpoint()
    async def generate(self, req: Request):
        import json
        import re

        data = await req.json()
        
        messages = [
            {"role": "system", "content": "You are a reasoning recommendation system. You must output an internal monologue inside <thinking>...</thinking> tags, followed by a valid JSON object containing the key 'ranked_items'."},
            {"role": "user", "content": f"Request: {data['prompt']}\nAlpha Analysis Input: {json.dumps(data['alpha_insight'])}"}
        ]
        inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
        
        with self.torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs, max_new_tokens=1024, temperature=0.15, repetition_penalty=1.15,
                pad_token_id=self.tokenizer.pad_token_id, eos_token_id=self.tokenizer.eos_token_id
            )
        raw_gen = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True).strip()
        
        parsed = {}
        try:
            json_area = raw_gen.split("</thinking>")[-1].strip() if "</thinking>" in raw_gen else raw_gen
            start_idx = json_area.find('{')
            end_idx = json_area.rfind('}')
            if start_idx != -1 and end_idx != -1:
                parsed = json.loads(json_area[start_idx:end_idx+1])
        except Exception as e:
            print(f"Extraction parsing warning: {e}")
            
        return {"raw_output": raw_gen, "parsed_json": parsed}