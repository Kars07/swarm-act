import requests
import json

# Replace with your actual Deployed Swarm Orchestrator URL
URL = "https://wakamateservices--bct-swarm-orchestrator-swarm-endpoint.modal.run/v1/swarm/process"

payload = {
    "target_item_id": "item_88492",
    "prompt": "The customer was looking for a high-performance GPU programming guide, specifically for CUDA and CuTe on Blackwell architecture. They prefer low-level optimizations over frameworks."
}

print("🚀 Sending request to the unified Swarm Orchestrator...")
print("This orchestrates Agent Alpha (rating & review generation) and Agent Beta (reasoning & items ranking) sequentially.")
print("This may take 1-2 mins if the containers are cold starting.\n")

try:
    response = requests.post(URL, json=payload, timeout=600)
    
    if response.status_code == 200:
        print("✅ SUCCESS! Swarm Orchestrator Response:\n")
        data = response.json()
        
        print("--- Agent Alpha Extraction (SFT + GRPO Review/Rating Insight) ---")
        print(json.dumps(data.get("alpha_extraction", {}), indent=4))
        
        print("\n--- Agent Beta Reasoning (Monologue + Ranked Items) ---")
        beta_res = data.get("beta_reasoning", {})
        print("💡 Raw Monologue:")
        print(beta_res.get("raw_monologue", "No thinking block."))
        
        print("\n📦 Payload (Beta Ranked Items):")
        print(json.dumps(beta_res.get("payload", {}), indent=4))
        
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Exception occurred: {e}")
