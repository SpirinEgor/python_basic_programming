import json
import cv2
import matplotlib.pyplot as plt
import os
import base64

from flask import Flask, g, request, send_from_directory
from flask_cors import CORS


def show_image(image):
    plt.axis("off")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.show()


this_app = Flask(__name__)
CORS(this_app)


@this_app.route('/')
def return_html():
    return send_from_directory('client', 'index.html')


@this_app.route('/js')
def return_js():
    return send_from_directory('client', "data_worker.js")


@this_app.route('/handle_img', methods=['POST'])
def handle_img():
    if 'image' not in request.files:
        resp = json.dumps({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    img_file = request.files.getlist('image')[0]
    filename = img_file.filename
    path = os.path.join("uploaded_images", filename)
    img_file.save(path)
    exec(open("./obj_detection_yolo/object_detection_yolo.py").read(),
         {"args": {"image": path}})
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    os.remove(path)
    return json.dumps({'success': True, 'image': encoded_string.decode('utf-8')}), 200, {
        'ContentType': 'application/json'}


if __name__ == '__main__':
    this_app.run()
