import os
import logging
import openai
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # GPT API Key

openai.api_key = OPENAI_API_KEY

# Logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Track user warnings
user_warnings = {}

# Moderation Settings
WARNING_LIMIT = 3

# Moderation: Detect links & warn users
async def moderate_chat(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    message_text = update.message.text

    if "http://" in message_text or "https://" in message_text or "t.me/" in message_text:
        user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
        await update.message.reply_text(f"⚠️ Warning {user_warnings[user_id]}/{WARNING_LIMIT}: No links allowed!")

        if user_warnings[user_id] >= WARNING_LIMIT:
            await context.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text(f"🚨 {update.message.from_user.first_name} was banned for repeated violations.")
            del user_warnings[user_id]
        else:
            await update.message.delete()

# AI Chat Function
async def ai_chat(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.message.chat_id

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are Hedie the Sloth, expert on Slothbar and Hedera."},
                  {"role": "user", "content": user_message}]
    )
    
    ai_reply = response["choices"][0]["message"]["content"]
    await context.bot.send_message(chat_id=chat_id, text=ai_reply)

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🦥 Hello! I'm Hedie the Sloth, your friendly Slothbar bot. I can chat and moderate!")

# Main Function
def main():
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    print("BOT_TOKEN:", repr(BOT_TOKEN))  # Debugging: Check if the token is loaded

    application = Application.builder().token(BOT_TOKEN).build()


    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))  # AI Chat
    application.add_handler(MessageHandler(filters.TEXT, moderate_chat))  # Moderation

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
