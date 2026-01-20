import os
import telebot
from flask import request, jsonify

# Get token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Initialize bot to None by default
bot = None

if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        welcome_text = (
            "🎮 እንኳን ወደ ROYAL BINGO በደህና መጡ!\n\n"
            "በዌብሳይታችን ላይ ለመመዝገብ የእርስዎን Chat ID ማወቅ ይኖርብዎታል።\n"
            f"የእርስዎ Chat ID: `{message.chat.id}`\n\n"
            "ይህንን ቁጥር በመያዝ ወደ ዌብሳይቱ ተመልሰው ምዝገባዎን ያጠናቅቁ።"
        )
        bot.reply_to(message, welcome_text, parse_mode='Markdown')

    @bot.message_handler(commands=['id'])
    def send_id(message):
        bot.reply_to(message, f"የእርስዎ Chat ID: `{message.chat.id}`", parse_mode='Markdown')
else:
    print("TELEGRAM_BOT_TOKEN not found. Bot functionality disabled.")
