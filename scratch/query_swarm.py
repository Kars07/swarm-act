import requests
import json

URL = "https://wakamateservices--bct-swarm-orchestrator-swarm-endpoint.modal.run/v1/swarm/process"

payload = {
    "target_item_id": "diner_south_112",
    "prompt": "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service."
}

print("🚀 Querying Swarm Orchestrator for Preset 4...")
response = requests.post(URL, json=payload, timeout=600)
if response.status_code == 200:
    data = response.json()
    print("\n✅ Success!")
    
    # We want to print the raw beta output if possible. Wait, the orchestrator returns:
    # "beta_reasoning": {"raw_monologue": ..., "payload": ...}
    # But wait, does it return the full beta_raw_output? No!
    # Ah! In swarm_orchestrator.py, it returns:
    # "beta_reasoning": {
    #     "raw_monologue": (split thinking tag or "No thinking block.")
    #     "payload": final_state["beta_parsed_json"]
    # }
    # So we don't have the original, full raw_output! 
    # Wait, let's look at the return signature of service_beta.py:
    # return {"raw_output": raw_gen, "parsed_json": parsed}
    # And swarm_orchestrator.py does:
    # return {"beta_raw_output": res["raw_output"], "beta_parsed_json": res["parsed_json"]}
    # Let's print both beta_raw_output and beta_parsed_json from final_state!
    
    # Wait, does the orchestrator return status_code 200? Yes. Let's print the entire response JSON.
    print("\nOrchestrator full response:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
