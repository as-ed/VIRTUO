from datetime import datetime
import json
from json import JSONDecodeError
import os
from typing import Union, Tuple

from flask import Flask, redirect, render_template, request, send_from_directory, Response

from config import CFG
import controller as cont
import file_converter as conv


server = Flask(__name__)


@server.get("/favicon.ico")
def favicon() -> Response:
	return send_from_directory(os.path.join(server.root_path, "static"), "favicon.ico")


@server.get("/")
def home() -> str:
	voices = cont.get_voices()
	current_voice = cont.get_current_voice()
	voices.remove(current_voice)

	# load metadata of all books
	books = []
	for book_dir in os.scandir(CFG["book_location"]):
		if not book_dir.is_dir():
			continue

		book = {"id": book_dir.name}

		with open(os.path.join(book_dir.path, "metadata.json")) as f:
			try:
				metadata = json.load(f)
			except JSONDecodeError:
				continue

			book["title"] = metadata["title"] if "title" in metadata else ""
			book["author"] = metadata["author"] if "author" in metadata else ""
			book["time"] = datetime.fromtimestamp(metadata["scan_time"])
			book["pages"] = metadata["pages"]

		books.append(book)

	books.sort(key=lambda b: b["time"], reverse=True)

	return render_template("home.html", books=books, voices=voices, currVoice=current_voice)


@server.get("/books/<book>/book.txt")
def download_txt(book) -> Union[str, Response]:
	if not os.path.isfile(_get_path(book, "book.txt")):
		return render_template("redirect.html")
	else:
		return send_from_directory(_get_path(book), "book.txt")


@server.get("/books/<book>/book.pdf")
def download_pdf(book) -> Response:
	conv.create_pdf(_get_path(book))
	return send_from_directory(_get_path(book), "book.pdf")


@server.route("/books/<book>/book.epub")
def download_epub(book) -> Response:
	conv.create_epub(_get_path(book))
	return send_from_directory(_get_path(book), "book.epub")


@server.route("/books/<book>/book.mp3")
def download_mp3(book) -> Response:
	conv.create_mp3(_get_path(book))
	return send_from_directory(_get_path(book), "book.mp3")


@server.post("/books/<book>/title")
def set_title(book) -> Tuple[str, int]:
	return ("", 200) if cont.set_book_attribute(book, "title", request.args["title"]) else ("", 400)


@server.post("/books/<book>/author")
def set_author(book) -> Tuple[str, int]:
	return ("", 200) if cont.set_book_attribute(book, "author", request.args["author"]) else ("", 400)


@server.route("/system/scan/start", methods=["GET", "POST"])
def begin_scan() -> Union[str, Response]:
	if request.method == "POST":
		scanning = cont.scan()
		return str(scanning)
	else:
		return redirect("/", 307)


@server.route("/system/scan/stop", methods=["GET", "POST"])
def stop_scan() -> Union[Tuple[str, int], Response]:
	if request.method == "POST":
		cont.stop_scan()
		return "", 204
	else:
		return redirect("/", 307)


@server.get("/system/getVolume")
def get_volume() -> str:
	return str(cont.get_volume())


@server.route("/system/setVolume/<value>", methods=["GET", "POST"])
def set_volume(value: str) -> Union[str, Response]:
	if request.method == "POST":
		return str(cont.set_volume(int(value) / 100))
	else:
		return redirect("/", 307)


@server.route("/system/setVoice/<value>", methods=["GET", "POST"])
def set_voice(value: str) -> Union[str, Response]:
	if request.method == "POST":
		return str(cont.set_voice(value))
	else:
		return redirect("/", 307)


@server.get("/system/voiceSample/<value>")
def get_voice_sample(value: str) -> Response:
	return send_from_directory(os.path.join(server.root_path, "static"), value + ".mp3")


@server.route("/system/togglePause", methods=["GET", "POST"])
def toggle_pause() -> Union[str, Response]:
	if request.method == "POST":
		return str(cont.toggle_pause())
	else:
		return redirect("/", 307)


@server.route("/system/fastForward", methods=["GET", "POST"])
def fast_forward() -> Union[str, Response]:
	if request.method == "POST":
		cont.fast_forward()
		return ""
	else:
		return redirect("/", 307)


@server.route("/system/rewind", methods=["GET", "POST"])
def rewind() -> Union[str, Response]:
	if request.method == "POST":
		cont.rewind()
		return ""
	else:
		return redirect("/", 307)


def _get_path(book: str, file: str = None) -> str:
	return os.path.join(CFG["book_location"], book) if file is None else os.path.join(CFG["book_location"], book, file)
