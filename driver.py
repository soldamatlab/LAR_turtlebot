import CONST
import numpy as np
from camera import *
import time

INFO = False


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.busy = True
        self.main = MainActivity(self, self)
        self.counter = 0
        
        self.color = CONST.GREEN

    def drive(self):
        if not self.busy:
            return None  #TODO
        if INFO: print()

        self.counter += 1
        self.main.perform()
        self.turtle.keep_speed()

    def change_color(self):
        if self.color == CONST.GREEN or self.color == CONST.BLUE:
            self.color = CONST.RED
        elif self.color == CONST.RED:
            self.color = CONST.BLUE
        else:
            print("ERROR: undefined color")
            quit()


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


class MainActivity(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(GoThroughGate(self, self.driver, self.driver.color, window=False))

        if isinstance(self.activity, GoThroughGate):
            self.driver.change_color()
            return self.do(GoThroughGate(self, self.driver, self.driver.color, window=False))


class TestActivity(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)
        self.window = Window("test")

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        hsv_img = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv_img, self.driver.color)
        self.window.show(bin_to_rgb(bin_img))


# Find a gate of the given color, measure its distance and go through it.
class GoThroughGate(Activity):

    def __init__(self, parent, driver, color, window=False):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.window = window

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if (self.activity is None) or (isinstance(self.activity, MeasureGateDist) and self.ret is None):
            return self.do(FindGate(self, self.driver, self.color, window=self.window))

        if isinstance(self.activity, FindGate):
            return self.do(MeasureGateDist(self, self.driver, self.color))

        if isinstance(self.activity, MeasureGateDist):
            dist = self.pop_ret()
            return self.do(Forward(self, self.driver, dist))

        self.end()


# Find gate of given color by turning and center itself on it.
class FindGate(Activity):

    def __init__(self, parent, driver, color, speed=np.pi/8, center_limit=12, window=False):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.speed = speed
        self.center_limit = center_limit  # in pixels
        self.window = window
        self.dir = 1

        if window:
            self.w_bin = Window("FindTwoSticks")

    def perform(self):
        Activity.perform_init(self)

        hsv = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv, self.color)
        sticks = self.driver.turtle.get_segments(self.color, bin_img=bin_img, min_area=2500)

        # Testing window
        if self.window:
            self.w_bin.show(bin_to_rgb(bin_img))

        if sticks.count < 1:  # TODO 2
            self.turtle.set_speed(0, self.dir * self.speed)
            return

        args = np.argsort(sticks.areas())
        center = sticks.centroids[args[0]]  # TODO (sticks.centroids[args[0]] + sticks.centroids[args[1]]) / 2

        diff = center[0] - (np.shape(bin_img)[1] / 2)

        if diff < 0:
            new_dir = 1
        else:
            new_dir = -1

        if new_dir != self.dir and abs(diff) < self.center_limit:
            self.turtle.stop()
            self.end()

        self.dir = new_dir
        self.turtle.set_speed(0, self.dir * self.speed)


# Measure a distance of the closest gate of the given color. (without turning)
class MeasureGateDist(Activity):

    def __init__(self, parent, driver, color, attempts=12):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.attempts = attempts

    def perform(self):
        Activity.perform_init(self)

        if self.attempts == 0:
            if INFO: print("\n MeasureGateDist FAILED")
            self.parent.ret = None
            self.end()

        sticks = self.driver.turtle.get_segments(self.color)
        if sticks.count < 2:
            self.attempts -= 1
            return self.perform()

        pc = self.turtle.get_point_cloud()
        sticks.calculate_coors(pc)

        args = np.argsort(sticks.areas())
        center = (sticks.coors[args[0]] + sticks.coors[args[1]]) / 2
        self.parent.ret = center[2]
        self.end()


# Go forward a set distance.
class Forward(Activity):

    def __init__(self, parent, driver, dist, speed=0.2):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed

    def start(self):
        self.turtle.reset_odometry()
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform_init(self)

        odometry = self.turtle.get_odometry()
        if self.dist - odometry[0] < self.speed * (CONST.SLEEP / 1000) / 2:
            self.turtle.stop()
            self.end()


# Stand idle for a given amount of time.
class Idle(Activity):

    def __init__(self, parent, driver, idle_time):
        Activity.__init__(self, parent, driver)
        self.idle_time = idle_time  # in seconds
        self.start_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def perform(self):
        Activity.perform_init(self)

        if time.perf_counter() - self.start_time < self.idle_time:
            return
        self.end()


# class Goto(Activity):
#
#     def __init__(self, parent, driver, target):
#         Activity.__init__(self, parent, driver)
#
#         x = target[0]
#         z = target[2]
#         self.dist = np.sqrt(x ** 2 + z ** 2)
#         self.alpha = np.arccos(z / self.dist)
#
#     def perform(self):
#         Activity.perform_init(self)
#         if self.busy:
#             return self.activity.perform()
#
#         if self.activity is None:
#             return self.do(Turn(self, self.driver, self.alpha))
#
#         # if isinstance(self.activity, Turn): TODO
#         #     return self.do(Forward(self, self.driver, self.dist))
#
#         self.end()


# class Turn(Activity):
#
#     def __init__(self, parent, driver, degree, speed=np.pi/12):
#         Activity.__init__(self, parent, driver)
#         self.speed = speed
#         self.turn_for = degree / speed
#         self.start_time = None
#
#     def start(self):
#         self.start_time = time.perf_counter()
#         self.turtle.set_speed(0, self.speed)
#
#     def perform(self):
#         Activity.perform_init(self)
#         if self.busy:
#             return self.activity.perform()
#
#         if 1000 * (self.turn_for - (time.perf_counter() - self.start_time)) < CONST.SLEEP / 2:
#             self.turtle.stop()
#             self.end()
