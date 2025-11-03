# from ocrmodule.ocr_handler import extract_text_from_image
from llmmodule.llm_parser import parse_text_to_json
import base64

# def process_image_to_db(image_path: str):
    # text: str = extract_text_from_image(image_path)
    # print(text)
    # data = parse_text_to_json(text)

def process_image_to_db(image_path, extension):
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')

            data = parse_text_to_json(encoded_image, extension)
            print(data)

            return data

    except FileNotFoundError:
        return { "error": f"File not found: {image_path}"}

    except RuntimeError as e:
        return { "error": f"Runtime error during LLM request: {e}"}
        
    except Exception as e:
        return { "error": f"Unexpected error: {e}"}
        
