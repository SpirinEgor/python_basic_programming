import os
from flask import Flask, send_file, request, render_template
from cv2 import imdecode, imwrite
from numpy import frombuffer, uint8
from time import time

import human_pose_estimation as hpe

app = Flask(__name__)


@app.route("/")
def main_page():
    return send_file("index.html")


@app.route("/", methods=["POST"])
def image_processing():
    image_storage = request.files["image"]
    image_buffer = image_storage.read()
    image_array = frombuffer(image_buffer, uint8)
    image = imdecode(image_array, 1)
    current_time = time()
    imwrite(f"images/{current_time}_initial_image.jpeg", image)
    for model in ["COCO", "MPI"]:
        key_points = hpe.key_points(image, model)
        pose_pairs = hpe.pose_pairs(model)
        image_with_key_points = hpe.image_with_key_points(image, key_points)
        image_with_skeleton = hpe.image_with_skeleton(
            image, key_points, pose_pairs
        )
        imwrite(
            f"images/{current_time}_image_with_key_points_{model}_model.jpeg",
            image_with_key_points
        )
        imwrite(
            f"images/{current_time}_image_with_skeleton_{model}_model.jpeg",
            image_with_skeleton
        )
    return render_template("result.html", time=current_time)


@app.route("/images/<image_name>")
def get_image(image_name):
    return send_file("images/" + image_name)

if __name__ == "__main__":
    if not os.path.exists("images/"):
        os.system("mkdir images/")
    if not (
            os.path.exists("pose/coco/pose_iter_440000.caffemodel") and
            os.path.exists("pose/mpi/pose_iter_160000.caffemodel")):
        os.system("./getModels.sh")
    app.run()

