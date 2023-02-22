from flask import Flask, redirect, render_template, request, send_from_directory
from markupsafe import escape
#from werkzeug.middleware.proxy_fix import ProxyFix
import os
import controller

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

    if os.path.exists("./books"):
        dirs = [name for name in os.listdir("./books")]
    else:
        dirs = []
    return render_template("home.html", books=dirs)

@app.route('/books/<filename>/book.txt')
def download_txt(filename):
    if not os.path.isfile('books/' + filename + '/book.txt'):
        return render_template('redirect.html')
    else:
        return send_from_directory('books/' + filename, 'book.txt')

@app.route('/books/<filename>/book.pdf')
def download_pdf(filename):
    if not os.path.isfile('books/' + filename + '/book.pdf'):
        os.system('pandoc -o books/' + filename.replace(' ', '\\ ') + '/book.pdf books/' + filename.replace(' ', '\\ ') + '/book.txt')
    return send_from_directory('books/' + filename, 'book.pdf')

@app.route('/books/<filename>/book.epub')
def download_epub(filename):
    if not os.path.isfile('books/' + filename + '/book.epub'):
        os.system('pandoc --metadata title=' + filename.replace(' ', '\\ ') + ' -o books/' + filename.replace(' ', '\\ ') + '/book.epub books/' + filename.replace(' ', '\\ ') + '/book.txt')
    return send_from_directory('books/' + filename, 'book.epub')

@app.route('/system/scan/start', methods=['GET','POST'])
def begin_scan():
    if request.method == 'POST':
        scan = controller.scan()
        return str(scan), 204
    else:
        return redirect('/', 307)

@app.route('/system/getVolume', methods=['GET'])
def get_volume():
   volume = 20 
   return str(volume)

@app.route('/system/setVolume/<val>', methods=['GET', 'POST'])
def set_volume(val):
    if request.method == 'POST':
        volume = int(val) / 100
        return str(controller.set_volume(volume))
    else:
        return redirect('/', 307)
