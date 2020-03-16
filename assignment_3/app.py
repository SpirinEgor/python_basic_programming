import numpy as np
import cv2

image = cv2.imread('image.jpg')
(image_h, image_w, _) = image.shape

res_image = np.zeros((image_h, image_w // 2 * 3, 3), np.uint8)
res_image[:, : image_w] = image

image2 = cv2.Canny(image, 200, 400)
image2.resize(image_h, image_w, 1)
image2 = np.tile(image2, (1, 1, 3))
image2 = cv2.resize(image2, None, fx=0.5, fy=0.5)
res_image[: image_h // 2, image_w :] = image2

image3 = cv2.blur(image, (7, 7))
image3 = cv2.resize(image3, None, fx=0.25, fy=0.25)
res_image[image_h // 2 : image_h // 4 * 3, image_w : image_w // 4 * 5] = image3

image4 = cv2.GaussianBlur(image, (7, 7), 0)
image4 = cv2.resize(image4, None, fx=0.25, fy=0.25)
res_image[image_h // 2 : image_h // 4 * 3, image_w // 4 * 5 :] = image4

K = np.random.randint(0, 100, (7, 7))
K = K / K.sum()
image5 = cv2.filter2D(image, -1, K)
image5 = cv2.resize(image5, None, fx=0.25, fy=0.25)
res_image[image_h // 4 * 3 :, image_w : image_w // 4 * 5] = image5

image6 = np.random.randint(0, 255, (image_h // 4, image_w // 4, 3))
res_image[image_h // 4 * 3 :, image_w // 4 * 5 :] = image6

cv2.imshow('res_image', res_image)
k = cv2.waitKey(0)
cv2.imwrite('res_image.jpg', res_image)
cv2.destroyAllWindows()
