# Translator Bot

An automated **Manchester United news aggregator and translator**.  
This bot monitors multiple Telegram “source” channels, translates the content into **Amharic** using **Gemini 2.5 Flash**, and provides an admin‑controlled workflow for approval, manual editing, and 30‑minute auto‑posting.

---

## 🚀 Key Features

- **Dual‑Client Architecture**  
  Uses a *Userbot* (Telethon) to “spy” on source channels and an *Admin Bot* to manage the private group and public channel.

- **AI‑Powered Translation**  
  Leverages Google Gemini for context‑aware sports journalism translations.

- **Smart Cleaning**  
  Automatically strips promotional links, external usernames and “Join” requests from source messages.

- **Admin Workflow**  
  1. **Manual Post** – one‑click approval.  
  2. **Manual Edit** – reply to a draft to override the AI translation.  
  3. **Auto‑Post** – a 30‑minute safety timer posts automatically if no action is taken.

- **Media Support**  
  Handles single photos, videos and full albums (grouped messages).

---

## 🛠 Tech Stack

| Component     | Details                                              |
|---------------|------------------------------------------------------|
| **Language**  | Python 3.10+                                         |
| **Framework** | Telethon (MTProto API)                               |
| **AI**        | Google GenAI (Gemini 2.5 Flash)                      |
| **Web Server**| FastAPI + Uvicorn (for Hugging Face health checks)   |
| **Deployment**| Docker / Hugging Face Spaces                         |

---

## 📂 Project Structure

| File              | Responsibility                                                                 |
|-------------------|--------------------------------------------------------------------------------|
| `main.py`         | Entry point. Starts FastAPI server and initializes both Telegram clients.     |
| `media_handler.py`| Detects new messages/albums and handles the 30‑minute auto‑post timer logic.   |
| `bot_handlers.py` | Manages Admin Group interactions (Accept, Reject, Manual Edit replies).       |
| `translator.py`   | Contains the Gemini AI prompt and cleaning rules for news content.           |
| `Dockerfile`      | Container configuration for cloud deployment (Hugging Face/Koyeb).           |

---

## ⚙️ Environment Variables

Set these in your `.env` file or cloud dashboard:

| Variable               | Description                                                         |
|------------------------|---------------------------------------------------------------------|
| `API_ID` / `API_HASH`  | Obtained from [my.telegram.org](https://my.telegram.org/).           |
| `BOT_TOKEN`            | Obtained from @BotFather.                                           |
| `USER_SESSION_STRING`  | Telethon string session for the Userbot account.                    |
| `BOT_SESSION_STRING`   | Telethon string session for the Bot account.                        |
| `GEMINI_API_KEY`       | API key from Google AI Studio.                                      |
| `SOURCE_CHANNELS`      | Comma‑separated IDs of channels to monitor (e.g., `-100123,-100456`).|
| `ADMIN_GROUP`          | ID of the private group where drafts are sent.                      |
| `TARGET_CHANNEL`       | ID or @username of the public channel where news is posted.         |

---

## 📦 Deployment on Hugging Face

1. **Create a New Space** – choose Docker (Blank template).  
2. **Add Secrets** – in *Settings → Variables and Secrets*, paste all the environment variables above.  
3. **Upload Files** – push all `.py` files, `requirements.txt`, and the `Dockerfile`.  
4. **Health Check** – ensure the bot listens on port `7860`. The Space shows “Running” once FastAPI starts.

---

## 📝 Usage & Workflow

1. **Detection** – a news post appears in a source channel.  
2. **Drafting** – the bot translates it and sends a draft to the Admin Group with Accept/Reject buttons.  
3. **Manual Edit** – reply to the bot’s draft with your own text to override the AI translation; the bot cancels the auto‑timer.  
4. **Auto‑Post** – if no action is taken for 30 minutes, the bot strips admin instructions and posts the AI translation to the public channel.

---

## ⚠️ Known Limitations

- **Hugging Face Sleep** – free Spaces sleep after 48 hours of inactivity. Use a ping service (e.g. cron‑job.org) to hit the Space URL hourly.
- **Rate Limits** – Telegram restricts bots to ~30 messages/sec. Avoid monitoring more than 10 high‑traffic channels simultaneously.
