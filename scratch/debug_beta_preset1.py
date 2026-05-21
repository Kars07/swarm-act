import requests
import json

URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"

payload_preset1 = {
    "prompt": "The customer wants an authentic Japanese ramen bar experience, specifically looking for rich tonkotsu broth, house-made noodles, and spicy miso options. They appreciate attentive but quick service and don't mind a wait.",
    "alpha_insight": {
        "predicted_rating": 5,
        "predicted_review": "I've been to Japan twice in my life (once as a child) so I have some pretty high standards when it comes to ramen. This place is legit! It's not your typical Americanized ramen shop where you can get any flavor of soup base or toppings on tap. \n\nThe staff was super friendly and helpful. We ordered the Tonkatsu Ramen which had a really good balance between salty and sweet flavors from the pork belly. My friend got the Miso Ramen which he said was great too.\n\nThey also serve sushi here if that's what you're into. Overall this place has everything you need for a delicious meal."
    }
}

print("Sending request for Preset 1 to Beta service...")
response = requests.post(URL, json=payload_preset1)
if response.status_code == 200:
    res_data = response.json()
    print("--- SUCCESS ---")
    print("RAW OUTPUT:")
    print(res_data["raw_output"])
    print("\nPARSED JSON:")
    print(json.dumps(res_data["parsed_json"], indent=4))
else:
    print(f"ERROR {response.status_code}: {response.text}")
