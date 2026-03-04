import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the NEW Gemini SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def translate_to_target(text: str, target_lang="Amharic") -> str:
    if not text:
        return ""
        
    OUR_SIGNATURE = "@manutdet10"
    
    prompt = f"""
    You are an expert sports journalist for Manchester United.
    Translate the following text into {target_lang}.

    CRITICAL CLEANING RULES:
    1. REMOVE all existing Telegram usernames (e.g., @anything).
    2. REMOVE all promotional links, invite links (t.me/...), and advertisement sentences.
    3. REMOVE any source signatures or "Join our channel" requests.
    4. FIX terminology: Ensure "Red Devils", "Gaffer", and player names are translated with a hype tone.
    5. HTML TAGS: Preserve <b>, <i>, <a> tags for actual news content only.

    OUTPUT FORMAT:
    - [Translated News Content]
    - 
    - {OUR_SIGNATURE}

    Original Text:
    {text}
    """
    
    print("⏳ Sending text to Gemini for translation...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Using the latest fast model
            contents=prompt,
        )
        print("✅ Translation successful!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        return f"\n\n{text}"