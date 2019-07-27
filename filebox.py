#!/usr/bin/env python3.7
import logging
from pathlib import Path

from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

from config import SECRET_KEY

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['LAST_USED_DIR'] = None


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
        if file:
            filename = secure_filename(file.filename)
            upload_dir_path = Path(request.form['path'])
            upload_dir_path.mkdir(parents=True, exist_ok=True)
            full_file_path = upload_dir_path / filename
            file.save(str(full_file_path))
            app.config['LAST_USED_DIR'] = str(upload_dir_path)
            app.logger.info(f"Uploaded {full_file_path}")
            flash(f"{full_file_path} uploaded successfully", 'action-success')
        else:
            flash(f"No file", 'action-fail')
            return redirect(request.url)

    return render_template("index.html.j2", last_used_dir=app.config['LAST_USED_DIR'])


if __name__ == '__main__':
    app.run()
