from datetime import datetime
import json
from json import JSONDecodeError
import os
from typing import Union, Tuple

from flask import Flask, redirect, render_template, request, send_from_directory, Response

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

	books = cont.books()

	books.sort(key=lambda b: b["time"], reverse=True)

	return render_template("home.html", books=books, voices=voices, current_voice=cont.voice, scanning=cont.scanning, listening=cont.listening, paused=cont.paused, volume=cont.volume)


@server.get("/books/<book>/book.txt")
def download_txt(book: str) -> Union[str, Response]:
	if not os.path.isfile(_get_path(book, "book.txt")):
		return render_template("redirect.html")
	else:
		return send_from_directory(_get_path(book), "book.txt")


@server.get("/books/<book>/book.pdf")
def download_pdf(book: str) -> Response:
	conv.create_pdf(_get_path(book))
	return send_from_directory(_get_path(book), "book.pdf")


@server.route("/books/<book>/book.epub")
def download_epub(book: str) -> Response:
	conv.create_epub(_get_path(book))
	return send_from_directory(_get_path(book), "book.epub")


@server.route("/books/<book>/book.mp3")
def download_mp3(book: str) -> Response:
	conv.create_mp3(_get_path(book))
	return send_from_directory(_get_path(book), "book.mp3")


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
def start_scan() -> Tuple[str, int]:
	book = cont.scan(request.args["listen"] == "true", request.args["book"] if "book" in request.args else None)
	return ({"id": book[0], "time": book[1].strftime("%Y-%m-%d\u00a0\u00a0\u00a0%H:%M")}, 200) if book is not None else ("", 400)


@server.post("/system/scan/stop")
def stop_scan() -> Tuple[str, int]:
	cont.stop_scan()
	return ({"id": book[0], "pages": book[1]}, 200) if (book := cont.stop_scan()) is not None else ("", 400)


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


@server.route("/system/fastForward", methods=["GET", "POST"])
def fast_forward() -> Tuple[str, int]:
	cont.fast_forward()
	return "", 204


@server.post("/system/rewind")
def rewind() -> Tuple[str, int]:
	cont.rewind()
	return "", 204


@server.get("/fonts/<file>")
def font(file: str) -> Response:
	return send_from_directory(os.path.join(server.root_path, "static", "fonts"), file)


def _get_path(book: str, file: str = None) -> str:
	return os.path.join(CFG["book_location"], book) if file is None else os.path.join(CFG["book_location"], book, file)
