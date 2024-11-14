import os
import logging
import requests
from typing import Dict
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GPT4V_KEY = os.getenv("GPT4V_KEY")
GPT4V_ENDPOINT = os.getenv("GPT4V_ENDPOINT")

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["Start Adventure"],
    ["Done"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Welcome to the Lucky Capybara adventure game! Type any action to start.",
        reply_markup=markup,
    )
    return CHOOSING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send /start to start the adventure. Type anything else to play.")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text
    try:
        scene_description, actions = await get_scene_description_and_actions(user_message)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, an error occurred while processing your request. Please try again.")
        return CHOOSING

    # Форматирование ответа
    formatted_message = format_response(scene_description, actions)

    # Отправка сообщения пользователю
    await update.message.reply_text(formatted_message, parse_mode='Markdown')

    return CHOOSING

async def get_scene_description_and_actions(user_input):
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT4V_KEY,
    }

    payload = {
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": user_input  # Замена содержимого на ввод пользователя
            }
          ]
        }
      ],
      "temperature": 0.7,
      "top_p": 0.95,
      "max_tokens": 800
    }

    # Отправка запроса к Azure OpenAI
    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    response_data = response.json()

    # Отладочная печать для проверки структуры ответа
    print("Ответ от API:", response_data)

    # Извлечение текста из ответа
    scene_description = response_data['choices'][0]['message']['content']

    actions_marker = "**Options:**"
    if actions_marker in scene_description:
        actions_start_idx = scene_description.index(actions_marker) + len(actions_marker)
        actions_text = scene_description[actions_start_idx:].strip()
    else:
        actions_text = "No actions found."

    return scene_description, actions_text

def format_response(scene_description, actions):
    actions = actions.replace("**Options:**", "**Possible Actions:**")
    formatted_message = (
        f"**Scene Description:**\n"
        f"{scene_description}\n\n"
        f"{actions}"
    )
    return formatted_message

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    await update.message.reply_text("Goodbye!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Start Adventure)$"), process_message
                ),
                CommandHandler("help", help_command),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), done)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))  # Обработчик команды /help

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()