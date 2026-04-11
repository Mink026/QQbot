import dotenv
import os

dotenv.load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
WS_PORT = int(os.getenv("WS_PORT"))
NAPCAT_WS_URL = f"{os.getenv("WS_URL").strip()}:{WS_PORT}"

# Tavily web search API
TAVILY_KEY = os.getenv("TAVILY_KEY")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
AI_KEY = os.getenv("AI_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")

# NapCat send_group_ai_record voice character id (override via AI_VOICE_CHARACTER)
AI_VOICE_CHARACTER = (os.getenv("AI_VOICE_CHARACTER") or "lucy-voice-female1").strip()
