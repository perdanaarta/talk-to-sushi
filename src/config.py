import os, discord
from dotenv import load_dotenv
load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

SUPERUSER = [
    458449942370058271
]

ACTIVITY_NAME = "Under Construction ⚒️"
ACTIVITY_TYPE = discord.ActivityType.playing

SRC_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(SRC_DIR, "../logs/latest.log")