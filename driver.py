import CONST
import numpy as np


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.activity = None

    def drive(self):

        if not (self.activity is None):
            self.activity.perform(self)
            return

        sticks = self.turtle.get_segments(CONST.GREEN)

        if sticks.count < 2:
            self.turtle.set_speed(0, np.pi / 12)
            return

        max_sticks = np.argsort(sticks.areas())
        A = sticks.coors[max_sticks[0]]
        B = sticks.coors[max_sticks[1]]

        avg_coor = (A + B) / 2

        self.activity = A_goto(self, avg_coor)


class A_goto:

    def __init__(self, driver, target):
        x = target[0]
        z = target[2]
        self.dist = np.sqrt(x ** 2 + z ** 2)
        self.alpha = np.arccos(z / self.dist)

        driver.turtle.reset_odometry()

    def perform(self, driver):
        odometry = driver.turtle.get_odometry()

        # if odometry.angle < self.alpha:
        #
        #     return
        #
        # if odometry.dist < self.dist:
        #
        #     return
        #
        # driver.activity = None
