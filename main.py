from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2
from camera import *
import CONST
from dance import dance


class Turtle:

    def __init__(self, rgb=True, pc=True, depth=True):
        self.bot = Turtlebot(rgb=rgb, pc=pc, depth=depth)

    def register_button_event_cb(self, cb):
        self.bot.register_button_event_cb(cb) # lambda msg: cb() if msg.state == 0 else None

    def get_rgb_image(self):
        return self.bot.get_rgb_image()
    
    def get_hsv_image(self):
        rgb = self.get_rgb_image()
        return rgb_to_hsv(rgb)

    def get_point_cloud(self):
        return self.bot.get_point_cloud()

    def get_depth_K(self):
        return self.bot.get_depth_K()

    def get_segments(self, min_area=CONST.MIN_AREA, target_ratio=CONST.TARGET_RATIO, max_ratio_diff=CONST.MAX_RATIO_DIFF):
        hsv = self.get_hsv_image()
        bin = img_threshold(hsv)
        segments = segment(bin, min_area=min_area)
        segments = hw_ratio_filter(segments, target=target_ratio, max_diff=max_ratio_diff, info=True)
        return segments


turtle = Turtle(rgb=True, pc=True, depth=True)


def button_cb(msg):
    if msg.state == 1: # PRESSED
        if msg.button == 0:
            sticks = turtle.get_segments()
            sticks.print_all()

            if sticks.count > 0:
                params = sticks.params[0]
                hsv = turtle.get_hsv_image()
                center_color = str(hsv[int(params[0]) + int(params[2]/2), int(params[1]) + int(params[3]/2)])
                print("Centroid 0 hsv color: " + str(center_color))


        if msg.button == 1:
            dance()

    # depth_point_cloud = turtle.get_point_cloud()
    # depth_K = turtle.get_depth_K()
    # bot_point_cloud = recalculate_coordinates(depth_point_cloud, depth_K)
    # print(bot_point_cloud)


def main():
    turtle.register_button_event_cb(button_cb)

    rate = Rate(10)
    window_rgb = Window("rgb")
    window_bool = Window("bool")

    while not turtle.bot.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        hsv = rgb_to_hsv(rgb)
        bin_img = bin_to_rgb(img_threshold(hsv))
        window_rgb.show(rgb)
        window_bool.show(bin_img)


if __name__ == '__main__':
    main()
