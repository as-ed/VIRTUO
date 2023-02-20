import os

from flask import Flask, redirect, render_template, request, send_from_directory

from config import CFG


server = Flask(__name__)


@app.get("/")
def home() -> str:
	"""
	Home page of the web interface
	"""
	return render_template("home.html", books=os.listdir(CFG["book_location"]))


@app.get("/books/<filename>/book.txt")
def download_txt(filename):
	return send_from_directory(CFG["book_location"] + filename, "book.txt")


@app.get('/books/<filename>/book.pdf')
def download_pdf(filename):
	if not os.path.isfile('books/' + filename + '/book.pdf'):
		os.system('pandoc -o books/' + filename.replace(' ', '\\ ') + '/book.pdf books/' + filename.replace(' ', '\\ ') + '/book.txt')
	return send_from_directory('books/' + filename, 'book.pdf')


@app.get('/books/<filename>/book.epub')
def download_epub(filename):
	if not os.path.isfile('books/' + filename + '/book.epub'):
		os.system('pandoc --metadata title=' + filename.replace(' ', '\\ ') + ' -o books/' + filename.replace(' ', '\\ ') + '/book.epub books/' + filename.replace(' ', '\\ ') + '/book.txt')
	return send_from_directory('books/' + filename, 'book.epub')


@app.route('/system/scan', methods=['GET','POST'])
def begin_scan():
	if request.method == 'POST':
		print("scanning book!")
		return '', 204
	else:
		return redirect('/', 307)
