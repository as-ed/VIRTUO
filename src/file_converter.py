import json
import os

from audio.audio_player import player
from audio.tts import tts


def create_pdf(book_path: str) -> None:
	if not os.path.isfile(os.path.join(book_path, "/book.pdf")):
		os.system("pandoc -o " + os.path.join(book_path, "book.pdf").replace(" ", "\\ ") + " " + os.path.join(book_path, "book.txt").replace(" ", "\\ "))


def create_epub(book_path: str) -> None:
	if not os.path.isfile(os.path.join(book_path, "/book.epub")):
		with open(os.path.join(book_path, "metadata.json")) as f:
			metadata = json.load(f)
			title = metadata["title"] if "title" in metadata else "Book"

		os.system("pandoc --metadata title=" + title + " -o " + os.path.join(book_path, "book.epub").replace(" ", "\\ ") + " " + os.path.join(book_path, "book.txt").replace(" ", "\\ "))


def create_mp3(book_path: str) -> None:
	with open(os.path.join(book_path, "book.txt")) as f:
		for chunk in tts.synthesize_long(f.read()):
			player.write_to_raw_file(chunk, os.path.join(book_path, "book.raw"))

		player.raw_to_mp3(os.path.join(book_path, "book.raw"))
