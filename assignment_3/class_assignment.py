import numpy as np
import cv2
import random 

imgA = cv2.imread('image.jpg')
rows, cols, channels = imgA.shape
imgB = cv2.resize(imgA, (cols // 2, rows // 2))
img_25 = cv2.resize(imgA, (cols // 4, rows // 4))

edges = cv2.Canny(imgB, 100, 200)
imgB = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

imgC = cv2.blur(img_25, (10, 10))

imgD = cv2.GaussianBlur(img_25, (5, 5), 0)

kernel = np.array([[-1, -1, 0], [-1, 4, -2], [0, -1, -1]])
imgE = cv2.filter2D(img_25, -1, kernel)

imgF = np.random.randint(0, 255, (rows // 4, cols // 4, 3))

res_img = np.zeros((rows, cols // 2 * 3, 3), np.uint8)
res_img[:, : cols] = imgA
res_img[: rows // 2, cols :] = imgB
res_img[rows // 2 : rows // 4 * 3, cols : cols // 4 * 5] = imgC
res_img[rows // 2 : rows // 4 * 3, cols // 4 * 5 :] = imgD
res_img[rows // 4 * 3 :, cols : cols // 4 * 5] = imgE
res_img[rows // 4 * 3 :, cols // 4 * 5 :] = imgF

cv2.imshow('image', res_img)
k = cv2.waitKey(0)
if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'): # wait for 's' key to save and exit
    cv2.imwrite('new_name.png', res_img)
    cv2.destroyAllWindows()
