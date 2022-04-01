from __future__ import print_function
from robolab_turtlebot import Rate
from turtle import Turtle
import numpy as np
import cv2
from camera import *
from dance import dance

turtle = Turtle(rgb=True, pc=True, depth=True)


def button_cb(msg):
    if msg.button == 0:
        dance()
    if msg.button == 1:
        button_1()


def button_1():
    pc = turtle.get_point_cloud()
    print(pc)


def main():
    turtle.register_button_event_cb(button_cb)

    rate = Rate(10)
    # window_rgb = Window("rgb")
    # window_bool = Window("bool")

    button_1() #TODO remove

    while not turtle.bot.is_shutting_down():
        rate.sleep()

        # rgb = turtle.get_rgb_image()
        # hsv = rgb_to_hsv(rgb)
        # bin_img = bin_to_rgb(img_threshold(hsv))
        # window_rgb.show(rgb)
        # window_bool.show(bin_img)


if __name__ == '__main__':
    main()
