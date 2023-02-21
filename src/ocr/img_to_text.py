import os
import re
from typing import Tuple

import cv2
from nltk.tokenize import sent_tokenize
import numpy as np
from PIL import Image
import pytesseract
from spellchecker import SpellChecker


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
	#_, binary = cv2.threshold(rotated, CFG["camera"]["black_threshold"], 255, cv2.THRESH_BINARY)

	# Thicken the characters by eroding the surrounding white pixels
	#kernel = np.ones((3, 3), np.uint8)
	#eroded = cv2.erode(binary, kernel, iterations=1)

	# Apply noise removal (smoothen character edges)
	#denoised = cv2.fastNlMeansDenoising(eroded, None, 20, 7, 21)

	return Image.fromarray(rotated)


def _save_img(img: Image, book_loc: str, page_nr: int) -> None:
	path = os.path.join(book_loc, "pages")
	os.makedirs(path, exist_ok=True)
	img.save(os.path.join(path, f"{page_nr}.png"), "PNG")


def _ocr(img: Image) -> str:
	return pytesseract.image_to_string(img)


def _post_processing(text: str, prev_sentence: str) -> Tuple[str, str]:
	# remove white space at start and end
	new_text = re.sub(r"^\s*", "", text)
	new_text = re.sub(r"\s*$", "", new_text)

	# remove hyphens that split words
	new_text = new_text.replace("-\n", "")

	# remove single line breaks
	new_text = re.sub("(^|[^\n])\n($|[^\n])", r"\1 \2", new_text)

	# convert multi line break to single line break
	new_text = re.sub("\n+", "\n", new_text)

	# convert multi white space to single space
	new_text = re.sub("[ \t]+", " ", new_text)

	# convert "|" (pipe) to "I"
	new_text = new_text.replace("|", "I")

	# limit characters
	new_text = re.sub("[\u201d\u201c]", '"', new_text)
	new_text = re.sub("[\u2018\u2019]", "'", new_text)
	new_text = re.sub("[^\\s\\w.,;'\"!?:&()-]", "", new_text)

	# append previous sentence
	if len(prev_sentence) > 0 and prev_sentence[-1] == "-":
		new_text = prev_sentence[:-1] + new_text
	else:
		new_text = prev_sentence + " " + new_text

	# extract last sentence
	sentences = sent_tokenize(new_text)
	new_text = " ".join(sentences[:-1])
	last_sentence = sentences[-1]

	# autocorrect
	new_text = _auto_correct(new_text)

	return new_text, last_sentence


def _auto_correct(text):
	spell_checker = SpellChecker()
	text_array = text.split(" ")
	result = ""

	for word in text_array:
		if word == "":
			continue
		elif word[0].isupper() or (not word[len(word) - 1].isalpha()):
			result = result + word + " "
			continue
		elif len(spell_checker.unknown([word])) == 1:
			w = spell_checker.correction(word)
			if w is not None:
				result = result + w + " "
			else:
				result = result + word + " "
		else:
			result = result + word + " "

	return result
