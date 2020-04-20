import numpy as np
import cv2 as cv
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# from flask documentation
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            colorize_image(filename)
            return redirect(url_for('uploaded_file',
                                    filename='colorized_' + filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def colorize_image(filename):
    frame = cv.imread(app.config['UPLOAD_FOLDER'] + '/' + filename)

    proto_file = "./models/colorization_deploy_v2.prototxt"
    weights_file = "./models/colorization_release_v2.caffemodel"

    pts_in_hull = np.load('./pts_in_hull.npy')

    net = cv.dnn.readNetFromCaffe(proto_file, weights_file)

    pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [pts_in_hull
                                                       .astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313],
                                                          2.606, np.float32)]

    weight_in = 224
    height_in = 224

    img_rgb = (frame[:, :, [2, 1, 0]] * 1.0 / 255).astype(np.float32)
    img_lab = cv.cvtColor(img_rgb, cv.COLOR_RGB2Lab)
    img_l = img_lab[:, :, 0]

    img_l_rs = cv.resize(img_l, (weight_in, height_in))
    img_l_rs -= 50

    net.setInput(cv.dnn.blobFromImage(img_l_rs))
    ab_dec = net.forward()[0, :, :, :].transpose((1, 2, 0))

    (height_orig, weight_orig) = img_rgb.shape[:2]
    ab_dec_us = cv.resize(ab_dec, (weight_orig, height_orig))
    img_lab_out = np.concatenate((img_l[:, :, np.newaxis], ab_dec_us), axis=2)
    img_bgr_out = np.clip(cv.cvtColor(img_lab_out, cv.COLOR_Lab2BGR), 0, 1)

    outputFile = 'colorized_' + filename
    cv.imwrite(app.config['UPLOAD_FOLDER'] + '/' + outputFile,
               (img_bgr_out*255).astype(np.uint8))


def check_upload_dir():
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(app.config['UPLOAD_FOLDER'])


def check_model_dir():
    if not os.path.exists('models'):
        os.system('sudo chmod a+x getModels.sh')
        os.system('./getModels.sh')


if __name__ == '__main__':
    check_upload_dir()
    check_model_dir()
    app.run()

