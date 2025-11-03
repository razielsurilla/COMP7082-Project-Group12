import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def parse_text_to_json(encoded_image, image_type):
    # there'll be more to this prompt later
    # need to figure out how the events are stored in the db before one-hot prompting 
    prompt = f"""
    You are an assistant that extracts structured scheduling data from OCR text.
    Return **only valid JSON**, no explanations or comments.

    I'll kill you if you return **anything other than** valid JSON data.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([
            prompt,
            {
               "inline_data": {
                   "mime_type": f"image/{image_type}",
                   "data": encoded_image
               }
            }
        ])
        
        if not hasattr(response, "text") or not response.text:
            raise RuntimeError("No text returned from Gemini response")

        raw = response.text.strip()

        # this is in case gemini returns markdown
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "").strip()

        return json.loads(raw)

    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        print("Raw output:\n", raw)
        raise ValueError("Gemini output was not valid JSON") from e

    except genai.types.generation_types.BlockedPromptException as e:
        raise RuntimeError(f"Prompt blocked by Gemini safety filters: {e}")

    except genai.types.generation_types.StopCandidateException as e:
        raise RuntimeError(f"Generation stopped early: {e}")

    except Exception as e:
        # all other errors
        raise RuntimeError(f"LLM request failed: {type(e).__name__}: {e}") from e
