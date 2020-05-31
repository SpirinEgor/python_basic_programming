mkdir model
wget https://pjreddie.com/media/files/yolov3.weights -O ./model/yolov3.weights
wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg?raw=true -O ./model/yolov3.cfg
wget https://github.com/pjreddie/darknet/blob/master/data/coco.names?raw=true -O ./model/coco.names
