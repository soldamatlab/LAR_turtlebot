import cv2
import numpy as np


GREEN = 65
HUE_DIFF = 15
SATUR_MIN = 100
VAL_MIN = 70


class Window:

    def __init__(self, name):
        self.name = name
        cv2.namedWindow(name)

    def show(self, img):
        cv2.imshow(self.name, img)
        cv2.waitKey(1)


class Segments:

    # params = [leftest, highest, width, height, area]
    def __init__(self, seg_count, params, centroids):
        self.seg_count = seg_count
        # self.labels = labels
        self.params = params
        self.centroids = centroids


def rgb_to_hsv(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)


def pixel_threshold(hsv_pix):
    hue = abs(hsv_pix[0] - GREEN) < HUE_DIFF
    satur = hsv_pix[1] > SATUR_MIN
    val = hsv_pix[2] > VAL_MIN
    return hue and satur and val


def img_threshold(hsv):
    hue = np.abs(hsv[:,:,0].astype(int) - GREEN) < HUE_DIFF
    satur = hsv[:,:,1] > SATUR_MIN
    val = hsv[:,:,2] > VAL_MIN
    return hue & satur & val


def bool_to_rgb(bin):
    return np.repeat((np.copy(bin) * 255)[:, :, np.newaxis], 3, axis=2).astype(np.uint8)


def segment(bin, min_area=60):
    out = cv2.connectedComponentsWithStats(bin.astype(np.uint8))
    for i in range(out[0]):
        if out[2][4][i] < min_area:
            out[0] -= 1
            out[2].pop(i)
            out[3].pop(i)
    return Segments(out[0], out[2], out[3])
