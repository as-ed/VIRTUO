import numpy as np
from PIL import Image
import pytesseract

def get_text(img: np.ndarray) -> str:
    PILImage = Image.fromarray(img)
    text = pytesseract.image_to_string(PILImage)
    return text

def post_processing(text: str) -> str:
	return text
