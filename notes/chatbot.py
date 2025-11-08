import os
from langchain_groq import ChatGroq

import requests
import json

# Replace with your actual OpenRouter API key
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Define the chatbot function
def ask_groq(prompt: str, model: str = "openai/gpt-oss-20b:free") -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error {response.status_code}: {response.text}"
