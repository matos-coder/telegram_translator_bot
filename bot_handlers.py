import os
from telethon import TelegramClient, events

def setup_bot_handlers(admin_bot: TelegramClient):
    
    TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
    
    # Try to convert to int if it looks like a numeric ID
    try:
        if TARGET_CHANNEL.startswith("-100") or TARGET_CHANNEL.isdigit():
            TARGET_CHANNEL = int(TARGET_CHANNEL)
    except ValueError:
        pass

    # Pre-fetch the entity to save the access hash to the session
    try:
        admin_bot.get_entity(TARGET_CHANNEL)
        print(f"✅ Target channel {TARGET_CHANNEL} is ready.")
    except Exception as e:
        print(f"⚠️ Warning: Bot hasn't 'seen' the channel yet: {e}")

    @admin_bot.on(events.CallbackQuery())
    async def handle_buttons(event):
        action = event.data
        msg = await event.get_message()
        reply_msg = await msg.get_reply_message()
        
        if action == b"reject_draft":
            print("\n🗑️ Rejecting draft...")
            await event.delete()

            if reply_msg:
                # await admin_bot.delete_messages(event.chat_id, reply_msg.id)
                await reply_msg.delete()
            print("✅ Draft rejected successfully.")
            
        elif action == b"post_draft":
            print("\n📤 Manually posting to target channel...")
            await event.answer() 
            
            try:
                if reply_msg:
                    # Telethon makes it beautifully simple to forward/copy messages
                    await admin_bot.send_message(TARGET_CHANNEL, reply_msg)
                else:
                    await admin_bot.send_message(TARGET_CHANNEL, msg.text)
                    
                await event.edit("✅ Manually Accepted & Posted")
                print("✅ Post successful!")
            except Exception as e:
                print(f"❌ Failed to post draft: {e}")