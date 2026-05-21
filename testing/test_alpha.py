import requests
import json

# Replace 'your-username' with your actual Modal workspace name
# You can find the exact URL in your Modal Web Dashboard under the 'bct-alpha-service' app
URL = "https://wakamateservices--bct-alpha-service-alphaservice-generate.modal.run"

payload = {
    "target_item_id": "item_88492",
    "prompt": "The customer was looking for a high-performance GPU programming guide, specifically for CUDA and CuTe on Blackwell architecture. They prefer low-level optimizations over frameworks."
}

print("🚀 Sending request to Agent Alpha (this will take ~3 mins if the container is waking up from sleep)...")

response = requests.post(URL, json=payload)

if response.status_code == 200:
    print("\n✅ SUCCESS! Agent Alpha Response:\n")
    data = response.json()
    print(json.dumps(data["parsed_json"], indent=4))
    
    print("\n--- Raw Output Stream ---")
    print(data["raw_output"])
else:
    print(f"❌ HTTP Error {response.status_code}: {response.text}")