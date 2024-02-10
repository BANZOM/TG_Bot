from MyTelegramBot import MyTelegramBot
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    bot = MyTelegramBot(os.getenv("TOKEN"), os.getenv("AUTHORISED_USERS"))
    bot.run()