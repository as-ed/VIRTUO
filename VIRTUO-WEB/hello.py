from flask import Flask, render_template, send_from_directory
from markupsafe import escape
#from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)

#app.wsgi_app = ProxyFix(
#            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
#        )

@app.route("/")
def home():
    
    '''
    
    book = {
            title: date or user chosen date
            author: author of book
            creation-time: date + time of creation of book
            }

    books/
        20230210-1715/
            20230210-1715.txt
            metadata.json
    '''

    if os.listdir("./books"):
        dirs = [name for name in os.listdir("./books")]
    else:
        dirs = []
    return render_template("home.html", books=dirs)

@app.route('/books/<filename>/book.txt')
def download_txt(filename):
    return send_from_directory('books/' + filename, 'book.txt')

@app.route('/books/<filename>/book.pdf')
def download_pdf(filename):
    if not os.path.isfile('books/' + filename + '/book.pdf'):
        os.system('pandoc -o books/' + filename.replace(' ', '\\ ') + '/book.pdf books/' + filename.replace(' ', '\\ ') + '/book.txt')
    return send_from_directory('books/' + filename, 'book.pdf')
