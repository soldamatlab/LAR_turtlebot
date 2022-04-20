from curses import window
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

    def start(self):
        self.turtle.stop()
        self.turtle.reset_odometry()

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(GotoCoors(self, self.driver, [0.2, 0.]))

        return self.end()


class FindNearestStick(Activity):

    def __init__(self, parent, driver, turn_left,
                 turn_offset=np.pi,
                 n_subturns=4,
                 speed=TURN_SPEED,
                 window=False):
        Activity.__init__(self, parent, driver)
        self.look_left = turn_left
        self.turn_offset = turn_offset
        self.n_subturns = n_subturns
        self.subturn_offset = None
        self.subturns_done = 0

        self.speed = speed
        self.window = window
        self.w_bin = None
    
    def start(self):
        self.turtle.stop()  # safety
        if window:
            self.w_bin = Window("FindNearestStick")
        self.subturn_offset = self.turn_offset / self.n_subturns
    
    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(ScanForNearest(self, self.driver, window=self.window, w_bin=self.w_bin))

        if isinstance(self.activity, ScanForNearest):
            if self.subturns_done < self.n_subturns:
                self.subturns_done += 1
                return self.do(Turn(self, self.driver, self.subturn_offset))

            else:
                print("TODO")
                return self.end()


class ScanForNearest(Activity):
    def __init__(self, parent, driver,
                 window=False,
                 w_bin=None):
        Activity.__init__(self, parent, driver)
        self.nearest_coors = None
        self.nearest_color = None
        self.nearest_dist = None

        self.window = window
        self.w_bin = w_bin
        
    def start(self):
        if self.window & self.w_bin is None:
            self.w_bin = Window("ScanSticks")

    def perform(self):
        # Process image
        hsv = self.turtle.get_hsv_image()
        if self.window:
            bin_all_colors = np.zeros_like(np.shape(hsv))

        for color in [CONST.RED, CONST.BLUE, CONST.GREEN]:
            bin_img = img_threshold(hsv, color)
            if self.window:
                bin_all_colors = bin_all_colors or bin_img
            sticks = self.driver.turtle.get_segments(color, bin_img=bin_img, get_coors=True, get_dists=True)
            nearest_idx = np.argsort(sticks.dists)[-1]
            min_dist = sticks.dists[nearest_idx]
            if (min_dist is None) or (min_dist < self.nearest_dist):
                self.nearest_dist = min_dist
                self.nearest_coors = sticks.get_flat_coors[nearest_idx]
                self.nearest_color = color

        # Testing window
        if self.window:
            self.w_bin.show(bin_to_rgb(bin_all_colors))

        self.parent.ret = self.nearest_coors, self.nearest_color
        return self.end()


class BypassStick(Activity):

    def __init__(self, parent, driver, current_stick, next_stick, next_color,
                 reserve=0.05):
        Activity.__init__(self, parent, driver)
        self.current_stick = current_stick
        self.next_stick = next_stick
        self.next_color = next_color
        self.reserve = reserve

        self.center = None
        self.first = None
        self.second = None
        self.finish = None
        self.forward_angle = None

    def start(self):
        self.turtle.stop()  # safety
        forward_dir = self.next_stick - self.current_stick
        forward_dir /= np.linalg.norm(forward_dir)
        left_dir = np.array(-[forward_dir[1], forward_dir[0]])
        gap = CONST.ROBOT_WIDTH + self.reserve

        self.step = None
        self.center = (self.current_stick + self.next_stick) / 2
        if self.next_color == CONST.RED:
            self.first = self.next_stick - (forward_dir * gap) + (left_dir * gap)
            self.second = self.next_stick + (forward_dir * gap) + (left_dir * gap)
        elif self.next_color == CONST.BLUE:
            self.first = self.next_stick - (forward_dir * gap) - (left_dir * gap)
            self.second = self.next_stick + (forward_dir * gap) - (left_dir * gap)
        else:
            raise ValueError("BypassStick [next_color] needs to be RED or BLUE.")
        self.finish = self.next_stick + (forward_dir * gap)

        forward_angle = np.arccos(forward_dir[1])
        if forward_dir[0] > 0:
            forward_angle *= -1
        self.forward_angle = forward_angle
        
    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            step = 'center'
            return self.do(GotoCoors(self, self.driver, self.center))

        if isinstance(self.activity, GotoCoors):
            if self.step == 'center':
                self.step = 'first'
                return self.do(GotoCoors(self, self.driver, self.first))
            if self.step == 'first':
                self.step = 'second'
                return self.do(GotoCoors(self, self.driver, self.second))
            if self.step == 'second':
                self.step = 'finish'
                return self.do(GotoCoors(self, self.driver, self.finish))
            if self.step == 'finish':
                self.parent.ret = self.next_stick, self.forward_angle
                self.driver.turtle.stop()
                return self.end()


# Move to the given coordinates. [x, z], x .. right, z .. forward
class GotoCoors(Activity):

    def __init__(self, parent, driver, target):
        Activity.__init__(self, parent, driver)
        self.target = target
        self.start_pos = None

        x = target[0]
        z = target[1]
        self.dist = np.sqrt(x ** 2 + z ** 2)
        alpha = np.arccos(z / self.dist)
        if x > 0:
            alpha *= -1
        self.alpha = alpha

    def start(self):
        self.turtle.stop()
        self.start_pos = self.turtle.get_current_position()

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(Turn(self, self.driver, self.alpha))

        if isinstance(self.activity, Turn):
            return self.do(MoveStraight(self, self.driver, self.dist))

        return self.end()


# Turn a set amount of degrees.
# ONLY WORKS FOR <-pi;+pi> TURNS. (no larger)
class Turn(Activity):

    # degree ... in radians, left: positive, right: negative
    def __init__(self, parent, driver, degree, speed=TURN_SPEED):
        Activity.__init__(self, parent, driver)
        self.degree = degree
        self.direction = 1 if degree > 0 else -1
        self.speed = abs(speed)
        self.step = (CONST.SLEEP / 1000) * speed
        self.start_angle = None

    def start(self):
        self.turtle.stop()
        self.start_angle = self.turtle.get_current_angle()
        self.turtle.set_speed(0, self.direction * self.speed)

    def perform(self):
        Activity.perform_init(self)

        angle = self.turtle.get_current_angle()
        if abs(self.degree - (angle - self.start_angle)) > self.step / 2:
            return

        self.turtle.stop()
        return self.end()


# Go straight a set distance.
class MoveStraight(Activity):

    def __init__(self, parent, driver, dist, speed=FORWARD_SPEED):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed
        self.step = self.speed * (CONST.SLEEP / 1000)
        self.start_pos = None

    def start(self):
        self.turtle.stop()
        self.start_pos = self.turtle.get_current_coors()
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform_init(self)

        pos = self.turtle.get_current_coors()
        if self.dist - np.linalg.norm(pos - self.start_pos) < self.step / 2:
            self.turtle.stop()
            return self.end()
