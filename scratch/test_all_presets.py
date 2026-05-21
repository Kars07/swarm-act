import requests
import json
import time

URL = "https://wakamateservices--bct-swarm-orchestrator-swarm-endpoint.modal.run/v1/swarm/process"

PRESETS = {
    "1": {
        "name": "🍜 Gourmet Ramen (Japanese Food)",
        "target_item_id": "ramen_shop_992",
        "prompt": "The customer wants an authentic Japanese ramen bar experience, specifically looking for rich tonkotsu broth, house-made noodles, and spicy miso options. They appreciate attentive but quick service and don't mind a wait."
    },
    "2": {
        "name": "☕ Cozy Coffeehouse & Bakery (Café)",
        "target_item_id": "cafe_cafe_883",
        "prompt": "The customer is looking for a quiet, homey local café to study or work. They prefer house-roasted pour-over coffee, fresh-baked pastries like almond croissants, and strong, reliable Wi-Fi with a cozy 90s Seattle vibe."
    },
    "3": {
        "name": "🥩 Fine Dining Steakhouse (Luxury Food)",
        "target_item_id": "steakhouse_998",
        "prompt": "The customer is celebrating an anniversary and looking for an upscale fine dining experience. They want perfectly cooked steaks (filet mignon), excellent craft cocktails (like a Manhattan), and high-end professional table service."
    },
    "4": {
        "name": "🍗 Late-Night Southern Diner (Comfort Food)",
        "target_item_id": "diner_south_112",
        "prompt": "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service."
    },
    "5": {
        "name": "💅 Relaxing Nail Salon & Spa (Service)",
        "target_item_id": "spa_nails_421",
        "prompt": "The customer is looking for a hygienic nail salon for a relaxing pedicure. They are highly critical of cleanliness, quick/rushed service, and want precise, detailed care with complimentary drinks."
    }
}

def main():
    print("====================================================")
    print("🚀 Running Diagnostics on ALL 5 Swarm Presets 🚀")
    print("====================================================\n")
    
    all_success = True
    
    for key, preset in PRESETS.items():
        print(f"Domain: {preset['name']}")
        print(f"  Target: {preset['target_item_id']}")
        print(f"  Prompt: {preset['prompt']}")
        
        start_time = time.time()
        payload = {
            "target_item_id": preset["target_item_id"],
            "prompt": preset["prompt"]
        }
        
        try:
            response = requests.post(URL, json=payload, timeout=600)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Done in {elapsed:.2f}s!")
                
                # Check Alpha output
                alpha_ext = data.get("alpha_extraction", {})
                print(f"  - Agent Alpha predicted rating: {alpha_ext.get('predicted_rating')}")
                
                # Check Beta output
                beta_res = data.get("beta_reasoning", {})
                beta_payload = beta_res.get("payload", {})
                ranked_items = beta_payload.get("ranked_items", [])
                
                print(f"  - Agent Beta monologue length: {len(beta_res.get('raw_monologue', ''))} chars")
                print(f"  - Agent Beta ranked items count: {len(ranked_items)}")
                print(f"  - Agent Beta ranked items list: {ranked_items}")
                
                # Validation check
                if not ranked_items:
                    print("  ❌ ERROR: Empty ranked_items list!")
                    all_success = False
                else:
                    polluted = [item for item in ranked_items if " " in item or len(item) > 30]
                    if polluted:
                        print(f"  ❌ ERROR: Polluted items found in ranked list: {polluted}")
                        all_success = False
                    else:
                        print("  ❇️ Valid payload with zero monologue pollution.")
                        
            else:
                print(f"  ❌ ERROR: HTTP {response.status_code} - {response.text}")
                all_success = False
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            all_success = False
        print("-" * 52 + "\n")
        
    if all_success:
        print("🎉 ALL PRESETS VERIFIED SUCCESSFULLY WITH ZERO MONOLOGUE POLLUTION!")
    else:
        print("⚠️ SOME PRESETS FAILED VALIDATION. PLEASE CHECK LOGS ABOVE.")

if __name__ == "__main__":
    main()
