import requests
import json

# Replace with your actual OpenRouter API key
api_key = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxx"

# Chat message payload
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": "Hello! What's the meaning of life?"}
    ]
}

# Headers for the request
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Send POST request to OpenRouter
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    data=json.dumps(payload)
)

# Parse and print the chatbot response
if response.status_code == 200:
    reply = response.json()["choices"][0]["message"]["content"]
    print("Bot reply:", reply)
else:
    print("Error:", response.status_code, response.text)
