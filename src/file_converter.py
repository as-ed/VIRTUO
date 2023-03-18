import json
import os

from pypandoc import convert_file

from audio.audio_player import AudioPlayer
from controller import controller as cont


def create_pdf(book_path: str) -> None:
	txt_path = os.path.join(book_path, cont.TEXT_FILE)
	pdf_path = os.path.join(book_path, "book.pdf")

	if os.path.isfile(txt_path) and not os.path.exists(pdf_path):
		convert_file(txt_path, "pdf", "md", outputfile=pdf_path)


def create_epub(book_path: str) -> None:
	txt_path = os.path.join(book_path, cont.TEXT_FILE)
	epub_path = os.path.join(book_path, "book.epub")

	if os.path.isfile(txt_path) and not os.path.exists(epub_path):
		with cont.metadata_lock, open(os.path.join(book_path, cont.METADATA_FILE)) as f:
			metadata = json.load(f)
			convert_file(txt_path, "epub", "md", outputfile=epub_path, extra_args=["--epub-title-page=false", f"--metadata title={metadata['title'] if 'title' in metadata and metadata['title'] != '' else 'Book'}{ 'author=' + metadata['author'] if 'author' in metadata and metadata['author'] else ''}"])


def create_mp3(book_path: str) -> None:
	if os.path.isdir(os.path.join(book_path, "audio")) and not os.path.exists(os.path.join(book_path, "book.mp3")):
		AudioPlayer.join_mp3s(book_path)
