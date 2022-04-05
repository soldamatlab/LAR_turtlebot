import CONST
import numpy as np
import time


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.main = MainActivity(None, self)

    def drive(self):
        self.main.perform()


# Abstract Activity
class Activity:

    def __init__(self, parent, driver):
        self.parent = parent
        self.driver = driver
        self.turtle = driver.turtle

        self.activity = None
        self.busy = False
        self.ret = None

    def perform(self):
        return None

    def do(self, activity):
        self.activity = activity
        self.busy = True
        activity.perform()

    def end(self):
        self.parent.busy = False


class MainActivity(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)

    def perform(self):
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(FindTwoSticks(self, self))

        if isinstance(self.activity, FindTwoSticks):
            target = self.ret
            self.ret = None
            return self.do(Goto(self, self, target))


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

    def perform(self):
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(Turn(self, self.driver, self.alpha))

        if isinstance(self.activity, Turn):
            return self.do(Forward(self, self.driver, self.dist))

        self.end()


class Turn(Activity):

    def __init__(self, parent, driver, degree, speed=np.pi/12):
        Activity.__init__(self, parent, driver)
        self.speed = speed
        self.turn_for = degree / speed
        self.start = time.perf_counter()

    def perform(self):
        if self.turn_for - (1000 * (time.perf_counter() - self.start)) > CONST.SLEEP / 2:
            self.turtle.set_speed(0, self.speed)
        else:
            self.end()


class Forward(Activity):

    def __init__(self, parent, driver, dist, speed=0.05):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed
        self.turtle.reset_odometry()

    def perform(self):
        odometry = self.turtle.get_odometry()
        if self.dist - odometry[2] > self.speed * (CONST.SLEEP / 1000) / 2:
            self.turtle.set_speed(self.speed, 0)
        else:
            self.end()
