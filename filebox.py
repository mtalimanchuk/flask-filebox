#!/usr/bin/env python3.7
import logging
from pathlib import Path

from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, SECRET_KEY

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config['UPLOAD_FOLDER'] = Path(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Select the file to upload', 'action-fail')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Empty filename', 'action-fail')
            return redirect(request.url)
        file_extension = Path(file.filename).suffix.strip('.')
        if file and file_extension in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            full_dir_path = app.config['UPLOAD_FOLDER'] / request.form['path']
            full_dir_path.mkdir(exist_ok=True)
            full_file_path = full_dir_path / filename
            file.save(str(full_file_path))
            app.logger.info(f"Uploaded {full_file_path}")
            flash(f"{full_file_path} uploaded successfully", 'action-success')
        else:
            flash(f"{file_extension} files are not allowed", 'action-fail')
            return redirect(request.url)

    return render_template("index.html.j2",
                            upload_folder=str(app.config['UPLOAD_FOLDER']),
                            existing_dirs=["/".join(d.parts[1:]) for d in app.config['UPLOAD_FOLDER'].rglob('*') if d.is_dir()])


if __name__ == '__main__':
    app.run()
