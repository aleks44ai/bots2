
import os
import openai
import requests
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from PIL import Image
import io
import pytesseract

# Ініціалізація токену Telegram і OpenAI
TELEGRAM_TOKEN = "7356035299:AAHCkcPnMK7MvHoQxlhKAR7VDjVB-u7EjWs"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# Налаштування Telegram бота
bot = Bot(token=TELEGRAM_TOKEN)
current_role = "помічник"
roles = {
    "художник": "Ти - професійний художник. Твоє завдання - створювати ідеї для візуальних проектів та допомагати у створенні зображень.",
    "учитель": "Ти - вчитель інформатики та математики. Твоє завдання - пояснювати складні концепції та допомагати у вирішенні задач.",
    "подружка 15 років": "Ти - 15-річна подружка. Спілкуйся невимушено та підтримуй співрозмовника в дружній манері."
}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Художник", callback_data='художник'),
         InlineKeyboardButton("Учитель", callback_data='учитель')],
        [InlineKeyboardButton("Подружка 15 років", callback_data='подружка 15 років')],
        [InlineKeyboardButton("Start (Play)", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Привіт! Я твій Telegram бот на базі ChatGPT-4. Виберіть роль, яку хочете активувати або почніть роботу:", reply_markup=reply_markup)

def role_selection(update: Update, context: CallbackContext):
    global current_role
    query = update.callback_query
    query.answer()
    selected_role = query.data
    if selected_role == 'start':
        query.edit_message_text(text="Роботу розпочато! Оберіть іншу роль за потреби.")
        return
    if selected_role in roles:
        current_role = selected_role
        query.edit_message_text(text=f"Роль змінена на: {selected_role}")
    else:
        query.edit_message_text(text="Невідома роль. Спробуйте ще раз.")

def handle_text(update: Update, context: CallbackContext):
    user_message = update.message.text
    try:
        # Перевірка на запит створення зображення
        if any(keyword in user_message.lower() for keyword in ["дай картинку", "створи зображення", "сгенеруй картинку", "generate image"]):
            handle_generate_image(update, context)
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": roles.get(current_role, "Ти - помічник, який допомагає користувачам відповідати на питання з зображень та анкет. Відповідай максимально точно та детально на основі отриманих даних.")},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_response = response['choices'][0]['message']['content']
            update.message.reply_text(f"Роль: {current_role}\n{bot_response}")
    except openai.error.OpenAIError as e:
        update.message.reply_text("Вибачте, сталася помилка під час обробки вашого запиту. Спробуйте пізніше.")
        print(f"OpenAI API Error: {e}")

def handle_image(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    image_byte_array = io.BytesIO()
    photo_file.download(out=image_byte_array)
    image_byte_array.seek(0)

    try:
        # Розпізнавання тексту на зображенні за допомогою Tesseract
        image = Image.open(image_byte_array)
        recognized_text = pytesseract.image_to_string(image, lang='eng+rus')
        if recognized_text.strip():
            # Використовуємо розпізнаний текст для запиту до ChatGPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": roles.get(current_role, "Ти - помічник, який допомагає користувачам відповідати на питання з зображень та анкет. Відповідай максимально точно та детально на основі отриманих даних.")},
                    {"role": "user", "content": recognized_text}
                ]
            )
            bot_response = response['choices'][0]['message']['content']
            update.message.reply_text(f"Розпізнаний текст: {recognized_text}\n\nВідповідь GPT-4: {bot_response}")
        else:
            update.message.reply_text("Вибачте, не вдалося розпізнати текст на зображенні. Спробуйте інше зображення.")
    except Exception as e:
        update.message.reply_text("Вибачте, сталася помилка під час аналізу зображення. Спробуйте пізніше.")
        print(f"Image Analysis Error: {e}")

def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    if document.mime_type.startswith("image/"):
        image_byte_array = io.BytesIO()
        document.get_file().download(out=image_byte_array)
        image_byte_array.seek(0)

        try:
            # Розпізнавання тексту на зображенні за допомогою Tesseract
            image = Image.open(image_byte_array)
            recognized_text = pytesseract.image_to_string(image, lang='eng+rus')
            if recognized_text.strip():
                # Використовуємо розпізнаний текст для запиту до ChatGPT-4
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": roles.get(current_role, "Ти - помічник, який допомагає користувачам відповідати на питання з зображень та анкет. Відповідай максимально точно та детально на основі отриманих даних.")},
                        {"role": "user", "content": recognized_text}
                    ]
                )
                bot_response = response['choices'][0]['message']['content']
                update.message.reply_text(f"Розпізнаний текст: {recognized_text}\n\nВідповідь GPT-4: {bot_response}")
            else:
                update.message.reply_text("Вибачте, не вдалося розпізнати текст на зображенні. Спробуйте інше зображення.")
        except Exception as e:
            update.message.reply_text("Вибачте, сталася помилка під час аналізу зображення. Спробуйте пізніше.")
            print(f"Image Analysis Error: {e}")
    else:
        update.message.reply_text("Вибачте, я можу обробляти лише файли зображень. Спробуйте надіслати файл у форматі зображення.")

def handle_generate_image(update: Update, context: CallbackContext):
    user_message = update.message.text.replace('/generate_image', '').strip()
    if not user_message:
        update.message.reply_text("Будь ласка, надайте опис для створення зображення після команди /generate_image.")
        return

    try:
        # Встановлюємо промт для професійного художника
        prompt = roles.get("художник", "Ти - професійний художник. Твоє завдання - створювати ідеї для візуальних проектів та допомагати у створенні зображень.")
        response = openai.Image.create(
            prompt=f"{prompt}. {user_message}",
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        update.message.reply_text(f"Ось ваше зображення за запитом: {user_message}")
        update.message.reply_photo(photo=image_url)
    except openai.error.OpenAIError as e:
        update.message.reply_text("Вибачте, сталася помилка під час створення зображення. Спробуйте пізніше.")
        print(f"OpenAI API Error: {e}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(role_selection))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    dp.add_handler(MessageHandler(Filters.document.category("image"), handle_document))
    dp.add_handler(CommandHandler("generate_image", handle_generate_image))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
