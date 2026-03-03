import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from translator import translate_to_target

# Global dictionary to track auto-post timers
pending_auto_posts = {}

def setup_media_handlers(userbot: TelegramClient, admin_bot: TelegramClient):
    
    # Parse multiple source channels into a list of integers
    raw_channels = os.getenv("SOURCE_CHANNELS", "").split(",")
    SOURCE_CHANNELS = [int(c.strip()) for c in raw_channels if c.strip()]
    ADMIN_GROUP = int(os.getenv("ADMIN_GROUP"))
    TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
    
    try:
        if TARGET_CHANNEL.startswith("-100") or TARGET_CHANNEL.isdigit():
            TARGET_CHANNEL = int(TARGET_CHANNEL)
    except: pass

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
    
    async def auto_post_timer(msg_ids_str, admin_group, target_channel, delay=1800):
        """Wait 30 minutes, then post if not cancelled."""
        await asyncio.sleep(delay)
        print(f"⏰ Timer expired for {msg_ids_str}. Auto-posting now...")
        
        # We trigger the 'post_album' logic directly
        msg_ids = [int(i) for i in msg_ids_str.split(",") if i.strip()]
        album_messages = await admin_bot.get_messages(admin_group, ids=msg_ids)
        valid_messages = [m for m in album_messages if m and not hasattr(m, 'empty')]
        
        if valid_messages:
            valid_messages.sort(key=lambda x: x.id)
            final_caption = next((m.text for m in valid_messages if m.text), None)
            if final_caption and "*To edit:" in final_caption:
                final_caption = final_caption.split("\n\n*To edit:")[0]

            if len(valid_messages) > 1:
                await admin_bot.send_file(target_channel, valid_messages, caption=final_caption, parse_mode='html')
            else:
                if valid_messages[0].media:
                    await admin_bot.send_file(target_channel, valid_messages[0].media, caption=final_caption, parse_mode='html')
                else:
                    await admin_bot.send_message(target_channel, final_caption, parse_mode='html')
            
            await admin_bot.send_message(admin_group, "🤖 **Auto-posted after 30 minutes.**")
        
        pending_auto_posts.pop(msg_ids_str, None)

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