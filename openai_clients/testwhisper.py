import os
import logging
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка переменных окружения
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY") or "your_api_key_here"
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or "your_endpoint_here"
TTS_MODEL = "hh234_tts"
VOICE = "alloy"
API_VERSION = "2024-02-15-preview"
SPEECH_FILE_PATH = "output.wav"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_audio_from_text(input_text):
    try:
        # Формирование URL и заголовков запроса
        final_url_tts = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{TTS_MODEL}/audio/speech?api-version={API_VERSION}"
        
        headers = {
            "api-key": AZURE_OPENAI_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "model": TTS_MODEL,
            "voice": VOICE,
            "input": input_text,
        }

        # Отправка запроса к API Azure OpenAI
        response = requests.post(final_url_tts, headers=headers, json=data)

        # Убедимся, что запрос был успешным
        response.raise_for_status()

        # Получение аудиоконтента
        audio_content = response.content

        # Сохранение аудиоконтента во временный файл
        with open(SPEECH_FILE_PATH, "wb") as f:
            f.write(audio_content)

        logger.info(f"Audio saved to {SPEECH_FILE_PATH}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {str(e)}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise e

def main():
    input_text = "the quick brown chicken jumped over the lazy dogs"
    
    logger.info("== Text to Speech Sample ==")
    get_audio_from_text(input_text)
    logger.info("Finished processing")

if __name__ == "__main__":
    main()