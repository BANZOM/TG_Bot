import telegram.ext
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')

updater = telegram.ext.Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    update.message.reply_text('Hello! Thank you for reaching out. I am a bot programmed to assist you. How can I be of service to you today?')

def save_text(update, context):
    text = ' '.join(context.args)
    if not text or text.isspace() or text == '':
        update.message.reply_text('Please provide some text to save')
        return
    with open('saved_text.txt', 'a') as file:
        file.write(text + '\n')
    with open('saved_text.txt', 'r') as file:
        lines = file.readlines()
        lines.sort()
    with open('saved_text.txt', 'w') as file:
        file.writelines(lines)
    update.message.reply_text('Text saved successfully')

def show_notes(update, context):
    with open('saved_text.txt', 'r') as file:
        notes = file.readlines()
    if not notes:
        update.message.reply_text('No notes found')
    else:
        for note in notes:
            update.message.reply_text(note.strip())

dispatcher.add_handler(telegram.ext.CommandHandler('show', show_notes))
dispatcher.add_handler(telegram.ext.CommandHandler('save', save_text))
dispatcher.add_handler(telegram.ext.CommandHandler('start', start))

updater.start_polling()
updater.idle()