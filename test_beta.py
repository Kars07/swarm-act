import requests
import json

# Replace with your actual Beta URL
URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"

# Simulated payload passing the user request and the data we just got from Alpha
payload = {
    "prompt": "The customer was looking for a high-performance GPU programming guide, specifically for CUDA and CuTe on Blackwell architecture. They prefer low-level optimizations over frameworks.",
    "alpha_insight": {
        "predicted_rating": 5,
        "predicted_review": "I have been working with Mike at this store since I moved to Nashville in January of 2017. He is very knowledgeable about all things related to GPUs, especially NVIDIA products. His knowledge base is impressive and he has helped me find exactly what I needed every time.\n\nMike also went above and beyond when my computer crashed during our last project together. We were able to get it back up running within minutes! \n\nIf you're looking for any type of technical support or guidance from an expert who will go out of his way to help you, look no further than Mike."
    }
}

print("🚀 Sending request to Agent Beta (this will take ~3 mins if the container is waking up from sleep)...")

response = requests.post(URL, json=payload)

if response.status_code == 200:
    print("\n✅ SUCCESS! Agent Beta Response:\n")
    data = response.json()
    
    print("--- Parsed JSON ---")
    print(json.dumps(data["parsed_json"], indent=4))
    
    print("\n--- Raw Output Stream (Including Monologue) ---")
    print(data["raw_output"])
else:
    print(f"❌ HTTP Error {response.status_code}: {response.text}")