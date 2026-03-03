from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Run this for BOTH your Userbot and your Bot
print("--- USERBOT STRING ---")
with TelegramClient(StringSession(), "25404872", "ec5921c38d2390b4c10745b911a15099") as client:
    print(client.session.save())

print("\n--- ADMIN_BOT STRING ---")
with TelegramClient(StringSession(), "25404872", "ec5921c38d2390b4c10745b911a15099") as client:
    # (The bot string is shorter/different but works the same)
    print(client.session.save())