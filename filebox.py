#!/usr/bin/env python3.7
from pathlib import Path
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = Path("box")
# FIXME substitute "box" with either complete or relative file path that works for you
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    'txt',
    'pdf',
    'png',
    'jpg',
    'jpeg',
    'gif'
    }
# FIXME revise allowed extensions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
# FIXME change your secret_key. It can be any string (or maybe even something else)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and Path(file.filename).suffix.strip('.') in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            full_dir_path = app.config['UPLOAD_FOLDER'] / request.form['path']
            full_dir_path.mkdir(exist_ok=True)
            full_file_path = full_dir_path / filename
            file.save(str(full_file_path))
            flash(f"{full_file_path} uploaded successfully")

    return render_template("index.html.j2",
                            upload_folder=str(app.config['UPLOAD_FOLDER']),
                            existing_dirs=["/".join(d.parts[1:]) for d in app.config['UPLOAD_FOLDER'].rglob('*') if d.is_dir()])


if __name__ == '__main__':
    app.run()
