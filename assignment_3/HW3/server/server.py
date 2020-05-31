import json
import requests
import numpy as np
import cv2 as cv
import os.path
import sys


from flask import Flask, g, redirect, request, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

confidence_threshold = 0.5
nms_threshold = 0.4
input_width = 416
input_height = 416


@app.route('/image', methods=['POST'])
def show_image():
    image = request.files['image']
    filename = secure_filename(image.filename)
    print(filename)
    image.save(filename)
    object_detection(filename)
    print('Done !!!')
    return '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <link rel="stylesheet" href="style.css">
                <title>Basic client</title>
            </head>
            <body>
                <div id="Show">
                    <img id="Before" src=''' + filename + '''>
                    <img id="After" src=''' + filename[:-4] + '_processed.jpg'+'''>
                </div>
            </body>
        </html>
        '''


def get_outputs_names(net):
    layers_names = net.getLayerNames()
    return [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


def draw_predicted(classes, frame, class_id, conf, left, top, right, bottom):
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

    label = '%.2f' % conf
    if classes:
        assert(class_id < len(classes))
        label = '%s:%s' % (classes[class_id], label)

    label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, label_size[1])
    cv.rectangle(frame, (left, top - round(1.5*label_size[1])), (left + round(1.5*label_size[0]), top + base_line), (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)


def postprocess(classes, frame, outs):
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold:
                center_x = int(detection[0] * frame_width)
                center_y = int(detection[1] * frame_height)
                width = int(detection[2] * frame_width)
                height = int(detection[3] * frame_height)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    indices = cv.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        draw_predicted(classes, frame, class_ids[i], confidences[i], left, top, left + width, top + height)


def object_detection(filename):
    classes_file = "model/coco.names"
    classes = None
    with open(classes_file, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    model_configuration = "model/yolov3.cfg"
    model_weights = "model/yolov3.weights"

    net = cv.dnn.readNetFromDarknet(model_configuration, model_weights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    window_name = 'Deep learning object detection in OpenCV'
    cv.namedWindow(window_name, cv.WINDOW_NORMAL)

    if not os.path.isfile(filename):
        print("Input image file ", filename, " doesn't exist")
        sys.exit(1)

    cap = cv.VideoCapture(filename)
    output_file = filename[:-4]+'_processed.jpg'

    _, frame = cap.read()

    blob = cv.dnn.blobFromImage(frame, 1/255, (input_width, input_height), [0, 0, 0], 1, crop=False)
    net.setInput(blob)

    outs = net.forward(get_outputs_names(net))
    postprocess(classes, frame, outs)
    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
    cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    cv.imwrite(output_file, frame.astype(np.uint8))


@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory('', filename)


if __name__ == '__main__':
    if (not os.path.exists('model/coco.names') or
            not os.path.exists('model/yolov3.cfg') or
            not os.path.exists('model/yolov3.weights')):
        os.system('sudo chmod a+x getModels.sh')
        os.system('getModels.sh')
    app.run()
