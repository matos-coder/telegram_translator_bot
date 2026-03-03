import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetMessagesRequest

def setup_bot_handlers(admin_bot: TelegramClient):
    TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
    ADMIN_GROUP = int(os.getenv("ADMIN_GROUP"))
    
    try:
        if TARGET_CHANNEL.startswith("-100") or TARGET_CHANNEL.isdigit():
            TARGET_CHANNEL = int(TARGET_CHANNEL)
    except: pass
    
    # --- NEW: Reply-to-Edit Listener ---
    @admin_bot.on(events.NewMessage(chats=ADMIN_GROUP))
    async def handle_manual_edit(event):
        # Check if the user is replying to a message with text
        if event.is_reply and event.text:
            reply_msg = await event.get_reply_message()
            
            # Check if the message they replied to is a bot draft (has our inline buttons)
            if reply_msg.reply_markup and getattr(reply_msg.reply_markup, 'rows', None):
                try:
                    # Extract the original media IDs from the button data
                    button_data = reply_msg.reply_markup.rows[0].buttons[0].data.decode()
                    if not button_data.startswith("post_album:"): return
                    
                    msg_ids = [int(i) for i in button_data.split(":")[1].split(",") if i.strip()]
                    custom_text = event.text # The user's manually typed text
                    
                    print("\n✏️ Manual Edit Detected! Overriding draft...")
                    
                    album_messages = await admin_bot.get_messages(event.chat_id, ids=msg_ids)
                    valid_messages = [m for m in album_messages if m and not hasattr(m, 'empty')]
                    valid_messages.sort(key=lambda x: x.id)
                    
                    if len(valid_messages) > 1:
                        # Post album with the user's custom text as the caption
                        await admin_bot.send_file(
                            TARGET_CHANNEL, 
                            valid_messages, 
                            caption=custom_text, 
                            parse_mode='html'
                        )
                    elif valid_messages:
                        # Single media or text. We can't easily edit a forwarded media, 
                        # so we resend the file with the new caption
                        if valid_messages[0].media:
                            await admin_bot.send_file(TARGET_CHANNEL, file=valid_messages[0].media, caption=custom_text, parse_mode='html')
                        else:
                            await admin_bot.send_message(TARGET_CHANNEL, custom_text, parse_mode='html')

                    # Cleanup the admin interface
                    await event.reply("✅ Custom edit posted successfully!")
                    await admin_bot.delete_messages(event.chat_id, msg_ids + [reply_msg.id])
                    
                except Exception as e:
                    print(f"❌ Failed to post edited draft: {e}")

    @admin_bot.on(events.CallbackQuery())
    async def handle_buttons(event):
        await event.answer()
        
        try:
            data = event.data.decode().split(":")
            if len(data) < 2: return
                
            action = data[0]
            # Convert string IDs back to integers
            msg_ids = [int(i) for i in data[1].split(",") if i.strip()]

            if action == "reject_album":
                print("\n🗑️ Rejecting draft...")
                await event.delete()
                # Delete the original media and the "Draft ready" message
                await admin_bot.delete_messages(event.chat_id, msg_ids + [event.message_id])
                
            elif action == "post_album":
                print("\n📤 Manually posting to target channel...")
                
                # 1. Fetch the messages using the high-level get_messages
                album_messages = await admin_bot.get_messages(event.chat_id, ids=msg_ids)
                
                # 2. Filter out any None or MessageEmpty results
                valid_messages = [m for m in album_messages if m and not hasattr(m, 'empty')]

                if not valid_messages:
                    print("❌ No valid messages found to post.")
                    return

                # 3. Sort messages to ensure the one with the caption comes first
                valid_messages.sort(key=lambda x: x.id)

                # 4. Extract the caption from the first message in the group
                # Telegram usually stores the album caption in the first message's text field
                final_caption = next((m.text for m in valid_messages if m.text), None)

                try:
                    if len(valid_messages) > 1:
                        # Send as an album with the extracted caption
                        await admin_bot.send_file(
                            TARGET_CHANNEL, 
                            valid_messages, 
                            caption=final_caption, 
                            parse_mode='html'
                        )
                    else:
                        # Single message (already contains its own caption/text)
                        await admin_bot.send_message(TARGET_CHANNEL, valid_messages[0])
                        
                    await event.edit("✅ Manually Accepted & Posted")
                    print("✅ Post successful!")
                except Exception as e:
                    print(f"❌ Failed to post: {e}")


        except Exception as e:
            print(f"❌ Error in handle_buttons: {e}")
