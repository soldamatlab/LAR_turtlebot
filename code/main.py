from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate, get_time
from turtle import Turtle
import numpy as np
import cv2
from camera import *
from dance import dance
from driver_task3 import Driver
import CONST

turtle = None
driver = None
running = False


def button_0():
    global running
    running = not running

def button_1():
    return None

def button_2():
    return None

def bumper():
    global running
    running = False
    turtle.stop()
    print("BUMPER-STOP")


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

    # INIT ACTIONS
    # rate.sleep()
    # turtle.play_sound()

    # MAIN LOOP
    while not turtle.bot.is_shutting_down():
        rate.sleep()
        if running:
            driver.drive()
