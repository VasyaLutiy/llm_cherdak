import os
import logging
import requests
from dotenv import load_dotenv


prompt = "Start Adventure"
model = "Olaf12345"
stream = False
url = "https://4c62-13-234-32-80.ngrok-free.app/api/generate"


def send_prompt(prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while sending the prompt: {e}")
        return None

response = send_prompt(prompt)

# Проверяем наличие ключа 'response' в ответе
scene = response.get('response', '')
if not scene:
    print("No scene received. Game over?")

#print(scene)

def split_description_and_actions(text):
    actions_marker = "**Possible Actions:**"
    if actions_marker in text:
        parts = text.split(actions_marker)
        scene_desc = parts[0].strip()
        actions_text = f"{actions_marker}\n{parts[1].strip()}"
    else:
        scene_desc = text
        actions_text = "No actions found."

    return scene_desc, actions_text

def format_response(scene_description, actions):
    formatted_message = (
        f"**Scene Description:**\n"
        f"{scene_description}\n\n"
        f"{actions}"
    )
    return formatted_message

scene_desc, actions_text = split_description_and_actions(scene)
fm = format_response(scene_desc, actions_text)
print(fm)