import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telethon import TelegramClient
from telethon.sessions import StringSession
from media_handler import setup_media_handlers
from bot_handlers import setup_bot_handlers
from dotenv import load_dotenv

# Load your .env variables
load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MUFC Translator Bot is Running"}

async def start_telegram_logic():
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    USER_STRING = os.getenv("USER_SESSION_STRING")
    BOT_STRING = os.getenv("BOT_SESSION_STRING")

    userbot = TelegramClient(StringSession(USER_STRING), API_ID, API_HASH)
    admin_bot = TelegramClient(StringSession(BOT_STRING), API_ID, API_HASH)

    await userbot.start()
    await admin_bot.start(bot_token=BOT_TOKEN)
    
    print("✅ Both clients are online!")

    setup_media_handlers(userbot, admin_bot)
    setup_bot_handlers(admin_bot)

    # Keep both running
    await asyncio.gather(userbot.run_until_disconnected(), admin_bot.run_until_disconnected())

async def run_all():
    config = uvicorn.Config(app, host="0.0.0.0", port=7860, loop="asyncio")
    server = uvicorn.Server(config)

    # 2. Run both the Web Server and the Telegram Logic concurrently
    await asyncio.gather(
        server.serve(),
        start_telegram_logic()
    )

if __name__ == "__main__":
    asyncio.run(run_all())
