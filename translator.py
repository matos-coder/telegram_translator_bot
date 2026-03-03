import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the NEW Gemini SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def translate_to_target(text: str, target_lang="Amharic") -> str:
    if not text:
        return ""
        
    prompt = f"""
    You are an expert sports journalist and translator specializing in Manchester United. 
    Translate the following text into {target_lang}.
    
    CRITICAL CONTEXT & RULES:
    - This is for a Manchester United news channel. 
    - Accurately translate football/soccer terminology, club slang (e.g., "Red Devils", "Gaffer", "Old Trafford"), and maintain the hype and tone of sports journalism.
    - Preserve all HTML tags (<b>, <i>, <a href="...">, <code>) exactly as they are. 
    - Output ONLY the translated text with the tags. No conversational filler.
    
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