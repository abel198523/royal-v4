import os
import threading
from app import app
from routes import *
from bot import bot, BOT_TOKEN

def run_bot():
    if BOT_TOKEN:
        print("Starting Telegram Bot...")
        bot.infinity_polling()

if __name__ == "__main__":
    # Start Telegram Bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
