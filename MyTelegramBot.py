from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3
import logging
from logging.handlers import RotatingFileHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# find handler for log messages
file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class MyTelegramBot:
    def __init__(self, token, authorised_users) -> None:
        self.__token = token
        self.__authorised_users = authorised_users

        self.__updater = Updater(self.__token, use_context=True)
        self.__dp = self.__updater.dispatcher

        # Connect to SQLite database
        self.__conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        self.__cursor = self.__conn.cursor()

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                            note_name TEXT PRIMARY KEY,
                            note_text TEXT
                            )''')
        self.__conn.commit()

        # Command Handlers
        self.__dp.add_handler(CommandHandler("start", self.start))
        self.__dp.add_handler(CommandHandler("help", self.help))
        self.__dp.add_handler(CommandHandler("save", self.save_note))
        self.__dp.add_handler(CommandHandler("update", self.update_note))
        self.__dp.add_handler(CommandHandler("delete", self.delete_note))
        self.__dp.add_handler(CommandHandler("notes", self.list_notes))
        self.__dp.add_handler(MessageHandler(Filters.regex(r'#\w+'), self.retrieve_note))



    def start(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        logger.info('User %s started the bot.', update.message.from_user.first_name)
        update.message.reply_text('Hello! This is your bot. Made with 🩷 by @AdityaPanwars')        

    def is_authorised_user(self, update, context):
        if update.message.from_user.username not in self.__authorised_users:
            logger.info('User %s is not authorized to use the bot.', update.message.from_user.first_name)
            update.message.reply_text('You are not authorized to use this bot. Contact the bot owner to get access.')
            return False
        return True

    def help(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        update.message.reply_text('The following commands are available:\n\n'
                                '/start - Start the bot\n'
                                '/notes - List all saved notes\n'
                                '/notes <prefix> - List notes starting with the prefix\n'
                                '/save <note_name> - Save a note\n'
                                '#<note_name> - Retrieve a note\n'
                                '/delete <note_name> - Delete a note\n'
                                '/update <note_name> - Update a note\n'
                                '/help - Show this help message')

        logger.info('User %s is asking for help.', update.message.from_user.first_name)

    def save_note(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        # Check if the reply is a text message
        if update.message.reply_to_message and update.message.reply_to_message.text:
            # Get the text of the replied message
            note_text = update.message.reply_to_message.text

            # Get the note name from the command
            command_parts = update.message.text.split()
            if len(command_parts) >= 2:
                note_name = command_parts[1]
                self.__cursor.execute('INSERT OR REPLACE INTO notes (note_name, note_text) VALUES (?, ?)', (note_name, note_text))
                self.__conn.commit()
                update.message.reply_text(f'Note "{note_name}" saved successfully.')
            else:
                update.message.reply_text('Please provide a note name.')
        else:
            update.message.reply_text('Please reply to a text message to save a note.')
        logger.info('User %s is saving a note.', update.message.from_user.first_name)

    def update_note(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        # Check if the reply is a text message
        if update.message.reply_to_message and update.message.reply_to_message.text:
            note_text = update.message.reply_to_message.text

            # Get the note name from the command
            command_parts = update.message.text.split()
            if len(command_parts) >= 2:
                note_name = command_parts[1]

                # Check if the note exists
                self.__cursor.execute('SELECT * FROM notes WHERE note_name = ?', (note_name,))
                result = self.__cursor.fetchone()

                if result:
                    self.__cursor.execute('UPDATE notes SET note_text = ? WHERE note_name = ?', (note_text, note_name))
                    self.__conn.commit()
                    update.message.reply_text(f'Note "{note_name}" updated successfully.')
                else:
                    update.message.reply_text(f'Note "{note_name}" does not exist.')
            else:
                update.message.reply_text('Please provide a note name.')
        else:
            update.message.reply_text('Please reply to a text message to update a note.')

        logger.info('User %s is updating a note.', update.message.from_user.first_name)

    def delete_note(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        # if the user passes empty arguments
        if len(context.args) == 0:
            update.message.reply_text('Please provide a note name.')
            return

        # Get the note name from the command
        note_name = update.message.text.split(' ')[1]

        self.__cursor.execute('SELECT * FROM notes WHERE note_name = ?', (note_name,))
        result = self.__cursor.fetchone()

        if result:
            self.__cursor.execute('DELETE FROM notes WHERE note_name = ?', (note_name,))
            self.__conn.commit()
            update.message.reply_text(f'Note "{note_name}" deleted successfully.')
            logger.info('User %s is deleting a note.', update.message.from_user.first_name)
        else:
            update.message.reply_text(f'Note "{note_name}" does not exist.')

    def list_notes(self, update, context):
        if not self.is_authorised_user(update=update, context=context):
            return
        # check if the user passes the prefix
        if len(context.args) > 0:
            prefix = context.args[0]
            self.__cursor.execute('SELECT note_name FROM notes WHERE note_name LIKE ? ORDER BY note_name ASC', (prefix + '%',))
        else:
            self.__cursor.execute('SELECT note_name FROM notes ORDER BY note_name ASC')
        
        result = self.__cursor.fetchall()

        if result:
            notes_list = "\n".join([f"#{note[0]}" for note in result])
            update.message.reply_text(f"List of saved notes:\n{notes_list}")
        else:
            update.message.reply_text("No notes saved yet.")

        logger.info('User %s is listing the notes.', update.message.from_user.first_name)

    def retrieve_note(self, update, context):
        # Get the note name from the command
        note_name = update.message.text.split('#')[1].strip()
        self.__cursor.execute('SELECT note_text FROM notes WHERE note_name = ?', (note_name,))
        result = self.__cursor.fetchone()

        if result:
            note_text = result[0]
            update.message.reply_text(f'Note "{note_name}":\n***********\n\n{note_text}')
        else:
            update.message.reply_text(f'Note "{note_name}" not found.')
        logger.info('User %s is retrieving a note.', update.message.from_user.first_name)

    def run(self):
        self.__updater.start_polling()
        self.__updater.idle()
