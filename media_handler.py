import os
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from translator import translate_to_target

def setup_media_handlers(userbot: TelegramClient, admin_bot: TelegramClient):
    
    # Parse multiple source channels into a list of integers
    raw_channels = os.getenv("SOURCE_CHANNELS", "").split(",")
    SOURCE_CHANNELS = [int(c.strip()) for c in raw_channels if c.strip()]
    ADMIN_GROUP = int(os.getenv("ADMIN_GROUP"))

    print(f"🔍 Listening to multiple source channels: {SOURCE_CHANNELS}")

    # Pass the LIST of channels to the events
    @userbot.on(events.Album(chats=SOURCE_CHANNELS))
    async def handle_album(event):
        print(f"\n📸 --- ALBUM DETECTED ({len(event.messages)} items) ---")
        await process_and_send_draft(event.messages, admin_bot, ADMIN_GROUP)

    @userbot.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def handle_single_message(event):
        if event.message.grouped_id:
            return 
        print("\n📝 --- SINGLE MESSAGE DETECTED ---")
        await process_and_send_draft([event.message], admin_bot, ADMIN_GROUP)

    async def process_and_send_draft(messages, admin_bot, admin_group):
        text_to_translate = ""
        downloaded_files = []
        
        for msg in messages:
            if msg.text and not text_to_translate:
                text_to_translate = msg.text
            if msg.media:
                path = await msg.download_media()
                downloaded_files.append(path)
        
        translated_text = await translate_to_target(text_to_translate)
        
        try:
            if downloaded_files:
                sent_msgs = await admin_bot.send_file(
                    admin_group, 
                    file=downloaded_files, 
                    caption=translated_text,
                    parse_mode='html'
                )
                for f in downloaded_files:
                    if os.path.exists(f): os.remove(f)
                        
                ids_list = [sent_msgs] if not isinstance(sent_msgs, list) else sent_msgs
                msg_ids_str = ",".join([str(m.id) for m in ids_list])
            
                buttons = [
                    [Button.inline("✅ Accept & Post", data=f"post_album:{msg_ids_str}".encode())],
                    [Button.inline("❌ Reject", data=f"reject_album:{msg_ids_str}".encode())]
                ]
                
                reply_id = ids_list[-1].id
                await admin_bot.send_message(
                    admin_group, 
                    "Draft ready.\n\n*To edit: Simply REPLY to this message with your new text.*", 
                    reply_to=reply_id, 
                    buttons=buttons
                )
            else:
                temp_msg = await admin_bot.send_message(admin_group, translated_text, parse_mode='html')
                buttons = [
                    [Button.inline("✅ Accept & Post", data=f"post_album:{temp_msg.id}".encode())],
                    [Button.inline("❌ Reject", data=f"reject_album:{temp_msg.id}".encode())]
                ]
                await temp_msg.edit(
                    text=f"{translated_text}\n\n*To edit: Simply REPLY to this message with your new text.*",
                    buttons=buttons,
                    parse_mode='html'
                )
            print("📬 Draft successfully delivered!")
        except Exception as e:
            print(f"❌ Error sending draft: {e}")