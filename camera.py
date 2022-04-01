import cv2
import numpy as np
import CONST


class Window:

    def __init__(self, name):
        self.name = name
        cv2.namedWindow(name)

    def show(self, img):
        cv2.imshow(self.name, img)
        cv2.waitKey(1)


class Segments:

    def __init__(self, count, label_mat, label_dict, params, centroids):
        self.count = count # number of segments
        self.label_mat = label_mat # labels of pixels
        self.label_dict = label_dict # label_dict[i] is the label of the i-th segment used in label_mat
        self.params = params # params of each segment: params[i] = [leftest, highest, width, height, area]
        self.centroids = centroids # centroid of each segment
        self.depth = None # median depth of each segment

    def leftest(self, i):
        return self.params[i][0]

    def highest(self, i):
        return self.params[i][1]

    def width(self, i):
        return self.params[i][2]

    def height(self, i):
        return self.params[i][3]

    def area(self, i):
        return self.params[i][4]

    def leftests(self):
        return [self.leftest(i) for i in range(0, self.count)]

    def highests(self):
        return [self.highest(i) for i in range(0, self.count)]

    def widths(self):
        return [self.width(i) for i in range(0, self.count)]

    def heights(self):
        return [self.height(i) for i in range(0, self.count)]

    def areas(self):
        return [self.area(i) for i in range(0, self.count)]

    def remove(self, index):
        self.count -= 1
        self.params.pop(index)
        self.centroids.pop(index)

    def get_bin_img(self, segment):
        bin_mat = np.zeros_like(self.label_mat, dtype=int)
        bin_mat[self.label_mat == self.label_dict[segment]] = 1
        return bin_mat

    def get_depth(self, pc):
        pc_shape = np.shape(pc)
        pixels = pc_shape[0] * pc_shape[1]
        pc = np.reshape(pc, (pixels, pc_shape[2]))

        depth = []
        for i in range(0, self.count):
            bin = self.get_bin_img(i)
            bin = np.reshape(bin, (pixels))
            values = []
            for p in range(0, pixels):
                if bin[p] != 0 and all(not np.isnan(c) for c in pc[p]):
                    values.append(pc[p])
            values = np.stack(values, axis=0)
            depth.append(np.median(values, axis=0))

        self.depth = depth


    def print(self, index):
        print("left: " + str(self.params[index][0]) + ", top: " + str(self.params[index][1]))
        print("size: " + str(self.params[index][2]) + " x " + str(self.params[index][3]))
        print("area: " + str(self.params[index][4]))
        print("center " + str(self.centroids[index]))

    def print_all(self):
        print("ALL SEGMENTS: " + str(self.count) + "\n")
        for i in range(self.count):
            print("segment " + str(i))
            self.print(i)
            print("")


def rgb_to_hsv(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)


def pixel_threshold(hsv_pix, color):
    [target_hue, hue_diff, satur_min, val_min] = CONST.get_color_consts(color)
    hue = abs(hsv_pix[0] - target_hue) < hue_diff
    satur = hsv_pix[1] > satur_min
    val = hsv_pix[2] > val_min
    return hue and satur and val


def img_threshold(hsv, color):
    [target_hue, hue_diff, satur_min, val_min] = CONST.get_color_consts(color)
    hue = get_hue_diff(hsv[:,:,0].astype(int), target_hue) <= hue_diff
    satur = hsv[:,:,1] >= satur_min
    val = hsv[:,:,2] >= val_min
    return hue & satur & val


def get_hue_diff(hue_array, target_hue, info=False):
    diff1 = np.abs(hue_array - target_hue)
    diff2 = np.abs(hue_array - (target_hue + CONST.HUE_MAX))
    return np.minimum(diff1, diff2)


def bin_to_rgb(bin):
    return np.repeat((np.copy(bin) * 255)[:, :, np.newaxis], 3, axis=2).astype(np.uint8)


def segment(bin, min_area=1000, info=False):
    out = cv2.connectedComponentsWithStats(bin.astype(np.uint8))
    if info: print("segment: received " + str(out[0]) + " segments")

    count = 0
    label_mat = out[1]
    label_dict = []
    params = []
    centroids = []

    for i in range(1, out[0]):  # skip first
        area = out[2][i][4]
        if info: print("area " + str(area))
        if area > min_area:
            count += 1
            label_dict.append(i)
            params.append(out[2][i])
            centroids.append(out[3][i])

    if info: print("")
    return Segments(count, label_mat, label_dict, params, centroids)


def hw_ratio_filter(segments, target=CONST.TARGET_RATIO, max_diff=CONST.MAX_RATIO_DIFF, info=False):
    if info: print("hw_ratio_filter: received " + str(segments.count) + " segments")

    rm_indices = []
    for i in range(segments.count):
        ratio = float(segments.params[i][3]) / float(segments.params[i][2])
        if info: print("ratio " + str(ratio))
        if abs(ratio - target) > max_diff:
            rm_indices.append(i)

    for i in reversed(rm_indices):
        segments.remove(i)

    if info: print("")
    return segments


def pc_cam_to_bot(cam_pc, K, l=CONST.DEPTH_CAM_LAMBDA):
    og_shape = np.shape(cam_pc)

    cam_pc = np.reshape(cam_pc, (og_shape[0] * og_shape[1], og_shape[2]))
    cam_z = np.copy(cam_pc[:,2])
    cam_pc[:,2] = 1

    bot_pc = np.matmul(cam_pc, l * np.linalg.inv(K))
    bot_pc[:,2] = cam_z
    bot_pc = np.reshape(bot_pc, og_shape)
    return bot_pc
