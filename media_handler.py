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
        downloaded_files = []
        group_id = messages[0].grouped_id 
        
        for msg in messages:
            # Grab the text/caption
            if msg.text and not text_to_translate:
                text_to_translate = msg.text
                
            # Grab the media object
            if msg.media:
                # Download media to a temporary file
                # This makes the file 'owned' by your bot script
                path = await msg.download_media()
                downloaded_files.append(path)
        
        print("⚙️ Translating text via Gemini...")
        translated_text = await translate_to_target(text_to_translate)
        
        # post_data = f"post_draft:{group_id}".encode()
        # reject_data = f"reject_draft:{group_id}".encode()
        
        # buttons = [
        #     [Button.inline("✅ Accept & Post", data=post_data)],
        #     [Button.inline("❌ Reject", data=reject_data)]
        # ]
        
        print("🚀 Sending draft to Admin Group...")
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
                        
                # Create the comma-separated ID string
                ids_list = [sent_msgs] if not isinstance(sent_msgs, list) else sent_msgs
                msg_ids_str = ",".join([str(m.id) for m in ids_list])
            
                buttons = [
                    [Button.inline("✅ Accept & Post", data=f"post_album:{msg_ids_str}".encode())],
                    [Button.inline("❌ Reject", data=f"reject_album:{msg_ids_str}".encode())]
                ]
                
                reply_id = ids_list[-1].id
                await admin_bot.send_message(admin_group, "Draft ready.", reply_to=reply_id, buttons=buttons)
            else:
                # Handle TEXT ONLY messages
                # We still need buttons for text-only!
                temp_msg = await admin_bot.send_message(admin_group, translated_text, parse_mode='html')
                
                text_buttons = [
                    [Button.inline("✅ Accept & Post", data=f"post_album:{temp_msg.id}".encode())],
                    [Button.inline("❌ Reject", data=f"reject_album:{temp_msg.id}".encode())]
                ]
                await temp_msg.edit(buttons=text_buttons)

            print("📬 Draft successfully delivered!")
        except Exception as e:
            print(f"❌ Error sending draft: {e}")
        # try:
        #     if media_bundle:
        #         # Send the media bundle first
        #         sent_msgs = await admin_bot.send_file(
        #             admin_group, 
        #             file=media_bundle, 
        #             caption=translated_text,
        #             parse_mode='html'
        #         )
                
        #         # Telethon returns a list if it was an album, or a single message if 1 item
        #         reply_id = sent_msgs[0].id if isinstance(sent_msgs, list) else sent_msgs.id
                
        #         # Reply with the buttons
        #         await admin_bot.send_message(
        #             admin_group, 
        #             "Draft ready. Choose an action:", 
        #             reply_to=reply_id, 
        #             buttons=buttons
        #         )
        #     else:
        #         # Just text
        #         await admin_bot.send_message(
        #             admin_group, 
        #             translated_text, 
        #             buttons=buttons,
        #             parse_mode='html'
        #         )
        #     print("📬 Draft successfully delivered!")
        # except Exception as e:
        #     print(f"❌ Error sending draft: {e}")