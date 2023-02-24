from flask import Flask, redirect, render_template, request, send_file
from markupsafe import escape
#from werkzeug.middleware.proxy_fix import ProxyFix
import os
import controller
import file_converter

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

    if os.path.exists("books/"):
        dirs = [name for name in os.listdir("books")]
    else:
        dirs = []
    voices = controller.get_voices()
    currVoice = controller.get_current_voice()
    voices.remove(currVoice)
    return render_template("home.html", books=dirs, voices=voices, currVoice=currVoice)

@app.route('/books/<filename>/book.txt')
def download_txt(filename):
    if not os.path.isfile('books/' + filename + '/book.txt'):
        return render_template('redirect.html')
    else:
        return send_file('/Users/matthew/uni/year_3/sem2/SDP/VIRTUO/books/' + filename + '/book.txt')

@app.route('/books/<filename>/book.pdf')
def download_pdf(filename):
    file_converter.create_pdf('books/' + filename)
    return send_file('/Users/matthew/uni/year_3/sem2/SDP/VIRTUO/books/' + filename + '/book.pdf')

@app.route('/books/<filename>/book.epub')
def download_epub(filename):
    file_converter.create_epub('books/' + filename)
    return send_file('/Users/matthew/uni/year_3/sem2/SDP/VIRTUO/books/' + filename + '/book.epub')

@app.route('/books/<filename>/book.mp3')
def download_mp3(filename):
    file_converter.create_mp3('books/' + filename)
    return send_file('/Users/matthew/uni/year_3/sem2/SDP/VIRTUO/books/' + filename + '/book.mp3')

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

@app.route('/system/setVoice/<val>', methods=['GET', 'POST'])
def set_voice(val):
    if request.method == 'POST':
        if val in controller.get_voices():
            return str(controller.set_voice(val))
        else:
            return ''
    else:
        return redirect('/', 307)

@app.route('/system/scan/stop', methods=['GET', 'POST'])
def stop_scan():
    if request.method == 'POST':
        return str(controller.stop_scan())
    else:
        return redirect('/', 307)


