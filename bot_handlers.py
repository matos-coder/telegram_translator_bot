import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetMessagesRequest

def setup_bot_handlers(admin_bot: TelegramClient):
    TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
    try:
        if TARGET_CHANNEL.startswith("-100") or TARGET_CHANNEL.isdigit():
            TARGET_CHANNEL = int(TARGET_CHANNEL)
    except: pass

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
