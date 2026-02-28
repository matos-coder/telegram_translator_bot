import asyncio
# --- PATCH FOR PYTHON 3.12+ ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ------------------------------

import os
from dotenv import load_dotenv
from pyrogram import Client, idle

from bot_handlers import setup_bot_handlers
from media_handler import setup_media_handlers

# Load variables from .env file
load_dotenv()

userbot = Client(
    "userbot_session",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

admin_bot = Client(
    "admin_bot_session",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

async def main():
    print("Starting dual-client system...")
    
    # 1. ATTACH HANDLERS FIRST (Before starting the clients!)
    print("⚙️ Registering event handlers...")
    try:
        setup_media_handlers(userbot, admin_bot)
        setup_bot_handlers(admin_bot)
    except Exception as e:
        print(f"❌ Setup handlers failed: {e}")
        return
    
    # 2. Start Userbot
    print("Initializing Userbot...")
    try:
        await userbot.start()
        # Optional: Print dialogs for debugging
        dialogs = [d async for d in userbot.get_dialogs(limit=10)] # Limited to 10 so it doesn't flood console
        print("📂 Top 10 Userbot dialogs:")
        for d in dialogs:
            print(f"- {d.chat.title or d.chat.username} (ID: {d.chat.id})")
    except Exception as e:
        print(f"❌ Userbot start failed: {e}")
        return
    
    # 3. Start Admin Bot
    print("Initializing Admin Bot...")
    try:
        await admin_bot.start()
    except Exception as e:
        print(f"❌ Admin bot start failed: {e}")
        return
    
    print("✅ Both clients are online and listening!")
    
    # 4. Keep the script running
    await idle()
    
    # 5. Stop clients gracefully if script is terminated
    await userbot.stop()
    await admin_bot.stop()

if __name__ == "__main__":
    asyncio.run(main())