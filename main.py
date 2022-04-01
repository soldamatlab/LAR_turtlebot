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


# TODO remove
def button_1():
    segments = turtle.get_segments()


def main():
    rate = Rate(10)
    
    # INIT ACTIONS
    # (the sleep is necessary to avoid errors
    # if any actions are to be performed before the main loop)
    # rate.sleep()
    
    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        # hsv = rgb_to_hsv(rgb)
        # bin_img = bin_to_rgb(img_threshold(hsv))
        w_rgb.show(rgb)
        # w_bool.show(bin_img)


if __name__ == '__main__':
    main()
