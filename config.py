import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("TG_KEY")
if not BOT_TOKEN:
    raise ValueError("TG_KEY not found in .env file")
