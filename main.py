from __future__ import print_function
from robolab_turtlebot import Rate
from turtle import Turtle
import numpy as np
import cv2
from camera import *
from dance import dance
from color_harvest import *
from driver import drive

turtle = None


def button_0():
    dance()

def button_1():
    return None

def button_2():
    return None


def main():
    rate = Rate(10)

    turtle = Turtle(rgb=True, pc=True, depth=True)
    turtle.register_button_cb(0, button_0)
    turtle.register_button_cb(1, button_1)
    turtle.register_button_cb(2, button_2)

    # w_rgb = Window("RGB")
    w_bin = Window("BIN")
    
    # INIT ACTIONS
    # If any actions are to be performed here before the main loop,
    # uncomment the sleep below. (It is necessary to avoid exceptions.)
    # rate.sleep()
    # turtle.play_sound()
    
    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()
        turtle.bot.cmd_velocity(linear=turtle.linear, angular=turtle.angular)

        drive(turtle)

        # Testing
        img_rgb = turtle.get_rgb_image()
        img_hsv = rgb_to_hsv(img_rgb)
        img_bin = img_threshold(img_hsv, CONST.GREEN)
        # w_rgb.show(img_rgb)
        w_bin.show(bin_to_rgb(img_bin))


if __name__ == '__main__':
    main()
