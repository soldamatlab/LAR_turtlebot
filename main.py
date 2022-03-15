from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2
from camera import *
import CONST


class Turtle:

    def __init__(self, rgb=True, pc=True, depth=True):
        self.bot = Turtlebot(rgb=rgb, pc=pc, depth=depth)

    def register_button_event_cb(self, cb):
        self.bot.register_button_event_cb(lambda msg: cb() if msg.state == 0 else None)

    def get_rgb_image(self):
        return self.bot.get_rgb_image()

    def get_point_cloud(self):
        return self.bot.get_point_cloud()

    def get_depth_K(self):
        return self.bot.get_depth_K()

    def get_segments(self, min_area, target_ratio, max_ratio_diff):
        rgb = self.get_rgb_image()
        hsv = rgb_to_hsv(rgb)
        bin = img_threshold(hsv)
        segments = segment(bin, min_area=min_area)
        segments = hw_ratio_filter(segments, target=target_ratio, max_diff=max_ratio_diff)
        return segments


turtle = Turtle(rgb=True, pc=True, depth=True)


def button_cb():
    segments = turtle.get_segments(CONST.MIN_AREA, CONST.TARGET_RATIO, CONST.MAX_RATIO_DIFF)
    depth_point_cloud = turtle.get_point_cloud()
    depth_K = turtle.get_depth_K()
    bot_point_cloud = depth_K * depth_point_cloud
    print(bot_point_cloud)


def main():
    turtle.register_button_event_cb(button_cb)

    rate = Rate(10)
    window_rgb = Window("rgb")
    window_bool = Window("bool")
    window_depth = Window("depth")

    while not turtle.bot.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        hsv = rgb_to_hsv(rgb)
        bin_img = bin_to_rgb(img_threshold(hsv))
        window_rgb.show(rgb)
        window_bool.show(bin_img)


if __name__ == '__main__':
    main()
