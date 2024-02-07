import telegram.ext
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')

updater = telegram.ext.Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    update.message.reply_text('Hello! I am a bot. How can I help you?')


dispatcher.add_handler(telegram.ext.CommandHandler('start', start))

updater.start_polling()
updater.idle()