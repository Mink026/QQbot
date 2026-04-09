import dotenv
import os

dotenv.load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
WS_PORT = int(os.getenv("WS_PORT"))
NAPCAT_WS_URL = f"{os.getenv("WS_URL").strip()}:{WS_PORT}"
