#!/usr/bin/env python3.7
from pathlib import Path
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = Path("box")
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    'txt',
    'pdf',
    'png',
    'jpg',
    'jpeg',
    'gif'
    }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and Path(file.filename).suffix.strip('.') in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file.save(str(app.config['UPLOAD_FOLDER'] / filename))
            flash(f"{filename} uploaded successfully")

    return render_template("index.html.j2")


if __name__ == '__main__':
    app.run()
