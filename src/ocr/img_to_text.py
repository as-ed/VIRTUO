import numpy as np
from PIL import Image
import pytesseract


def get_text(img: np.ndarray) -> str:
	image = Image.fromarray(img).transpose(Image.ROTATE_90)
	image.save("pil_img.png", "PNG")
	text = pytesseract.image_to_string(image)
	return text


def post_processing(text: str) -> str:
	return text
