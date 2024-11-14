import requests
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:
    def __init__(self, api_key, api_version, endpoint):
        self.api_key = api_key
        self.api_version = api_version
        self.endpoint = endpoint

    def chat(self, model, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": model,
            "prompt": messages,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

def ollama_client():
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
    ollama_api_key = os.getenv("OLLAMA_API_KEY")
    ollama_api_version = os.getenv("OLLAMA_API_VERSION", "1")

    return OllamaClient(
        api_key=ollama_api_key,
        api_version=ollama_api_version,
        endpoint=ollama_endpoint,
    )