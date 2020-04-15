# ------------------------- BODY MODEL -------------------------
# Downloading body pose COCO model
OPENPOSE_URL="http://posefs1.perception.cs.cmu.edu/OpenPose/models/"

WEIGTHS_URL="http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/coco/pose_iter_440000.caffemodel"
PROTO_URL="https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/master/models/pose/coco/pose_deploy_linevec.prototxt"

# Body (COCO)
COCO_FOLDER=${POSE_FOLDER}"coco/"
wget -c ${WEIGTHS_URL} -P ${COCO_FOLDER}
wget -c ${PROTO_URL} -P ${COCO_FOLDER}