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
    rate = Rate(10)
    w_rgb = Window("RGB")
    
    # INIT ACTIONS
    # If any actions are to be performed here before the main loop,
    # uncomment the sleep below. (It is necessary to avoid exceptions.)
    rate.sleep()
    # turtle.play_sound()
    button_1()
    
    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        w_rgb.show(rgb)


turtle = None
if __name__ == '__main__':
    turtle = Turtle(rgb=True, pc=True, depth=True)
    turtle.register_button_cb(0, button_0)
    turtle.register_button_cb(1, button_1)
    turtle.register_button_cb(2, button_2)
    main()
