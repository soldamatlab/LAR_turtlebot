import CONST
import numpy as np
from camera import *
import time

INFO = True
FORWARD_SPEED = 0.2
TURN_SPEED = np.pi/8
ANGLE_MARGIN = np.pi / 12


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.busy = True
        self.main = MainActivity(self, self, window=True)
        self.counter = 0

        # self.window = Window("driver")
        # self.color = CONST.GREEN

    def drive(self):
        if not self.busy:
            return None  #TODO
        if INFO: print()

        # hsv_img = self.turtle.get_hsv_image()
        # bin_img = img_threshold(hsv_img, self.color)
        # self.window.show(bin_to_rgb(bin_img))

        self.counter += 1
        self.main.perform()
        self.turtle.keep_speed()

    def change_color(self):
        if self.color == CONST.BLUE:
            self.color = CONST.RED
        elif self.color == CONST.RED:
            self.color = CONST.BLUE
        else:
            print("ERROR: current color neither blue nor red")
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

    def __init__(self, parent, driver, window=False):
        Activity.__init__(self, parent, driver)
        self.window = window
        self.determined_first_color = False

    def start(self):
        self.activity = GoThroughGate(self, self.driver, CONST.GREEN, window=self.window)  # TODO rem
    #     self.determined_first_color = True  # TODO rem
    #     self.driver.color = CONST.RED  # TODO rem

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(GoThroughGate(self, self.driver, CONST.GREEN, window=self.window))

        if isinstance(self.activity, DetermineFirstColor):
            self.determined_first_color = True
            first_color, area = self.pop_ret()  # TODO check area
            self.driver.color = first_color
        if not self.determined_first_color:
            return self.do(DetermineFirstColor(self, self.driver, window=self.window))

        # if isinstance(self.activity, GoThroughGate):
        #     self.driver.change_color()  TODO uncomment
        return self.do(GoThroughGate(self, self.driver, self.driver.color, window=self.window))


class TestActivity(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)
        self.window = None

    def start(self):
        self.window = Window("test")

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        hsv_img = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv_img, self.driver.color)
        self.window.show(bin_to_rgb(bin_img))


# TODO turn to sides only, not 360 ?
# Turn 360 degrees, measure red and blue stick areas, return which was the larges.
# returns (color, area)
class DetermineFirstColor(Activity):

    def __init__(self, parent, driver, speed=TURN_SPEED, window=False,
                 angle_margin=ANGLE_MARGIN,
                 direction=-1,
                 ):
        Activity.__init__(self, parent, driver)
        self.speed = speed
        self.window = window
        self.blue_window = None
        self.red_window = None
        self.blue_largest_area = 0
        self.red_largest_area = 0
        self.direction = direction  # left: +1, right: -1
        self.turn_counter = TurnCounter(direction, self.turtle, angle_margin=angle_margin)

    def start(self):
        if self.window:
            self.blue_window = Window("BLUE")
            self.red_window = Window("RED")

        self.turn_counter.start()
        self.turtle.set_speed(0, self.direction * self.speed)

    def perform(self):
        Activity.perform_init(self)

        # Termination condition
        if self.turn_counter.get_turns() > 0:
            return self.done()

        # Measurements
        hsv_img = self.turtle.get_hsv_image()
        blue_bin = img_threshold(hsv_img, CONST.BLUE)
        red_bin = img_threshold(hsv_img, CONST.RED)
        if self.window:
            self.blue_window.show(bin_to_rgb(blue_bin))
            self.red_window.show(bin_to_rgb(red_bin))
        blue_segments = self.turtle.get_segments(CONST.BLUE, bin_img=blue_bin)
        red_segments = self.turtle.get_segments(CONST.RED, bin_img=red_bin)
        if blue_segments.count > 0:
            blue_max = np.amax(blue_segments.areas())
            if blue_max > self.blue_largest_area:
                self.blue_largest_area = blue_max
        if red_segments.count > 0:
            red_max = np.amax(red_segments.areas())
            if red_max > self.red_largest_area:
                self.red_largest_area = red_max

    def done(self):
        if self.blue_largest_area >= self.red_largest_area:
            color = CONST.BLUE
            area = self.blue_largest_area
        else:
            color = CONST.RED
            area = self.red_largest_area

        self.parent.ret = (color, area)
        self.turtle.stop()
        self.end()


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
            dist = self.pop_ret() + (CONST.ROBOT_WIDTH / 2)
            return self.do(Forward(self, self.driver, dist))

        self.end()


# Find gate of given color by turning and center itself on it.
class FindGate(Activity):

    def __init__(self, parent, driver, color, speed=TURN_SPEED, window=False,
                 height_diff_factor=1.05,
                 center_limit_min=2,
                 center_limit_step=2,
                 center_limit_max=24,
                 ):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.speed = speed
        self.height_diff_factor = height_diff_factor
        self.center_limit_min = center_limit_min  # in pixels
        self.center_limit_step = center_limit_step  # in pixels
        self.center_limit_max = center_limit_max  # in pixels
        self.center_limit = center_limit_min
        self.window = window
        self.w_bin = None
        self.dir = 1

    def start(self):
        self.turtle.stop()  # safety
        if self.window:
            self.w_bin = Window("FindTwoSticks")

    def perform(self):
        Activity.perform_init(self)

        hsv = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv, self.color)
        sticks = self.driver.turtle.get_segments(self.color, bin_img=bin_img, min_area=2500)

        # Testing window
        if self.window:
            self.w_bin.show(bin_to_rgb(bin_img))

        if sticks.count < 2:
            self.turtle.set_speed(0, self.dir * self.speed)
            return

        args = np.argsort(sticks.heights())
        A_height = sticks.height(args[0])
        B_height = sticks.height(args[1])
        A_coors = sticks.centroids[args[0]]
        B_coors = sticks.centroids[args[1]]

        if (A_height / B_height) > self.height_diff_factor:
            self.turtle.set_speed(0, self.dir * self.speed)
            return

        center = (A_coors + B_coors) / 2
        diff = center[0] - (np.shape(bin_img)[1] / 2)

        if diff < 0:
            new_dir = 1
        else:
            new_dir = -1

        if new_dir != self.dir:
            if abs(diff) < self.center_limit:
                self.turtle.stop()
                self.end()
            elif self.center_limit < self.center_limit_max:
                self.center_limit += self.center_limit_step

        self.dir = new_dir
        self.turtle.set_speed(0, self.dir * self.speed)


# Measure a distance of the closest gate of the given color. (without turning)
# return None ... if all attempts fail
# return dist ... otherwise
class MeasureGateDist(Activity):

    def __init__(self, parent, driver, color,
                 attempts=12,
                 ):
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

    def __init__(self, parent, driver, dist, speed=FORWARD_SPEED):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed
        self.step = self.speed * (CONST.SLEEP / 1000)

    def start(self):
        self.turtle.stop()
        self.turtle.reset_odometry()
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform_init(self)

        odometry = self.turtle.get_odometry()[0]
        if self.dist - odometry < self.step / 2:
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
#     def __init__(self, parent, driver, degree, speed=TURN_SPEED):
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

# Counts turns made by the robot from "start".
# Only works correctly when not turning back more than the given [angle_margin].
# Does not subtract turns.
class TurnCounter:

    def __init__(self, direction, turtle, angle_margin=ANGLE_MARGIN):
        self.direction = direction  # left: +1, right: -1
        self.turtle = turtle
        self.angle_margin = angle_margin
        self.turns = 0
        self.half_turns = 0
        self.half_turn = False

    # WILL RESET ODOMETRY
    def start(self):
        self.turtle.reset_odometry()

    def update(self):
        angle = self.turtle.get_odometry()[2]
        if self.direction < 0:
            angle *= -1

        if self.half_turn:
            if angle > self.angle_margin:
                self.half_turn = False
                self.half_turns += 1
                self.turns += 1
        else:
            if (angle < 0) and (angle > - np.pi + self.angle_margin):
                self.half_turn = True
                self.half_turns += 1

    def get_turns(self):
        self.update()
        return self.turns

    def get_half_turns(self):
        self.update()
        return self.half_turns
