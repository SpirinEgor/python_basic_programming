import json
import requests
import numpy as np
import cv2 as cv
import os.path

from flask import Flask, g, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def colorization(image):
    proto_file = "models/colorization_deploy_v2.prototxt"
    weights_file = "models/colorization_release_v2.caffemodel"
    frame = cv.imread(image)
    pts_in_hull = np.load('pts_in_hull.npy')
    net = cv.dnn.readNetFromCaffe(proto_file, weights_file)
    pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [pts_in_hull.astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]
    W_in = 224
    H_in = 224
    img_rgb = (frame[:,:,[2, 1, 0]] * 1.0 / 255).astype(np.float32)
    img_lab = cv.cvtColor(img_rgb, cv.COLOR_RGB2Lab)
    img_l = img_lab[:,:,0]
    img_l_rs = cv.resize(img_l, (W_in, H_in)) #
    img_l_rs -= 50
    net.setInput(cv.dnn.blobFromImage(img_l_rs))
    ab_dec = net.forward()[0,:,:,:].transpose((1,2,0))
    (H_orig,W_orig) = img_rgb.shape[:2]
    ab_dec_us = cv.resize(ab_dec, (W_orig, H_orig))
    img_lab_out = np.concatenate((img_l[:,:,np.newaxis],ab_dec_us),axis=2)
    img_bgr_out = np.clip(cv.cvtColor(img_lab_out, cv.COLOR_Lab2BGR), 0, 1)
    outputFile = image+'_colorized.png'
    cv.imwrite(outputFile, (img_bgr_out*255).astype(np.uint8))
    print('Done !!!')


@app.route('/image', methods=['POST'])
def new_picture():
    user_json = request.get_json()
    image = user_json['image']
    colorization(image)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    if (not os.path.exists('models/colorization_deploy_v2.prototxt') or
            not os.path.exists('models/colorization_deploy_v2.prototxt') or
            not os.path.exists('pts_in_hull.npy')):
        os.system('sudo chmod a+x getModels.sh')
        os.system('./getModels.sh')
    app.run()