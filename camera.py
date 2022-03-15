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
    def __init__(self, count, params, centroids):
        self.count = count
        self.params = params
        self.centroids = centroids

    def remove(self, index):
        self.count -= 1
        self.params.delete(index)
        self.centroids.delete(index)

    def print(self, index):
        print("left: " + self.params[index][0] + ", top: " + self.params[index][1])
        print("size: " + self.params[index][2] + " x " + self.params[index][3])
        print("area: " + self.params[index][4])
        print("center " + self.centroids[index])

    def print_all(self):
        for i in range(self.count):
            print("segment " + i)
            self.print(i)
            print("")


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

    count = 0
    params = []
    centroids = []
    for i in range(count):
        if out[2][i][4] > min_area:
            count += 1
            params.append(out[2][i])
            centroids.append(out[3][i])

    return Segments(count, params, centroids)


def hw_ratio_filter(segments, target=1, max_diff=0.2):
    rm_indices = []
    for i in range(segments.count):
        ratio = float(segments.params[i][3]) / float(segments.params[i][2])
        if abs(ratio - target) > max_diff:
            rm_indices.append(i)

    for i in reversed(rm_indices):
        segments.remove(i)

    return segments
