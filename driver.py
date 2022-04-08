import CONST
import numpy as np
import time

INFO = True


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.main = MainActivity(None, self)
        self.counter = 0

    def drive(self):
        if INFO:
            print()
        self.counter += 1
        self.turtle.keep_speed()
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

        self._first = True

    def start(self):
        return None

    def perform(self):
        if INFO:
            print(str(self.driver.counter) + ": " + str(type(self)) + " perform")

        if self._first:
            self._first = False
            self.start()

        if self.busy:
            return self.activity.perform()

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
        Activity.perform(self)

        if self.activity is None:
            return self.do(FindTwoSticks(self, self.driver))

        if isinstance(self.activity, FindTwoSticks):
            sticks = self.ret
            self.ret = None
            target = np.mean(sticks, axis=0)
            return self.do(Goto(self, self.driver, target))

        self.end()


class FindTwoSticks(Activity):

    def __init__(self, parent, driver):
        Activity.__init__(self, parent, driver)

    def start(self):
        self.turtle.set_speed(0, np.pi / 12)

    def perform(self):
        Activity.perform(self)

        sticks = self.driver.turtle.get_segments(CONST.GREEN)

        if sticks.count < 2:
            return

        max_sticks = np.argsort(sticks.areas())
        A = sticks.coors[max_sticks[0]]
        B = sticks.coors[max_sticks[1]]

        self.parent.ret = (A, B)
        self.turtle.stop()
        self.end()


class Goto(Activity):

    def __init__(self, parent, driver, target):
        Activity.__init__(self, parent, driver)

        x = target[0]
        z = target[2]
        self.dist = np.sqrt(x ** 2 + z ** 2)
        self.alpha = np.arccos(z / self.dist)

    def perform(self):
        Activity.perform(self)

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
        self.start_time = time.perf_counter()

    def start(self):
        self.turtle.set_speed(0, self.speed)

    def perform(self):
        Activity.perform(self)

        if 1000 * (self.turn_for - (time.perf_counter() - self.start_time)) < CONST.SLEEP / 2:
            self.turtle.stop()
            self.end()


class Forward(Activity):

    def __init__(self, parent, driver, dist, speed=0.05):
        Activity.__init__(self, parent, driver)
        self.dist = dist
        self.speed = speed
        self.turtle.reset_odometry()

    def start(self):
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform(self)

        odometry = self.turtle.get_odometry()
        if self.dist - odometry[2] < self.speed * (CONST.SLEEP / 1000) / 2:
            self.turtle.stop()
            self.end()
