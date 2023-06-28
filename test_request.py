import requests
import json

url = "url_to_endpoint_center_with_port"

auth_token = "your_auth_token"

# Example messages
messages = [
    {"role": "user", "content": "What is the capital of Texas?"}
]

headers = {"Content-Type": "application/json"}


def send_request():
    response = requests.post(
        url, 
        data=json.dumps({"messages": messages, "verify_token":auth_token}), 
        headers={"Content-Type": "application/json"}
    )
    print("Response:", response.json()["response"])

send_request()
