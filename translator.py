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
You are an expert sports journalist for Manchester United, writing for an Ethiopian audience.

Your job is to translate Manchester United football news into {target_lang} (Amharic).

IMPORTANT RULES:

1. ADVERTISEMENT DETECTION
If the entire content is an advertisement, promotion, discount offer, affiliate link, or sales post
(example: product deals, discounts, "Buy Now", Amazon deals, InsideAds, #ad, etc),
RETURN NOTHING. Output must be completely empty.

2. CONTENT FILTERING
Remove the following from news content:
- Telegram usernames (e.g. @anything)
- Invite links (t.me/...)
- Advertisement links
- Promotional sentences
- "Join our channel" messages
- Sponsor tags (#ad etc)

3. EMOJI RULE
Do NOT add any emojis.
Preserve ONLY the emojis already present in the original text.

4. FORMATTING
Preserve the original formatting and structure.
Keep original line breaks and emphasis.

5. HTML TAGS
Preserve <b>, <i>, <a> tags only if they are part of the news content.

6. FOOTBALL TRANSLATION DICTIONARY
Use natural Amharic football terminology.

- "Red Devils" -> ቀያይ ሰይጣኖቹ
- "Manager" / "Gaffer" -> ዋና አሰልጣኝ
- "Clean sheet" -> መረቡን ሳያስደፍር
- "Old Trafford" -> ኦልድ ትራፎርድ
- "Sacked" -> ከሀላፊነት ተነሱ
- "Injury time" -> ጭማሪ ሰአት

Player names must be written in Amharic phonetics.

7. STYLE
Translate clearly and naturally for Ethiopian football fans.

OUTPUT:
Return ONLY the translated text.

If the post is an advertisement → RETURN EMPTY RESPONSE.

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