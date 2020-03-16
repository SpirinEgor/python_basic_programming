import cv2 as cv
import numpy as np
from random import randint as rand

im_folder = 'images\\'


def read_images():
    # 800x600 (source img)
    a_img = cv.imread(im_folder + 'COVID-19.jpg')

    # 400x300
    b_img = cv.resize(a_img, (a_img.shape[1] // 2, a_img.shape[0] // 2))

    # 200x150
    c_img = cv.resize(a_img, (a_img.shape[1] // 4, a_img.shape[0] // 4))
    d_img = cv.resize(a_img, (a_img.shape[1] // 4, a_img.shape[0] // 4))
    e_img = cv.resize(a_img, (a_img.shape[1] // 4, a_img.shape[0] // 4))
    f_img = cv.resize(a_img, (a_img.shape[1] // 4, a_img.shape[0] // 4))

    return a_img, b_img, c_img, d_img, e_img, f_img


def apply_canny(image):
    edges = cv.Canny(image, 100, 200)
    image = cv.cvtColor(edges, cv.COLOR_GRAY2BGR)
    return image


def apply_averaging(image):
    return cv.blur(image, (15, 15))


def apply_gauss(image):
    return cv.GaussianBlur(image, (5, 5), 0)


def apply_custom(image):
    kernel = np.array([[-1, -1, -1],
                       [2, 4, 2],
                       [-1, -1, -1]])
    return cv.filter2D(image, -1, kernel)


def apply_random(image):
    result = image
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            result[y, x] = [rand(0, 255), rand(0, 255), rand(0, 255)]
    return result


def get_modified_images():
    a_img, b_img, c_img, d_img, e_img, f_img = read_images()
    b_img = apply_canny(b_img)
    c_img = apply_averaging(c_img)
    d_img = apply_gauss(d_img)
    e_img = apply_custom(e_img)
    f_img = apply_random(f_img)
    return a_img, b_img, c_img, d_img, e_img, f_img


def create_image():
    a_img, b_img, c_img, d_img, e_img, f_img = get_modified_images()

    # final image heigth is equal to source image heigth
    total_height = a_img.shape[0]
    # but width is 1.5 times larger
    total_width = a_img.shape[1] + a_img.shape[1] // 2

    final_img = np.zeros((total_height, total_width, 3), dtype=np.uint8)

    def put_on_final_img(image, x, y):
        final_img[y:image.shape[0] + y, x:image.shape[1] + x] = image

    current_y = 0
    current_x = 0

    # init image A
    put_on_final_img(a_img, current_x, current_y)

    # concat with image B
    current_x = a_img.shape[1]
    put_on_final_img(b_img, current_x, current_y)

    # concat with image C
    current_y = b_img.shape[0]
    put_on_final_img(c_img, current_x, current_y)

    # concat with image D
    current_x = a_img.shape[1] + c_img.shape[1]
    put_on_final_img(c_img, current_x, current_y)

    # concat with image E
    current_x = a_img.shape[1]
    current_y = b_img.shape[0] + c_img.shape[0]
    put_on_final_img(e_img, current_x, current_y)

    # concat with image F
    current_x = a_img.shape[1] + c_img.shape[1]
    put_on_final_img(f_img, current_x, current_y)

    cv.imwrite(im_folder + 'result.jpg', final_img)


create_image()
