import cv2
import numpy as np
import random

imgA = cv2.imread('img.jpg')
height = imgA.shape[0]
width = imgA.shape[1]
imgB = cv2.resize(imgA, (width // 2, height // 2))
imgC = cv2.resize(imgA, (width // 4, height // 4))
imgD = cv2.resize(imgA, (width // 4, height // 4))
imgE = cv2.resize(imgA, (width // 4, height // 4))
imgF = cv2.resize(imgA, (width // 4, height // 4))
canny = cv2.Canny(imgB, 100, 200)
imgB = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
imgC = cv2.blur(imgC, (5, 5))
imgD = cv2.GaussianBlur(imgD, (5,5), 0)
kernel = np.array([[-1,  2, -3],
                   [ 4, -5,  6],
                   [-7,  8, -9]])
imgE = cv2.filter2D(imgE, -1, kernel)
for i in range(0, height // 4):
    for j in range(0, width // 4):
        imgF[i][j] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

imgFinal = np.zeros((height, width + width // 2, 3), dtype=np.uint8)
imgFinal[0:height, 0:width] = imgA
imgFinal[0:height // 2, width:width + width // 2] = imgB
imgFinal[height // 2:height // 2 + height // 4, width:width + width // 4] = imgC
imgFinal[height // 2:height // 2 + height // 4, width + width // 4:width + width // 2] = imgD
imgFinal[height // 2 + height // 4:height, width:width + width // 4] = imgE
imgFinal[height // 2 + height // 4:height, width + width // 4:width + width // 2] = imgF
cv2.imwrite('result.jpg', imgFinal)
