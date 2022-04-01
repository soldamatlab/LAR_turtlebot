from __future__ import print_function
from robolab_turtlebot import Rate
from turtle import Turtle
import numpy as np
import cv2
from camera import *
from dance import dance

def button_0():
    dance()

def button_1():
    segments = turtle.get_segments()

def button_2():
    return None


def main():
    turtle = Turtle(rgb=True, pc=True, depth=True)
    turtle.register_button_cb(0, button_0)
    turtle.register_button_cb(1, button_1)
    turtle.register_button_cb(2, button_2)
    rate = Rate(10)

    w_rgb = Window("RGB")
    
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
