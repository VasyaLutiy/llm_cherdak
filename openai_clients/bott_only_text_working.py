import os
import logging
import requests
from typing import Dict
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GPT4V_KEY = os.getenv("GPT4V_KEY")
GPT4V_ENDPOINT = os.getenv("GPT4V_ENDPOINT")
IMAGE_GEN_ENDPOINT = "https://dev.wisebuddy.ai/sdPoombCapibara/generate"
WAITING_GIF_PATH = "/home/kosmoletc/openai_sd_prompt/waiting.jpg"  # Укажи путь к анимации ожидания

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["1", "2", "3", "4", "5"],  # Обновлено для отображения действий
    ["Done"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Welcome to the adventure game! Starting the adventure...",
        reply_markup=markup,
    )
    
    initial_message = "Start Adventure"

    try:
        new_scene_description, new_actions = await get_scene_description_and_actions(initial_message)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, an error occurred while starting the adventure. Please try again.")
        return CHOOSING

    # Сохранение нового состояния сцены и действий
    context.user_data["scene_description"] = new_scene_description
    context.user_data["actions"] = new_actions

    # Генерация и отправка изображения
    await send_image_from_scene(new_scene_description, update, context)

    # Форматирование ответа
    formatted_message = format_response(new_scene_description, new_actions)

    # Отправка сообщения пользователю
    await update.message.reply_text(formatted_message, reply_markup=markup, parse_mode='Markdown')

    return CHOOSING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send /start to start the adventure. Type anything else to play.")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text

    # Проверка была ли нажата кнопка Done
    if user_message.lower().strip() == "done":
        await done(update, context)  # Завершение диалога и отмена дальнейших действий
        return ConversationHandler.END

    # Отправка анимации ожидания
    #waiting_message = await update.message.reply_animation(open(WAITING_GIF_PATH, 'rb'))

    # Проверить, выбрано ли действие
    if user_message.isdigit() and 1 <= int(user_message) <= 5:
        scene_description = context.user_data.get("scene_description", "")
        actions = context.user_data.get("actions", "")
        chosen_action = get_chosen_action_text(actions, int(user_message))
        
        # Формирование нового запроса к модели с выбором действия
        user_message = f"{scene_description}\n\nYou chose action {int(user_message)}: {chosen_action}"

    try:
        new_scene_description, new_actions = await get_scene_description_and_actions(user_message)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, an error occurred while processing your request. Please try again.")
        return CHOOSING

    # Сохранение нового состояния сцены и действий
    context.user_data["scene_description"] = new_scene_description
    context.user_data["actions"] = new_actions

    # Удаление анимации ожидания
    #await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=waiting_message.message_id)

    # Генерация и отправка изображения
    await send_image_from_scene(new_scene_description, update, context)
    
    # Форматирование ответа
    formatted_message = format_response(new_scene_description, new_actions)

    # Отправка сообщения пользователю
    await update.message.reply_text(formatted_message, reply_markup=markup, parse_mode='Markdown')

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
      "temperature": 1.5,
      "top_p": 0.95,
      "max_tokens": 8000
    }

    # Отправка запроса к Azure OpenAI
    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    response_data = response.json()

    # Отладочная печать для проверки структуры ответа
    logger.debug("Ответ от API: %s", response_data)

    # Извлечение текста из ответа
    scene_description = response_data['choices'][0]['message']['content']

    # Разделить описание сцены и возможные действия
    scene_desc, actions_text = split_description_and_actions(scene_description)

    return scene_desc, actions_text

async def send_image_from_scene(scene_description, update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Запрос к endpoint для генерации изображения
        response = requests.post(IMAGE_GEN_ENDPOINT, data={'prompt': scene_description, 'seed': '5466973843955452462'})
        response.raise_for_status()
        image_data = response.content

        # Отправка изображения пользователю
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_data)
    except Exception as e:
        logger.error(f"Failed to generate or send image. Error: {e}")
        await update.message.reply_text("Sorry, an error occurred while generating the image.")

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

def get_chosen_action_text(actions, choice_number):
    """Извлекает текст действия по номеру выбора."""
    lines = actions.split('\n')
    choice_text = ""
    for line in lines:
        if line.strip().startswith(f"{choice_number}."):
            choice_text = line.strip()
            break
    return choice_text

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    await update.message.reply_text("Goodbye!", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
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
                    filters.TEXT & ~filters.COMMAND, process_message
                ),
                CommandHandler("help", help_command),
                MessageHandler(filters.Regex("^(Done)$"), done)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), done)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))  # Обработчик команды /help
    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()