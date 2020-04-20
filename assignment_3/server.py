import json
import os
import base64
import logging
import gc

from flask import Flask, g, request, send_from_directory
from flask_cors import CORS
from obj_detection_yolo.object_detection_yolo import *

UPLOAD_FOLDER = 'uploaded_images'

this_app = Flask(__name__)
this_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(this_app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# log_print("loading net...")
# net, classes = net_init()
# log_print("net loaded")


@this_app.route('/')
def return_html():
    return send_from_directory('client', 'index.html')


@this_app.route('/js')
def return_js():
    return send_from_directory('client', "data_worker.js")


@this_app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(this_app.root_path, 'uploaded_images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@this_app.route('/uploaded_images/<filename>')
def return_processed(filename):
    return send_from_directory(this_app.config['UPLOAD_FOLDER'],
                               filename)


@this_app.route('/handle_img', methods=['POST'])
def handle_img():
    gc.collect()
    target = os.path.join(APP_ROOT, 'uploaded_images')

    # create image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    log_print("start")
    if 'image' not in request.files:
        resp = json.dumps({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    img_file = request.files['image']
    log_print("got file")
    filename = img_file.filename
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp"):
        print("File accepted")
    else:
        resp = json.dumps({'message': 'Not accepted extension'})
        resp.status_code = 400
        return resp

    path = "/".join([target, filename])
    print("File saved to to:", path)
    img_file.save(path)
    log_print("saved new")
    net, classes = net_init()
    process_inputs(net, classes, {"image": path})
    log_print("processed")
    # with open(path, "rb") as image_file:
    #    encoded_string = base64.b64encode(image_file.read())
    # log_print("encoded")
    # os.remove(path)
    # log_print("removed old")
    # , 'image': encoded_string.decode('utf-8')
    return json.dumps({'success': True}), 200, {
        'ContentType': 'application/json'}


if __name__ == '__main__':
    this_app.run(debug=True)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    this_app.logger.handlers = gunicorn_logger.handlers
    this_app.logger.setLevel(gunicorn_logger.level)
