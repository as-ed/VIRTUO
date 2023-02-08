import os
from typing import Tuple

import numpy as np
from PIL import Image
import pytesseract


def get_text(img: np.ndarray, book_loc: str, page_nr: int = 0, prev_sentence: str = "") -> Tuple[str, str]:
	"""
	Converts image to text.

	:param img: image as a numpy array of RGB values
	:param book_loc: location where the digitized book is stored
	:param page_nr: number of the current page
	:param prev_sentence: last sentence of the previous page
	:return: tuple of 2 strings: (page text except last sentence, last (potentially incomplete) sentence)
	"""
	page_img = _pre_processing(img)
	_save_img(page_img, book_loc, page_nr)

	return _post_processing(_ocr(page_img), prev_sentence)


def _pre_processing(img: np.ndarray) -> Image:
	return Image.fromarray(img).transpose(Image.ROTATE_90)


def _save_img(img: Image, book_loc: str, page_nr: int) -> None:
	path = os.path.join(book_loc, "pages")
	os.makedirs(path, exist_ok=True)
	img.save(os.path.join(path, f"{page_nr}.png"), "PNG")


def _ocr(img: Image) -> str:
	return pytesseract.image_to_string(img)


def _post_processing(text: str, prev_sentence: str) -> Tuple[str, str]:
	# TODO:
	#  - remove line breaks
	#  - remove hyphens that split words
	#  - extract last sentence
	#  - autocorrect
	#  - replace '|' (pipe) with 'I'
	return prev_sentence + " " + text, ""
