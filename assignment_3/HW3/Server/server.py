import requests
import numpy as np
import cv2 as cv
import os.path


from flask import Flask, g, redirect, request, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

classesFile = "coco.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

confThreshold = 0.5
nmsThreshold = 0.4
inpWidth = 416
inpHeight = 416

modelConfiguration = "yolov3.cfg"
modelWeights = "yolov3.weights"

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)


def get_outputs_names(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


def draw_pred(classId, conf, left, top, right, bottom, frame):
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
    label = '%.2f' % conf
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)


def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        draw_pred(classIds[i], confidences[i], left, top, left + width, top + height, frame)


def detection(filename):
    if not os.path.isfile(filename):
        print("Input image file ", filename, " doesn't exist")
        sys.exit(1)
    cap = cv.VideoCapture(filename)
    outputFile = filename[:-4]+'_detected.jpg'

    has_frame, frame = cap.read()
    blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    outs = net.forward(get_outputs_names(net))
    postprocess(frame, outs)
    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
    cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    cv.imwrite(outputFile, frame.astype(np.uint8))


@app.route('/image', methods=['POST'])
def image():
    image = request.files['image']
    filename = secure_filename(image.filename)
    print(filename)
    image.save(filename)
    detection(filename)
    print('Done !!!')
    return '''
    <!DOCTYPE html>
    <head>
        <title>Basic client</title>
    </head>
    <body>
    <div id="Show">
        <img id="Before" src='''+filename+'''>
        <img id="After" src='''+filename[:-4]+'_detected.jpg'+'''>
    </div>
    </body>
    </html>
    '''


@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory('', filename)


if __name__ == '__main__':
    if (not os.path.exists('coco.names') or
            not os.path.exists('yolov3.cfg') or
            not os.path.exists('yolov3.weights')):
        os.system('sudo chmod a+x getModels.sh')
        os.system('getModels.sh')
    app.run()
