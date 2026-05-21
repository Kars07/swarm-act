import requests
import json

ALPHA_SERVICE_URL = "https://wakamateservices--bct-alpha-service-alphaservice-generate.modal.run"
BETA_SERVICE_URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"

payload_alpha = {
    "target_item_id": "item_88492",
    "prompt": "The customer was looking for a high-performance GPU programming guide, specifically for CUDA and CuTe on Blackwell architecture. They prefer low-level optimizations over frameworks."
}

payload_beta = {
    "prompt": "The customer was looking for a high-performance GPU programming guide, specifically for CUDA and CuTe on Blackwell architecture. They prefer low-level optimizations over frameworks.",
    "alpha_insight": {
        "predicted_rating": 5,
        "predicted_review": "Excellent"
    }
}

print("Testing Alpha URL with requests...")
try:
    response = requests.post(ALPHA_SERVICE_URL, json=payload_alpha)
    print("Alpha Status Code:", response.status_code)
    print("Alpha Headers:", dict(response.headers))
    print("Alpha Output:", response.text[:200])
except Exception as e:
    print("Alpha failed with:", e)

print("\nTesting Beta URL with requests...")
try:
    response = requests.post(BETA_SERVICE_URL, json=payload_beta)
    print("Beta Status Code:", response.status_code)
    print("Beta Headers:", dict(response.headers))
    print("Beta Output:", response.text[:200])
except Exception as e:
    print("Beta failed with:", e)
