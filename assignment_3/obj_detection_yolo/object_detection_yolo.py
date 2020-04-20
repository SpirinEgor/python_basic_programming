# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

import cv2 as cv
import sys
import numpy as np
import os.path


# Give the configuration and weight files for the model and load the network using them.

def log_print(s):
    print("!!! ", s, " !!!")
    sys.stdout.flush()


def net_init():
    # Load names of classes
    classes_file = "obj_detection_yolo/coco.names"
    classes = None
    with open(classes_file, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    model_configuration = "obj_detection_yolo/yolov3.cfg"
    model_weights = "obj_detection_yolo/yolov3.weights"
    net = cv.dnn.readNetFromDarknet(model_configuration, model_weights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
    return net, classes


# Get the names of the output layers
def get_outputs_names(net):
    # Get the names of all the layers in the network
    layers_names = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Draw the predicted bounding box
def draw_pred(frame, class_id, conf, left, top, right, bottom, classes):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

    label = '%.2f' % conf

    # Get the label for the class name and its confidence
    if classes:
        assert (class_id < len(classes))
        label = '%s:%s' % (classes[class_id], label)

    # Display the label at the top of the bounding box
    label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, label_size[1])
    cv.rectangle(frame, (left, top - round(1.5 * label_size[1])), (left + round(1.5 * label_size[0]), top + base_line),
                 (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs, classes):
    # Initialize the parameters
    conf_threshold = 0.5  # Confidence threshold
    nms_threshold = 0.4  # Non-maximum suppression threshold

    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * frame_width)
                center_y = int(detection[1] * frame_height)
                width = int(detection[2] * frame_width)
                height = int(detection[3] * frame_height)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        draw_pred(frame, class_ids[i], confidences[i], left, top, left + width, top + height, classes)


# Process inputs
def process_inputs(net, classes, args):
    log_print("Start processing")
    inp_width = 416  # _width of network's input image
    inp_height = 416  # _height of network's input image

    if args.get('image') is not None:
        image = args['image']
        # Open the image file
        if not os.path.isfile(image):
            log_print("Input image file doesn't exist")
            raise Exception("no image")
        log_print("Got image, cv videocapture")
        cap = cv.VideoCapture(image)
        output_file = image

        # get frame from the video
        log_print("getting frame")
        has_frame, frame = cap.read()

        # Stop the program if reached end of video
        if not has_frame:
            log_print("Done processing !!!")
            log_print("Output file is stored as " + output_file)
            # Release device
            cap.release()
        log_print("creating blob")
        # Create a 4D blob from a frame.
        blob = cv.dnn.blobFromImage(frame, 1 / 255, (inp_width, inp_height), [0, 0, 0], 1, crop=False)

        log_print("give input to net")
        # Sets the input to the network
        net.setInput(blob)
        log_print("run net")
        # Runs the forward pass to get output of the output layers
        outs = net.forward(get_outputs_names(net))

        log_print("postprocess")
        # Remove the bounding boxes with low confidence
        postprocess(frame, outs, classes)

        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t)
        # and the timings for each of the layers(in layersTimes)
        t, _ = net.getPerfProfile()
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        log_print("write result to file")
        # Write the frame with the detection boxes
        if args.get('image') is not None:
            cv.imwrite(output_file, frame.astype(np.uint8))
        cap.release()
# cv.imshow(winName, frame)
