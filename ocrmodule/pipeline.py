from ocrmodule.ocr_handler import extract_text_from_image
from ocrmodule.llm_parser import parse_text_to_json

def process_image_to_db(image_path: str):
    text: str = extract_text_from_image(image_path)
    data = parse_text_to_json(text)
