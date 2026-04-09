import dotenv
import os
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NAPCAT_WS_URL = os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:22222")