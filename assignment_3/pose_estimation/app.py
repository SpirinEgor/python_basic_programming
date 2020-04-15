import os
import cv2
import base64
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def pose_estimate(filename):

    threshold = 0.1
    in_width = 368
    in_height = 368
    n_points = 18
    pose_pairs = [
        [1, 0], [1, 2], [1, 5],
        [2, 3], [3, 4], [5, 6],
        [6, 7], [1, 8], [8, 9],
        [9, 10], [1, 11], [11, 12],
        [12, 13], [0, 14], [0, 15],
        [14, 16], [15, 17]
        ]

    proto_file = "coco/pose_deploy_linevec.prototxt"
    weights_file = "coco/pose_iter_440000.caffemodel"
    net = cv2.dnn.readNetFromCaffe(proto_file, weights_file)
    frame = cv2.imread(filename)

    inp_blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (in_width, in_height),
                                     (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inp_blob)

    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]

    points = []

    for i in range(n_points):
        prob_map = output[0, i, :, :]

        minVal, prob, minLoc, point = cv2.minMaxLoc(prob_map)
        x = (frame.shape[1] * point[0]) / W
        y = (frame.shape[0] * point[1]) / H

        if prob > threshold:
            points.append((int(x), int(y)))
        else:
            points.append(None)

    for pair in pose_pairs:
        partA = pair[0]
        partB = pair[1]
        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2)
            cv2.circle(frame, points[partA], 8, (0, 0, 255),
                       thickness=-1, lineType=cv2.FILLED)

    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), frame)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            pose_estimate(filename)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet"
              href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
              integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
              crossorigin="anonymous">
        <title>Upload new File</title>
    </head>
    <body>
    <div class="container mt-5">
        <form id="form" action="" method=post enctype=multipart/form-data>
            <p><input type=file name=file></p>
            <button type="submit" class="btn btn-primary">Upload</button>
        </form>
    </div>
    </body>
    </html>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run()
