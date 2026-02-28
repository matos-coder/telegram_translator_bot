import asyncio
from email.mime import message
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton
from translator import translate_to_target

media_group_cache = {}

def setup_media_handlers(userbot: Client, admin_bot: Client):
    
    # FIX: Intelligently convert channel IDs to integers if they are numbers
    def parse_chat_id(chat_id_str):
        if not chat_id_str: return None
        return int(chat_id_str) if chat_id_str.lstrip('-').isdigit() else chat_id_str

    SOURCE_CHANNEL = parse_chat_id(os.getenv("SOURCE_CHANNEL"))
    ADMIN_GROUP = parse_chat_id(os.getenv("ADMIN_GROUP"))

    print(f"🔍 Userbot is actively listening to channel ID/Username: {SOURCE_CHANNEL}")

    @userbot.on_message(filters.chat(SOURCE_CHANNEL))
    async def intercept_post(client: Client, message: Message):
        print("\n📥 --- NEW MESSAGE INTERCEPTED ---")
        
        
        if message.media_group_id:
            mg_id = message.media_group_id
            print(f"📸 Detected Album part! Media Group ID: {mg_id}")
            
            if mg_id not in media_group_cache:
                print("⏱️ First item in album. Waiting 3 seconds to gather the rest...")
                media_group_cache[mg_id] = [message]
                await asyncio.sleep(3) 
                
                print(f"📦 Gathering complete. Processing {len(media_group_cache[mg_id])} items.")
                album_messages = media_group_cache.pop(mg_id)
                await process_and_send_draft(album_messages, admin_bot, ADMIN_GROUP)
            else:
                print("📎 Adding another item to waiting album...")
                media_group_cache[mg_id].append(message)
                
        else:
            print("📝 Detected Single Message (Text/Single Media). Processing immediately...")
            await process_and_send_draft([message], admin_bot, ADMIN_GROUP)


    async def process_and_send_draft(messages: list, admin_bot: Client, admin_group):
        text_to_translate = ""
        media_bundle = []
        
        for msg in messages:
            if msg.text:
                text_to_translate = msg.text.html
            elif msg.caption:
                text_to_translate = msg.caption.html
                
            if msg.photo:
                media_bundle.append(InputMediaPhoto(media=msg.photo.file_id))
            elif msg.video:
                media_bundle.append(InputMediaVideo(media=msg.video.file_id))
        
        print("⚙️ Processing translation...")
        translated_text = await translate_to_target(text_to_translate)
        
        if media_bundle:
            media_bundle[0].caption = translated_text
            media_bundle[0].parse_mode = getattr(media_bundle[0], "parse_mode", None)

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept & Post", callback_data="post_draft")],
            [InlineKeyboardButton("❌ Reject", callback_data="reject_draft")]
        ])

        print("🚀 Sending draft to Admin Group...")
        try:
            if media_bundle:
                sent_msgs = await admin_bot.send_media_group(chat_id=admin_group, media=media_bundle)
                await admin_bot.send_message(
                    chat_id=admin_group, 
                    text="Draft ready. Choose an action:", 
                    reply_to_message_id=sent_msgs[0].id,
                    reply_markup=buttons
                )
            else:
                await admin_bot.send_message(chat_id=admin_group, text=translated_text, reply_markup=buttons)
            print("📬 Draft successfully delivered to Admin Group!")
        except Exception as e:
            print(f"❌ Error sending draft to admin: {e}")
    @userbot.on_message()
    async def debug_all(client, message):
        print("🔥 RECEIVED:", message.chat.title, message.chat.type)
        
    @userbot.on_message()
    async def debug_all(client, message):
        print("🔥 RECEIVED:")
        print("Title:", message.chat.title)
        print("ID:", message.chat.id)
        print("Type:", message.chat.type)
        print("Text:", message.text)
        print("-----------")