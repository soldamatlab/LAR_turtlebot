import CONST
import numpy as np


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.activity = FindTwoSticks(self, self)
        self.ret = None

    def drive(self):
        if self.activity is not None:
            self.activity.perform()
            return

        print("RET: " + str(self.ret))


# Abstract Activity
class Activity:

    def __init__(self, parent, driver):
        self.parent = parent
        self.driver = driver
        self.turtle = driver.turtle
        self.ret = None

    # def perform(self):

    def end(self):
        self.parent.activity = None


class FindTwoSticks(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)

    def perform(self):
        sticks = self.driver.turtle.get_segments(CONST.GREEN)

        if sticks.count < 2:
            self.turtle.set_speed(0, np.pi / 12)
            return

        max_sticks = np.argsort(sticks.areas())
        A = sticks.coors[max_sticks[0]]
        B = sticks.coors[max_sticks[1]]

        self.parent.ret = (A, B)
        self.end()


class Goto(Activity):

    def __init__(self, parent, driver, target):
        Activity.__init__(self, parent, driver)

        x = target[0]
        z = target[2]
        self.dist = np.sqrt(x ** 2 + z ** 2)
        self.alpha = np.arccos(z / self.dist)

        self.turtle.reset_odometry()

    def perform(self):
        odometry = self.turtle.get_odometry()

        # if odometry.angle < self.alpha:
        #
        #     return
        #
        # if odometry.dist < self.dist:
        #
        #     return
        #
        # driver.activity = None
