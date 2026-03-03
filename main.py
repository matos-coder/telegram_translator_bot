import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

from media_handler import setup_media_handlers
from bot_handlers import setup_bot_handlers

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

USER_SESSION_STRING = os.getenv("USER_SESSION_STRING")
BOT_SESSION_STRING = os.getenv("BOT_SESSION_STRING")
# Initialize Telethon clients
# userbot = TelegramClient('userbot_session', API_ID, API_HASH)
# admin_bot = TelegramClient('admin_bot_session', API_ID, API_HASH)
userbot = TelegramClient(StringSession(USER_SESSION_STRING), API_ID, API_HASH)
admin_bot = TelegramClient(StringSession(BOT_SESSION_STRING), API_ID, API_HASH)

async def main():
    print("🚀 Starting Telethon dual-client system...")
    
    # 1. Start the clients
    await userbot.start()
    await admin_bot.start(bot_token=BOT_TOKEN)
    print("✅ Clients authenticated!")

    # 2. Setup the event listeners
    setup_media_handlers(userbot, admin_bot)
    setup_bot_handlers(admin_bot)
    
    print("🎧 Telethon is actively listening for messages...")
    
    # 3. Keep both clients running indefinitely
    await asyncio.gather(
        userbot.run_until_disconnected(),
        admin_bot.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())