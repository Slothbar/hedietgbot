import os
import logging
import openai
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("7942098238:AAGSq81r9BOFOn-_RQMXl9Jkbozza6IkNLk")  # Telegram Bot Token
OPENAI_API_KEY = os.getenv("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")  # GPT API Key

openai.api_key = OPENAI_API_KEY

# Logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Track user warnings
user_warnings = {}

# Moderation Settings
WARNING_LIMIT = 3

# Moderation: Detect links & warn users
def moderate_chat(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    message_text = update.message.text

    if "http://" in message_text or "https://" in message_text or "t.me/" in message_text:
        user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
        update.message.reply_text(f"⚠️ Warning {user_warnings[user_id]}/{WARNING_LIMIT}: No links allowed!")

        if user_warnings[user_id] >= WARNING_LIMIT:
            context.bot.ban_chat_member(chat_id, user_id)
            update.message.reply_text(f"🚨 {update.message.from_user.first_name} was banned for repeated violations.")
            del user_warnings[user_id]
        else:
            update.message.delete()

# AI Chat Function
def ai_chat(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.message.chat_id

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are Hedie the Sloth, expert on Slothbar and Hedera."},
                  {"role": "user", "content": user_message}]
    )
    
    ai_reply = response["choices"][0]["message"]["content"]
    context.bot.send_message(chat_id=chat_id, text=ai_reply)

# Start Command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🦥 Hello! I'm Hedie the Sloth, your friendly Slothbar bot. I can chat and moderate!")

# Main Function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_chat))  # AI Chat
    dp.add_handler(MessageHandler(Filters.text, moderate_chat))  # Moderation

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
