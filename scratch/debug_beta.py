import requests
import json

ALPHA_URL = "https://wakamateservices--bct-alpha-service-alphaservice-generate.modal.run"
BETA_URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"

PRESETS = {
    "1": {
        "name": "🍜 Gourmet Ramen (Japanese Food)",
        "target_item_id": "ramen_shop_992",
        "prompt": "The customer wants an authentic Japanese ramen bar experience, specifically looking for rich tonkotsu broth, house-made noodles, and spicy miso options. They appreciate attentive but quick service and don't mind a wait."
    },
    "4": {
        "name": "Late-Night Southern Diner (Comfort Food)",
        "target_item_id": "diner_south_112",
        "prompt": "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service."
    },
    "5": {
        "name": "💅 Relaxing Nail Salon & Spa (Service)",
        "target_item_id": "spa_nails_421",
        "prompt": "The customer is looking for a hygienic nail salon for a relaxing pedicure. They are highly critical of cleanliness, quick/rushed service, and want precise, detailed care with complimentary drinks."
    }
}

def debug_preset(key):
    preset = PRESETS[key]
    print(f"\n====================================================")
    print(f"🕵️ DEBUGGING PRESET {key}: {preset['name']}")
    print(f"====================================================")
    
    # 1. Query Alpha
    print("🛰️ Querying Alpha Service...")
    alpha_payload = {
        "target_item_id": preset["target_item_id"],
        "prompt": preset["prompt"]
    }
    alpha_res = requests.post(ALPHA_URL, json=alpha_payload)
    if alpha_res.status_code != 200:
        print(f"❌ Alpha failed: {alpha_res.status_code} - {alpha_res.text}")
        return
        
    alpha_data = alpha_res.json()
    print("\nAlpha Parsed Output:")
    print(json.dumps(alpha_data.get("parsed_json"), indent=2))
    
    # 2. Query Beta
    print("\n🛰️ Querying Beta Service...")
    beta_payload = {
        "prompt": preset["prompt"],
        "alpha_insight": alpha_data.get("parsed_json")
    }
    beta_res = requests.post(BETA_URL, json=beta_payload)
    if beta_res.status_code != 200:
        print(f"❌ Beta failed: {beta_res.status_code} - {beta_res.text}")
        return
        
    beta_data = beta_res.json()
    print("\nBeta Service Returned Signature Keys:", list(beta_data.keys()))
    print("\nBeta parsed_json:")
    print(json.dumps(beta_data.get("parsed_json"), indent=2))
    print("\nBeta raw_output:")
    print("-" * 60)
    print(beta_data.get("raw_output"))
    print("-" * 60)

if __name__ == "__main__":
    import sys
    preset_to_run = sys.argv[1] if len(sys.argv) > 1 else "4"
    debug_preset(preset_to_run)
