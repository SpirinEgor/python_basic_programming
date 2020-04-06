import os
import cv2
import numpy as np
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def change_file(filename):
    proto_file = "./models/colorization_deploy_v2.prototxt"
    weights_file = "./models/colorization_release_v2.caffemodel"
    frame = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    W_in = 224
    H_in = 224
    net = cv2.dnn.readNetFromCaffe(proto_file, weights_file)
    pts_in_hull = np.load('./pts_in_hull.npy')
    pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [pts_in_hull.astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313],
                                                          2.606, np.float32)]
    img_rgb = (frame[:, :, [2, 1, 0]] * 1.0 / 255).astype(np.float32)
    img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2Lab)
    img_l = img_lab[:, :, 0]
    img_l_rs = cv2.resize(img_l, (W_in, H_in))
    img_l_rs -= 50
    net.setInput(cv2.dnn.blobFromImage(img_l_rs))
    ab_dec = net.forward()[0, :, :, :].transpose((1, 2, 0))
    (H_orig, W_orig) = img_rgb.shape[:2]
    ab_dec_us = cv2.resize(ab_dec, (W_orig, H_orig))
    img_lab_out = np.concatenate((img_l[:, :, np.newaxis], ab_dec_us), axis=2)
    img_bgr_out = np.clip(cv2.cvtColor(img_lab_out, cv2.COLOR_Lab2BGR), 0, 1)
    res_image = np.zeros((H_orig, W_orig * 2, 3), np.uint8)
    res_image[:, : W_orig] = frame
    res_image[:, W_orig:] = img_bgr_out*255
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), res_image)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            change_file(filename)
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
    if (not os.path.exists('models/colorization_deploy_v2.prototxt') or
            not os.path.exists('models/colorization_deploy_v2.prototxt') or
            not os.path.exists('pts_in_hull.npy')):
        os.system('sudo chmod a+x getModels.sh')
        os.system('./getModels.sh')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run()
