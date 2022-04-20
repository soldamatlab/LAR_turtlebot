import CONST
import numpy as np
from camera import *
import time
import math

INFO = False  # TODO
FORWARD_SPEED = 0.2
TURN_SPEED = np.pi/8


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.busy = True
        self.main = ThirdTask(self, self)
        self.counter = 0
        self.color = CONST.GREEN
        self.window_enabled = True
        self.window = None

        if self.window_enabled:
            self.window = Window("driver")

    def drive(self):
        if not self.busy:
            return
        if INFO: print()

        if self.window_enabled:
            hsv_img = self.turtle.get_hsv_image()
            bin_img = img_threshold(hsv_img, self.color)
            self.window.show(bin_to_rgb(bin_img))

        self.counter += 1
        self.main.perform()
        self.turtle.keep_speed()

    def change_color(self):
        if self.color == CONST.BLUE:
            self.color = CONST.RED
        elif self.color == CONST.RED:
            self.color = CONST.BLUE
        else:
            raise ValueError("ERROR: current color neither blue nor red")


# Abstract Activity
class Activity:

    def __init__(self, parent, driver):
        self.parent = parent
        self.driver = driver
        self.turtle = driver.turtle

        self.activity = None
        self.busy = False
        self.ret = None

        self._first = True

    def start(self):
        return None

    def perform_init(self):
        if INFO:
            print(str(self.driver.counter) + ": " + str(type(self)) + " perform")

        if self._first:
            self._first = False
            self.start()

    # def perform(self)

    def do(self, activity):
        self.activity = activity
        self.busy = True
        activity.perform()

    def end(self):
        self.parent.busy = False

    def pop_ret(self):
        ret = self.ret
        self.ret = None
        return ret


class ThirdTask(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(MoveStraight(self, self.driver, 0.5))

        return self.end()


# Go straight a set distance.
class MoveStraight(Activity):

    def __init__(self, parent, driver, dist, speed=FORWARD_SPEED):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed
        self.step = self.speed * (CONST.SLEEP / 1000)
        self.start = None

    def start(self):
        self.turtle.stop()
        self.start = self.turtle.get_current_position()
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform_init(self)

        pos = self.turtle.get_current_position()
        if self.dist - np.linalg.norm(pos - self.start) < self.step / 2:
            self.turtle.stop()
            return self.end()
