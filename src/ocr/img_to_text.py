import os
from typing import Tuple

import numpy as np
from PIL import Image
import pytesseract
import cv2

from config import CFG


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
	# Load the image into a CV2 object and convert it to grayscale
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Rotate image by 90 degrees as camera returns a landscape orientation
	rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

	# Binarize the image (Make each pixel either black or white based on a threshold)
	_, binary = cv2.threshold(rotated, CFG["camera"]["black_threshold"], 255, cv2.THRESH_BINARY)

	# Thicken the characters by eroding the surrounding white pixels
	kernel = np.ones((3, 3), np.uint8)
	eroded = cv2.erode(binary, kernel, iterations=1)

	# Apply noise removal (smoothen character edges)
	denoised = cv2.fastNlMeansDenoising(eroded, None, 20, 7, 21)

	return Image.fromarray(denoised)


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
