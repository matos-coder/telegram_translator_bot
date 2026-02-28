import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the NEW Gemini SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def translate_to_target(text: str, target_lang="English") -> str:
    if not text:
        return ""
        
    prompt = f"""
    You are an expert translator. Translate the following text into {target_lang}.
    CRITICAL INSTRUCTION: Preserve all HTML tags (<b>, <i>, <a href="...">, <code>) exactly as they are. 
    Output ONLY the translated text with the tags.
    
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
        return f"⚠️ TRANSLATION FAILED ⚠️\n\n{text}"