from flask import Flask, request, send_file, render_template, redirect
import os
import subprocess
import time
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'aac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            output_filename = os.path.splitext(filename)[0] + '_16bit.wav'
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            subprocess.run(['ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-y',output_path], check=True)
            delayed_delete(input_path)
            delayed_delete(output_path)
            return send_file(output_path, as_attachment=True)
    return render_template('upload.html')

def delayed_delete(file_path, delay=10):
    def task():
        try:
            time.sleep(delay)
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    threading.Thread(target=task).start()

if __name__ == '__main__':
    app.run(debug=True, port=8001, host='0.0.0.0')