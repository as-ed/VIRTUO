import json
import os
from time import sleep
from typing import Union, Tuple, Dict, List, Generator

from flask import Flask, render_template, request, send_from_directory, Response, send_file

from config import CFG
from controller import controller as cont
import file_converter as conv


server = Flask(__name__)


@server.get("/favicon.ico")
def favicon() -> Response:
	return send_from_directory(os.path.join(server.root_path, "static"), "favicon.ico")


@server.get("/")
def home() -> str:
	voices = cont.get_voices()
	voices.remove(cont.voice)

	return render_template(
		"home.html",
		books=list(reversed(cont.books)),
		voices=voices,
		current_voice=cont.voice,
		scanning=cont.scanning,
		listening=cont.listening,
		playing=cont.playing,
		paused=cont.paused,
		volume=cont.volume,
		page_flip_error=cont.page_flip_error)


@server.get("/books")
def get_books() -> Tuple[List[Dict], int]:
	return cont.books, 200


@server.get("/books/<book>/book.txt")
def download_txt(book: str) -> Response:
	return send_file(os.path.join(_get_path(book), "book.txt"), mimetype="text/plain", download_name=_get_download_name(book, ".txt"))


@server.get("/books/<book>/book.pdf")
def download_pdf(book: str) -> Response:
	conv.create_pdf(_get_path(book))
	return send_file(os.path.join(_get_path(book), "book.pdf"), mimetype="application/pdf", download_name=_get_download_name(book, ".pdf"))


@server.get("/books/<book>/book.epub")
def download_epub(book: str) -> Response:
	conv.create_epub(_get_path(book))
	return send_file(os.path.join(_get_path(book), "book.epub"), mimetype="application/epub+zip", download_name=_get_download_name(book, ".epub"))


@server.get("/books/<book>/book.mp3")
def download_mp3(book: str) -> Response:
	conv.create_mp3(_get_path(book))
	return send_file(os.path.join(_get_path(book), "book.mp3"), mimetype="audio/mpeg", download_name=_get_download_name(book, ".mp3"))


@server.get("/books/<book>/book.stream.mp3")
def stream_mp3(book: str) -> Response:
	def stream() -> Generator[bytes, None, None]:
		for page in sorted(os.scandir(os.path.join(_get_path(book), "audio")), key=lambda file: int(file.name[:-4])):
			with open(page.path, "rb") as f:
				yield f.read()

	return Response(stream(), mimetype="audio/mpeg")


@server.post("/books/<book>/title")
def set_title(book: str) -> Tuple[str, int]:
	return ("", 200) if cont.set_book_attribute(book, "title", request.args["title"]) else ("", 400)


@server.post("/books/<book>/author")
def set_author(book: str) -> Tuple[str, int]:
	return ("", 204) if cont.set_book_attribute(book, "author", request.args["author"]) else ("", 400)


@server.get("/books/<book>/lastPage")
def get_last_page(book: str) -> Tuple[str, int]:
	return cont.last_page(book), 200


@server.post("/system/scan/start")
def start_scan() -> Tuple[Union[Dict, str], int]:
	book = cont.scan(request.args["listen"] == "true", request.args["book"] if "book" in request.args else None)
	return (book, 200) if book is not None else ("", 400)


@server.post("/system/scan/stop")
def stop_scan() -> Tuple[str, int]:
	return ("", 204) if cont.stop_scan() else ("", 400)


@server.post("/system/setVolume/<value>")
def set_volume(value: str) -> Tuple[str, int]:
	cont.volume = int(value) / 100
	return str(cont.volume * 100), 200


@server.post("/system/setVoice/<value>")
def set_voice(value: str) -> Tuple[str, int]:
	cont.voice = value
	return "", 204


@server.get("/system/voiceSample/<value>")
def get_voice_sample(value: str) -> Response:
	return send_from_directory(os.path.join(server.root_path, "static"), value + ".mp3")


@server.post("/system/togglePause")
def toggle_pause() -> Tuple[str, int]:
	return str(cont.toggle_pause()), 200


@server.post("/system/pause")
def pause() -> Tuple[str, int]:
	cont.pause()
	return "", 200


@server.get("/system/playbackPos")
def playback_pos() -> Tuple[str, int]:
	return str(cont.playback_pos), 200


@server.post("/system/seek/<pos>")
def seek(pos: str) -> Tuple[str, int]:
	cont.seek(float(pos))
	return "", 204


@server.route("/system/fastForward", methods=["GET", "POST"])
def fast_forward() -> Tuple[str, int]:
	cont.fast_forward()
	return "", 204


@server.post("/system/rewind")
def rewind() -> Tuple[str, int]:
	cont.rewind()
	return "", 204


@server.post("/system/clearPageFlipError")
def clear_page_flip_error() -> Tuple[str, int]:
	cont.clear_page_flip_error()
	return "", 204


@server.get("/system/status")
def status() -> Tuple[Dict, int]:
	return {
		"scanning": cont.scanning,
		"listening": cont.listening,
		"playing": cont.playing,
		"paused": cont.paused or not cont.playing,
		"volume": cont.volume * 100, "num_books": len(cont.books),
		"current_book_pages": [b for b in cont.books if b["id"] == cont.scanning][0]["pages"] if cont.scanning is not None else -1,
		"page_flip_error": cont.page_flip_error
	}, 200


@server.get("/fonts/<file>")
def font(file: str) -> Response:
	return send_from_directory(os.path.join(server.root_path, "static", "fonts"), file)


def _get_path(book: str, file: str = None) -> str:
	return os.path.join(CFG["book_location"], book) if file is None else os.path.join(CFG["book_location"], book, file)


def _get_download_name(book: str, suffix: str) -> str:
	with cont.metadata_lock, open(os.path.join(_get_path(book), cont.METADATA_FILE)) as f:
		metadata = json.load(f)
		name = title if "title" in metadata and (title := metadata["title"]) != "" else "Book"

		if "author" in metadata and (author := metadata["author"]) != "":
			name += " - " + author

		name += suffix

	return name
