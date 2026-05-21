import requests
import json

URL = "https://wakamateservices--bct-beta-service-betaservice-generate.modal.run"

# Payload for Preset 4
payload_preset4 = {
    "prompt": "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service.",
    "alpha_insight": {
        "predicted_rating": 5,
        "predicted_review": "I've been here several times now and I'm always impressed by how good it is! It's not fancy but you can tell that they take pride in their food and make sure to serve up some of the best southern comfort food around. \n\nThe staff is very friendly and attentive and will go out of their way to accommodate your needs. My favorite thing on the menu so far has been the Chicken Salad Sandwich which comes with two pieces of breaded chicken breast topped with lettuce, tomato, onion, mayo, and sour cream. You get a side too - my personal favorites have been the mashed potatoes (which come with gravy) and the green beans."
    }
}

print("Sending request for Preset 4 to Beta service...")
response = requests.post(URL, json=payload_preset4)
if response.status_code == 200:
    res_data = response.json()
    print("--- SUCCESS ---")
    print("RAW OUTPUT:")
    print(res_data["raw_output"])
    print("\nPARSED JSON:")
    print(json.dumps(res_data["parsed_json"], indent=4))
else:
    print(f"ERROR {response.status_code}: {response.text}")
