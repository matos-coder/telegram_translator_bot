import os
from pyrogram import Client
from pyrogram.types import CallbackQuery

def setup_bot_handlers(admin_bot: Client):
    
    def parse_chat_id(chat_id_str):
        if not chat_id_str: return None
        return int(chat_id_str) if chat_id_str.lstrip('-').isdigit() else chat_id_str

    TARGET_CHANNEL = parse_chat_id(os.getenv("TARGET_CHANNEL"))

    @admin_bot.on_callback_query()
    async def handle_draft_buttons(client: Client, query: CallbackQuery):
        action = query.data
        admin_chat_id = query.message.chat.id
        
        print(f"🖱️ Button clicked in Admin Group: {action}")

        if action == "reject_draft":
            print("🗑️ Rejecting draft. Deleting messages...")
            # Delete the "Draft ready" message
            await query.message.delete()
            # If it was a reply to media, delete the media too
            if query.message.reply_to_message:
                await query.message.reply_to_message.delete()
            await query.answer("Draft deleted.", show_alert=False)
            print("✅ Draft rejected successfully.")

        elif action == "post_draft":
            print(f"📤 Posting draft to target channel: {TARGET_CHANNEL}...")
            
            try:
                # Check if this is attached to a media group/image or just text
                if query.message.reply_to_message:
                    target_msg = query.message.reply_to_message
                    
                    if target_msg.media_group_id:
                        # It's an album. We copy the whole media group.
                        print("📦 Copying Album to target channel...")
                        await client.copy_media_group(
                            chat_id=TARGET_CHANNEL,
                            from_chat_id=admin_chat_id,
                            message_id=target_msg.id
                        )
                    else:
                        # It's a single image/video
                        print("🖼️ Copying single media to target channel...")
                        await target_msg.copy(chat_id=TARGET_CHANNEL)
                else:
                    # It's just a text message
                    print("📝 Copying text message to target channel...")
                    await query.message.copy(
                        chat_id=TARGET_CHANNEL, 
                        reply_markup=None # Strip the inline buttons
                    )
                
                # Cleanup the admin interface
                await query.message.edit_text("✅ Manually Accepted & Posted to channel.")
                await query.answer("Successfully Posted!", show_alert=True)
                print("✅ Post successful!")
                
            except Exception as e:
                print(f"❌ Failed to post draft: {e}")
                await query.answer("Error posting to channel. Check console.", show_alert=True)