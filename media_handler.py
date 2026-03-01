import os
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from translator import translate_to_target

def setup_media_handlers(userbot: TelegramClient, admin_bot: TelegramClient):
    
    SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
    ADMIN_GROUP = int(os.getenv("ADMIN_GROUP"))

    # --- SCENARIO A: Album Handler ---
    @userbot.on(events.Album(chats=SOURCE_CHANNEL))
    async def handle_album(event):
        print(f"\n📸 --- ALBUM DETECTED ({len(event.messages)} items) ---")
        await process_and_send_draft(event.messages, admin_bot, ADMIN_GROUP)

    # --- SCENARIO B: Single Message Handler ---
    @userbot.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handle_single_message(event):
        # Ignore messages that belong to an album (events.Album handles them)
        if event.message.grouped_id:
            return 
            
        print("\n📝 --- SINGLE MESSAGE DETECTED ---")
        await process_and_send_draft([event.message], admin_bot, ADMIN_GROUP)


    async def process_and_send_draft(messages, admin_bot, admin_group):
        text_to_translate = ""
        media_bundle = []
        
        for msg in messages:
            # Grab the text/caption
            if msg.text and not text_to_translate:
                text_to_translate = msg.text
                
            # Grab the media object
            if msg.media:
                media_bundle.append(msg.media)
        
        print("⚙️ Translating text via Gemini...")
        translated_text = await translate_to_target(text_to_translate)
        
        buttons = [
            [Button.inline("✅ Accept & Post", data=b"post_draft")],
            [Button.inline("❌ Reject", data=b"reject_draft")]
        ]
        
        print("🚀 Sending draft to Admin Group...")
        try:
            if media_bundle:
                # Send the media bundle first
                sent_msgs = await admin_bot.send_file(
                    admin_group, 
                    file=media_bundle, 
                    caption=translated_text,
                    parse_mode='html'
                )
                
                # Telethon returns a list if it was an album, or a single message if 1 item
                reply_id = sent_msgs[0].id if isinstance(sent_msgs, list) else sent_msgs.id
                
                # Reply with the buttons
                await admin_bot.send_message(
                    admin_group, 
                    "Draft ready. Choose an action:", 
                    reply_to=reply_id, 
                    buttons=buttons
                )
            else:
                # Just text
                await admin_bot.send_message(
                    admin_group, 
                    translated_text, 
                    buttons=buttons,
                    parse_mode='html'
                )
            print("📬 Draft successfully delivered!")
        except Exception as e:
            print(f"❌ Error sending draft: {e}")