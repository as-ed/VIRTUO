import os

from flask import Flask, redirect, render_template, request, send_from_directory

from config import CFG
from file_converter import create_epub, create_mp3, create_pdf


server = Flask(__name__)


@server.get("/")
def home() -> str:
	"""
	Home page of the web interface
	"""
	return render_template("home.html", books=os.listdir(CFG["book_location"]))


@server.get("/books/<filename>/book.txt")
def download_txt(filename):
	return send_from_directory(os.path.join(CFG["book_location"], filename), "book.txt")


@server.get('/books/<filename>/book.pdf')
def download_pdf(filename):
	create_pdf(os.path.join(CFG["book_location"], filename))
	return send_from_directory('books/' + filename, 'book.pdf')


@server.get('/books/<filename>/book.epub')
def download_epub(filename):
	create_epub(os.path.join(CFG["book_location"], filename))
	return send_from_directory('books/' + filename, 'book.epub')


@server.route('/system/scan', methods=['GET', 'POST'])
def begin_scan():
	if request.method == 'POST':
		print("scanning book!")
		return '', 204
	else:
		return redirect('/', 307)
