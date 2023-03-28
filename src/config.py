import os, discord
from dotenv import load_dotenv
load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GCLOUD_API_KEY = os.path.join(os.path.dirname(__file__), "../" + os.environ["GCLOUD_API_KEY"])

BOT_NAME = os.environ["BOT_NAME"]
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

SUPERUSER = [
    458449942370058271
]

ALLOWED_SERVER_IDS = [
    998467063972626513,
    513511763334135809,
    801079456244170792,
]

ACTIVITY_NAME = "Under Construction ⚒️"
ACTIVITY_TYPE = discord.ActivityType.playing

SRC_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(SRC_DIR, "../logs/latest.log")

SECONDS_DELAY_RECEIVING_MSG = 3  # give a delay for the bot to respond so it can catch multiple messages
ACTIVE_THREAD_PREFIX = "💬✅"
INACTIVE_THREAD_PREFIX = "💬❌"
MAX_THREAD_MESSAGES = 200
MAX_CHARS_PER_REPLY_MSG = 1500  # discord has a 2k limit, we just break message into 1.5k