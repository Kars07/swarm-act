import requests
import json
import sys

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

def run_test(target_id, prompt):
    payload = {
        "target_item_id": target_id,
        "prompt": prompt
    }
    
    print("\n🚀 Sending request to the unified Swarm Orchestrator...")
    print(f"🎯 Target Item ID: {target_id}")
    print(f"📝 Prompt: {prompt}\n")
    print("Sequential execution is running. Please wait...")
    
    try:
        response = requests.post(URL, json=payload, timeout=600)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Swarm Orchestrator Response:\n")
            data = response.json()
            
            print("=== Agent Alpha Extraction (SFT + GRPO Review/Rating Insight) ===")
            print(json.dumps(data.get("alpha_extraction", {}), indent=4))
            
            print("\n=== Agent Beta Reasoning (Monologue + Ranked Items) ===")
            beta_res = data.get("beta_reasoning", {})
            print("💡 Raw Monologue:")
            print(beta_res.get("raw_monologue", "No thinking block."))
            
            print("\n📦 Payload (Beta Ranked Items):")
            print(json.dumps(beta_res.get("payload", {}), indent=4))
            
        else:
            print(f"\n❌ HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Swarm Orchestrator Multi-Domain Test Presets")
    parser.add_argument("--preset", type=str, help="Select a preset option (1-5)")
    args = parser.parse_args()
    
    if args.preset:
        choice = args.preset.strip().lower()
        if choice in PRESETS:
            preset = PRESETS[choice]
            run_test(preset["target_item_id"], preset["prompt"])
            return
        else:
            print(f"Invalid preset choice '{choice}'. Please select from 1-5.")
            return

    print("====================================================")
    print("🌟 Swarm Orchestrator Multi-Domain Test Presets 🌟")
    print("====================================================")
    print("Choose one of the following preset domains to test the swarm:")
    
    for key, preset in PRESETS.items():
        print(f"  [{key}] {preset['name']}")
    print("  [6] ✍️ Enter a Custom Prompt")
    print("  [Q] Exit")
    
    choice = input("\nSelect an option: ").strip().lower()
    
    if choice == 'q':
        sys.exit(0)
    elif choice in PRESETS:
        preset = PRESETS[choice]
        run_test(preset["target_item_id"], preset["prompt"])
    elif choice == '6':
        custom_prompt = input("\nEnter your custom prompt: ").strip()
        custom_id = input("Enter a target item ID (e.g. item_1234): ").strip()
        if not custom_id:
            custom_id = "custom_item_abc"
        if custom_prompt:
            run_test(custom_id, custom_prompt)
        else:
            print("Error: Prompt cannot be empty.")
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()
