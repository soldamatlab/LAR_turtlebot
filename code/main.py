from __future__ import print_function
from robolab_turtlebot import Rate
from turtle import Turtle
import numpy as np
import cv2
from camera import *
from dance import dance
from color_harvest import *
from driver import Driver
import CONST

turtle = None
driver = None


def button_0():
    main()

def button_1():
    segments = turtle.get_segments(driver.color, min_area=200)
    pc = turtle.get_point_cloud()
    segments.calculate_coors(pc)
    segments.print_all()
    print(segments.coors)

def button_2():
    turtle.get_segments(CONST.GREEN, info=True)

def bumper():
    print("BUMPER")


if __name__ == '__main__':
    rate = Rate(CONST.RATE)

    turtle = Turtle(rgb=True, pc=True, depth=True)
    turtle.register_button_cb(0, button_0)
    turtle.register_button_cb(1, button_1)
    turtle.register_button_cb(2, button_2)
    turtle.register_bumper_cb("ALL", bumper)
    turtle.bot.wait_for_odometry()
    turtle.reset_odometry()

    driver = Driver(turtle)

    # w_rgb = Window("RGB")
    # w_bin = Window("BIN")

    # INIT ACTIONS
    # rate.sleep()
    # turtle.play_sound()


def main():
    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()
        driver.drive()
