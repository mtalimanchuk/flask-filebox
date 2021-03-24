#!/usr/bin/env python3.7
import io
import logging
from pathlib import Path
import tarfile
import zipfile

from flask import Flask, flash, request, redirect, render_template, jsonify, send_file, Response
from werkzeug.utils import secure_filename

from config import SECRET_KEY

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 5000


def get_arguments():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--ip', dest='ip', default=DEFAULT_IP, help='IP address to bind to. Default is ' + DEFAULT_IP)
    parser.add_argument('--port', dest='port', default=DEFAULT_PORT,
                        help='TCP Port to bind to. Default is ' + str(DEFAULT_PORT))
    options = parser.parse_args()

    return options


options = get_arguments()

ip = options.ip
port = int(options.port)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['LAST_USED_DIR'] = None


def _add_to_archive(add_f: callable, path: Path):
    arcname_offset = len(path.parents)
    if path.is_dir():
        for f_name in path.glob("**/*"):
            add_f(f_name, Path(*f_name.parts[arcname_offset:]))
    else:
        add_f(path, Path(*path.parts[arcname_offset:]))


def _make_zip(path):
    path = Path(path)
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        _add_to_archive(z.write, path)
    data.seek(0)

    return data, 'application/zip', f'{path.stem}.zip'


def _make_tar(path):
    path = Path(path)
    data = io.BytesIO()
    with tarfile.TarFile(fileobj=data, mode='w') as tar:
        _add_to_archive(tar.add, path)
    data.seek(0)

    return data, 'application/tar', f'{path.stem}.tar.gz'


def serve_file(path, ftype):
    if ftype == "zip":
        data, mimetype, fname = _make_zip(path)
    elif ftype == "tar":
        data, mimetype, fname = _make_tar(path)
    else:
        raise ValueError(f"Wrong file type {ftype}")

    return data, mimetype, fname


def save_file(files, save_dir):
    if 'file' not in request.files:
        raise FileNotFoundError('Select the file to upload')

    file = request.files['file']

    if file.filename == '':
        raise ValueError('Empty filename')

    if not file:
        raise ValueError('Empty file')

    filename = secure_filename(file.filename)

    upload_dir_path = Path(save_dir).absolute()
    upload_dir_path.mkdir(parents=True, exist_ok=True)

    full_file_path = upload_dir_path / filename
    file.save(str(full_file_path))

    app.config['LAST_USED_DIR'] = str(upload_dir_path)
    app.logger.info(f"Uploaded {full_file_path}")

    return full_file_path


def dir_info(path):
    path = Path(path).absolute()
    dir_exists = False
    breadcrumbs = []
    content = []

    for i, part in enumerate(path.parts):
        p = Path(*path.parts[:i + 1])
        item = {
            "name": part,
            "absolute": str(p.absolute()),
        }
        breadcrumbs.append(item)

    if path.is_dir():
        dir_exists = True
        for c in path.glob("*"):
            item = {
                "name": c.name,
                "absolute": str(c.absolute()),
                "is_dir": c.is_dir(),
            }
            content.append(item)

    response = {
        "exists": dir_exists,
        "breadcrumbs": breadcrumbs,
        "parent": str(path.parent),
        "content": content,
    }

    return response


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        app.logger.info(request.files)
        try:
            files = request.files
            save_dir = request.form['path']
            full_file_path = save_file(files, save_dir)
            flash(f"{full_file_path} uploaded successfully", 'action-success')
        except (FileNotFoundError, ValueError) as e:
            flash(str(e), 'action-fail')

        return redirect(request.url)

    return render_template("index.html", last_used_dir=app.config['LAST_USED_DIR'])


@app.route('/api/path', methods=["POST"])
def resolve_path():
    path = request.json

    response = dir_info(path)

    return jsonify(response)


@app.route('/api/download', methods=['GET'])
def download():
    try:
        path = request.args["path"]
        ftype = request.args["ftype"]

        data, mimetype, fname = serve_file(path, ftype)
        return send_file(
            data,
            mimetype=mimetype,
            as_attachment=True,
            attachment_filename=fname
        )
    except KeyError as e:
        return Response(str(e), status=404)
    except ValueError as e:
        return Response(str(e), status=404)


if __name__ == '__main__':
    app.run(host=ip, port=port)
