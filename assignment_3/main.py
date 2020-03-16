import numpy as np
import cv2

image_a = cv2.imread('sample_image.jpg')
(image_h, image_w, _) = image_a.shape

image_b = cv2.Canny(image_a, 200, 400)
image_b.resize(image_h, image_w, 1)
image_b = np.tile(image_b, (1, 1, 3))
image_b = cv2.resize(image_b, None, fx=0.5, fy=0.5)

image_c = cv2.blur(image_a, (7, 7))
image_c = cv2.resize(image_c, None, fx=0.25, fy=0.25)

image_d = cv2.GaussianBlur(image_a, (7, 7), 0)
image_d = cv2.resize(image_d, None, fx=0.25, fy=0.25)

K = np.random.randint(0, 100, (7, 7))
K = K / K.sum()
image_e = cv2.filter2D(image_a, -1, K)
image_e = cv2.resize(image_e, None, fx=0.25, fy=0.25)

image_f = np.random.randint(0, 255, (image_h // 4, image_w // 4, 3))

res_image = np.zeros((image_h, image_w // 2 * 3, 3), np.uint8)
res_image[:, : image_w] = image_a
res_image[: image_h // 2, image_w:] = image_b
res_image[image_h // 2: image_h // 4 * 3, image_w: image_w // 4 * 5] = image_c
res_image[image_h // 2: image_h // 4 * 3, image_w // 4 * 5:] = image_d
res_image[image_h // 4 * 3:, image_w: image_w // 4 * 5] = image_e
res_image[image_h // 4 * 3:, image_w // 4 * 5:] = image_f

cv2.imwrite('res.jpg', res_image)
