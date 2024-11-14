import os
import openai
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка переменных окружения

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")


class AzureOpenAI:
    def __init__(self, api_version, azure_endpoint, api_key):
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key

    def chat(self, model, messages):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        url = f"{self.azure_endpoint}"
        payload = {
            "model": model,
            "messages": messages,
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

def openai_client(disable_azure=False):
    azure_openai_endpoint = AZURE_OPENAI_ENDPOINT
    azure_openai_api_key = AZURE_OPENAI_KEY

    if azure_openai_endpoint is not None and not disable_azure:
        instance = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=azure_openai_endpoint,
            api_key=azure_openai_api_key,
        )
        return instance

    # Обычный клиент OpenAI, если Azure отключен
    return openai
