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
    print(segments.count)
    print(segments.depth)

def button_2():
    arr = []
    arr.append(np.array([0,0,0])
    arr.append(np.array([1,2,3]))
    arr.append(np.array([5,5,5]))
    print(np.median(arr, axis=0))


def main():
    rate = Rate(10)
    w_rgb = Window("RGB")
    w_bin = Window("BIN")
    
    # INIT ACTIONS
    # If any actions are to be performed here before the main loop,
    # uncomment the sleep below. (It is necessary to avoid exceptions.)
    rate.sleep()
    # turtle.play_sound()
    button_2()
    
    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()

        img_rgb = turtle.get_rgb_image()
        img_hsv = rgb_to_hsv(img_rgb)
        img_bin = img_threshold(img_hsv)
        w_rgb.show(img_rgb)
        w_bin.show(bin_to_rgb(img_bin))


turtle = None
if __name__ == '__main__':
    turtle = Turtle(rgb=True, pc=True, depth=True)
    turtle.register_button_cb(0, button_0)
    turtle.register_button_cb(1, button_1)
    turtle.register_button_cb(2, button_2)
    main()
