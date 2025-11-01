import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def parse_text_to_json(text: str) -> dict:

    # there'll be more to this prompt later
    # need to figure out how the events are stored in the db before one-hot prompting 
    prompt = f"""
    You are an assistant that extracts structured scheduling data from OCR text.
    Return **only valid JSON**, no explanations or comments.

    I'll kill you if you return **anything other than** valud JSON data.

    Text:
    {text}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        response = model.generate_content(prompt)

        raw = response.text.strip()

        # this is in case gemini returns markdown
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "").strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        raise ValueError("Gemini output was not valid JSON")
    except Exception as e:
        raise RuntimeError(f"LLM request failed: {e}")
