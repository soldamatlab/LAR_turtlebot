import math

import CONST
import numpy as np
from camera import *
import time
import math

INFO = True
FORWARD_SPEED = 0.2
TURN_SPEED = np.pi/8
ANGLE_MARGIN = np.pi / 12
TURN_OFFSET = CONST.ROBOT_WIDTH/2 + 0.05
OVERSHOOT = CONST.ROBOT_WIDTH/2
FOV = (30 + 20) * 2*np.pi / 360
FOV_GREEN = (60 + 20) * 2*np.pi / 360
HEIGHT_DIFF_FACTOR = 1.05
START_GATE_FIND_ATTEMPTS = 1
START_GATE_BACKWARD_DIST = 0.1


class Driver:

    def __init__(self, turtle):
        self.turtle = turtle
        self.busy = True
        self.main = MainActivity(self, self, window=False)
        self.counter = 0
        self.color = CONST.GREEN

        self.window = Window("driver")

    def drive(self):
        if not self.busy:
            return
        if INFO: print()

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
        self.next_turn = None

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(PassStartGate(self, self.driver, fov=FOV_GREEN, window=self.window))

        if isinstance(self.activity, DetermineFirstColor):
            self.determined_first_color = True
            first_color, area, angle = self.pop_ret()
            self.driver.color = first_color
            self.next_turn = -1 if angle < 0 else 1
        if not self.determined_first_color:
            return self.do(DetermineFirstColor(self, self.driver, fov=FOV, window=False))

        if isinstance(self.activity, PassNormalGate):
            self.driver.change_color()
            angle = self.pop_ret()
            self.next_turn = -1 if angle > 0 else 1
        return self.do(PassNormalGate(self, self.driver, self.driver.color, fov=FOV, init_dir=self.next_turn, window=self.window))


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

        if self.activity is None:
            return self.do(FindGate(self, self.driver, CONST.GREEN))

        if isinstance(self.activity, FindGate):
            return self.do(MeasureGateCoordinates(self, self.driver, CONST.GREEN))

        if isinstance(self.activity, MeasureGateCoordinates):
            coors = self.pop_ret()
            print(coors)
            return self.end()


# Turn withing the given FOV (do 360 instead if FOV is None),
# measure red and blue stick areas, return which was the larges.
# returns (color, area, angle) ... angle is the angle at which the bot found the largest area
class DetermineFirstColor(Activity):

    def __init__(self, parent, driver, speed=TURN_SPEED, fov=None, window=False,
                 angle_margin=ANGLE_MARGIN,
                 direction=1,
                 ):
        Activity.__init__(self, parent, driver)
        self.speed = speed
        self.fov = None if fov is None else abs(fov)
        self.window = window
        self.blue_window = None
        self.red_window = None
        self.blue_largest_area = 0
        self.red_largest_area = 0
        self.blue_angle = None
        self.red_angle = None
        self.init_dir = 1 if direction > 0 else -1  # FINAL, left: +1, right: -1
        self.dir = self.init_dir
        self.turn_counter = TurnCounter(direction, self.turtle, angle_margin=angle_margin) if self.fov is None else None
        self.turn = None if self.fov is None else 1

    def start(self):
        if self.window:
            self.blue_window = Window("BLUE")
            self.red_window = Window("RED")

        self.turtle.stop()  # safety
        if self.fov is None:
            self.turn_counter.start()
        else:
            self.turtle.reset_odometry()
        self.turtle.set_speed(0, self.dir * self.speed)

    def perform(self):
        Activity.perform_init(self)

        # Termination condition
        if self.fov is None:
            if self.turn_counter.get_turns() > 0:
                return self.done()
        else:
            angle = self.turtle.get_odometry()[2]
            angle *= self.init_dir
            if self.turn == 1:
                if angle > self.fov:
                    self.change_dir()
                    self.turn = 2
            elif self.turn == 2:
                if angle < - self.fov:
                    self.change_dir()
                    self.turn = 3
            elif self.turn == 3:
                if angle > 0:
                    return self.done()
            else:
                raise Exception("turn counter invalid")

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
                self.blue_angle = self.turtle.get_odometry()[2]
        if red_segments.count > 0:
            red_max = np.amax(red_segments.areas())
            if red_max > self.red_largest_area:
                self.red_largest_area = red_max
                self.red_angle = self.turtle.get_odometry()[2]

    def change_dir(self):
        self.dir *= -1
        self.turtle.set_speed(0, self.dir * self.speed)

    def done(self):
        if self.blue_largest_area >= self.red_largest_area:
            color = CONST.BLUE
            area = self.blue_largest_area
            angle = self.blue_angle
        else:
            color = CONST.RED
            area = self.red_largest_area
            angle = self.red_angle
        self.parent.ret = (color, area, angle)
        self.turtle.stop()
        return self.end()


# Same as [PassNormalGate] but [FindGate] is not infinite.
# If find [FindGate] fails, the bot moves backwards and tries again.
class PassStartGate(Activity):

    def __init__(self, parent, driver, color=CONST.GREEN, fov=None, init_dir=1, window=False,
                 turn_offset=TURN_OFFSET,
                 overshoot=OVERSHOOT,
                 find_attempts=START_GATE_FIND_ATTEMPTS,
                 backward_dist=START_GATE_BACKWARD_DIST,
                 ):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.fov = fov
        self.init_dir = init_dir
        self.window = window
        self.turn_offset = turn_offset
        self.overshoot = overshoot
        self.step = 0
        self.second_step = None
        self.side = None
        self.find_attempts = find_attempts
        self.backward_dist = backward_dist

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if (self.activity is None)\
                or (isinstance(self.activity, MoveStraight))\
                or (isinstance(self.activity, MeasureGateCoordinates) and self.ret is None):
            return self.do(FindGate(self, self.driver, self.color, attempts=self.find_attempts, fov=self.fov, init_dir=self.init_dir, window=self.window))

        if isinstance(self.activity, FindGate):
            side = self.pop_ret()
            if side is None:
                return self.do(MoveStraight(self, self.driver, self.backward_dist, speed=-FORWARD_SPEED))
            else:
                self.side = -1 if side < 0 else 1
                return self.do(MeasureGateCoordinates(self, self.driver, self.color))

        if isinstance(self.activity, MeasureGateCoordinates):
            A, B = self.pop_ret()
            return self.do(GoThroughGate(self, self.driver, A, B, turn_offset=self.turn_offset, overshoot=self.overshoot))

        if isinstance(self.activity, GoThroughGate):
            self.parent.ret = self.side
            return self.end()


# Find a gate of the given color, measure its distance and go through it.
# Returns the side to which the bot turned initially to go through the gate. (left: +1, right: -1)
class PassNormalGate(Activity):

    def __init__(self, parent, driver, color, fov=None, init_dir=1, window=False,
                 turn_offset=TURN_OFFSET,
                 overshoot=OVERSHOOT,
                 ):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.fov = fov
        self.init_dir = init_dir
        self.window = window
        self.turn_offset = turn_offset
        self.overshoot = overshoot
        self.step = 0
        self.second_step = None
        self.side = None

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if (self.activity is None) or (isinstance(self.activity, MeasureGateCoordinates) and self.ret is None):
            return self.do(FindGate(self, self.driver, self.color, fov=self.fov, init_dir=self.init_dir, window=self.window))

        if isinstance(self.activity, FindGate):
            self.side = -1 if self.pop_ret() < 0 else 1
            return self.do(MeasureGateCoordinates(self, self.driver, self.color))

        if isinstance(self.activity, MeasureGateCoordinates):
            A, B = self.pop_ret()
            return self.do(GoThroughGate(self, self.driver, A, B, turn_offset=self.turn_offset, overshoot=self.overshoot))

        if isinstance(self.activity, GoThroughGate):
            self.parent.ret = self.side
            return self.end()


# Go through a gate given the coordinates of its two sticks.
class GoThroughGate(Activity):

    def __init__(self, parent, driver, stick_A, stick_B,
                 turn_offset=TURN_OFFSET,
                 overshoot=OVERSHOOT,
    ):
        Activity.__init__(self, parent, driver)
        self.A = stick_A
        self.B = stick_B
        self.turn_offset = turn_offset
        self.overshoot = overshoot
        self.step = 0
        self.second_step = None

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.step == 0:
            A, B = np.array([self.A[0], self.A[2]]), np.array([self.B[0], self.B[2]])
            gate_center = (A + B) / 2
            midturn_point = self.calculate_first_step(A, B, gate_center, self.turn_offset)
            self.second_step = self.calculate_second_step(midturn_point, gate_center)
            self.step = 1
            return self.do(GotoCoors(self, self.driver, midturn_point))

        if self.step == 1:
            self.step = 2
            return self.do(GotoCoors(self, self.driver, self.second_step, overshoot=self.overshoot))

        return self.end()

    # Calculate the first step of the turn. (Vector from start of the turn to the mid-turn point.)
    # B has higher x-coordinate than A
    @staticmethod
    def calculate_first_step(A, B, C, turn_offset):
        D = B - A
        N = np.array([D[1], -D[0]])
        N /= math.sqrt(N[0] ** 2 + N[1] ** 2)
        first_step = C + turn_offset * N
        return first_step

    # Calculate the second step of the turn. (Vector from the mid-turn point to the end of the turn.)
    @staticmethod
    def calculate_second_step(M, C):
        norm = math.sqrt(M[0] ** 2 + M[1] ** 2)
        alpha = np.arccos(M[1] / norm)
        if M[0] < 0:
            alpha *= -1
        second_step = GoThroughGate.rotate_vector(C - M, alpha)
        return second_step

    @staticmethod
    def rotate_vector(vec, alpha):
        s, c = np.sin(alpha), np.cos(alpha)
        R = np.array([[c, -s], [s, c]])
        return np.matmul(R, vec)


# Find gate of given color by turning and center itself on it.
# Return the angle at which the gate has been found or None if run out of attempts.
class FindGate(Activity):

    def __init__(self, parent, driver, color, fov=None, init_dir=1, speed=TURN_SPEED, window=False,
                 height_diff_factor=HEIGHT_DIFF_FACTOR,
                 center_limit_min=2,
                 center_limit_step=2,
                 center_limit_max=24,
                 attempts=0,  # 1 attempt means left,center,right,center within the fov; set to 0 for unlimited attempts
                 ):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.speed = speed
        self.fov = None if fov is None else abs(fov)
        self.height_diff_factor = height_diff_factor
        self.center_limit_min = center_limit_min  # in pixels
        self.center_limit_step = center_limit_step  # in pixels
        self.center_limit_max = center_limit_max  # in pixels
        self.center_limit = center_limit_min
        self.window = window
        self.w_bin = None
        self.dir = -1 if init_dir < 0 else 1
        self.max_attempts = attempts
        self.half_turns = 0
        self.last_angle = None

    def start(self):
        self.turtle.stop()  # safety
        self.turtle.reset_odometry()
        if self.window:
            self.w_bin = Window("FindTwoSticks")

    def perform(self):
        Activity.perform_init(self)

        # Process image
        hsv = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv, self.color)
        sticks = self.driver.turtle.get_segments(self.color, bin_img=bin_img)

        # Testing window
        if self.window:
            self.w_bin.show(bin_to_rgb(bin_img))

        if sticks.count < 2:
            self.turtle.set_speed(0, self.dir * self.speed)
            return self.continue_search()

        # Pick A,B
        args = np.argsort(sticks.heights())
        A_height = sticks.height(args[0])
        B_height = sticks.height(args[1])
        A_coors = sticks.centroids[args[0]]
        B_coors = sticks.centroids[args[1]]

        # Check same height
        if (A_height / B_height) > self.height_diff_factor:
            self.turtle.set_speed(0, self.dir * self.speed)
            return self.continue_search()

        # Center on sticks
        center = (A_coors + B_coors) / 2
        diff = center[0] - (np.shape(bin_img)[1] / 2)
        if diff < 0:
            new_dir = 1
        else:
            new_dir = -1
        if new_dir != self.dir:
            if abs(diff) < self.center_limit:
                return self.done()
            elif self.center_limit < self.center_limit_max:
                self.center_limit += self.center_limit_step
        self.dir = new_dir
        self.turtle.set_speed(0, self.dir * self.speed)

    def continue_search(self):
        # Keep in FOV
        if self.fov is not None:
            angle = self.turtle.get_odometry()[2]
            if abs(angle) > self.fov:
                self.dir = -1 if angle > 0 else 1
                self.turtle.set_speed(0, self.dir * self.speed)
            if (self.max_attempts > 0) and (self.last_angle is not None) and (self.last_angle * angle) < 0:
                self.half_turns += 1
                if self.half_turns / 2 >= self.max_attempts:
                    self.parent.ret = None
                    return self.end()
            self.last_angle = angle
        return

    def done(self):
        self.turtle.stop()
        angle = self.turtle.get_odometry()[2]
        self.parent.ret = angle
        return self.end()


# Measure a distance of the closest gate of the given color. (without turning)
# return None ... if all attempts fail
# return (A, B) ... coordinates, A is left stick, B is right stick
class MeasureGateCoordinates(Activity):

    def __init__(self, parent, driver, color,
                 attempts=12,
                 ):
        Activity.__init__(self, parent, driver)
        self.color = color
        self.attempts = attempts

    def perform(self):
        Activity.perform_init(self)

        if self.attempts <= 0:
            if INFO: print("\n MeasureGateDist FAILED")
            self.parent.ret = None
            return self.end()

        sticks = self.driver.turtle.get_segments(self.color)
        if sticks.count < 2:
            self.attempts -= 1
            return self.perform()

        pc = self.turtle.get_point_cloud(convert_to_bot=True)
        sticks.calculate_coors(pc)

        args = np.argsort(sticks.areas())
        A = sticks.coors[args[-1]]
        B = sticks.coors[args[-2]]
        if A[0] > B[0]:
            tmp = A
            A = B
            B = tmp

        self.parent.ret = (A, B)
        return self.end()


class GotoCoors(Activity):

    # target = [x, z]
    def __init__(self, parent, driver, target, overshoot=0):
        Activity.__init__(self, parent, driver)
        x = target[0]
        z = target[1]
        self.dist = np.sqrt(x ** 2 + z ** 2)
        alpha = np.arccos(z / self.dist)
        if x > 0:
            alpha *= -1
        self.alpha = alpha
        self.overshoot = overshoot

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.activity is None:
            return self.do(Turn(self, self.driver, self.alpha))

        if isinstance(self.activity, Turn):
            return self.do(MoveStraight(self, self.driver, self.dist + self.overshoot))

        return self.end()


# Turn a set amount of degrees.
# ONLY WORKS FOR <-pi;+pi> TURNS. (no larger)
class Turn(Activity):

    # degree ... in radians, left: positive, right: negative
    def __init__(self, parent, driver, degree, speed=TURN_SPEED):
        Activity.__init__(self, parent, driver)
        self.degree = degree
        self.direction = 1 if degree > 0 else -1
        self.speed = speed
        self.step = (CONST.SLEEP / 1000) * speed

    def start(self):
        self.turtle.stop()  # safety
        self.turtle.reset_odometry()
        self.turtle.set_speed(0, self.direction * self.speed)

    def perform(self):
        Activity.perform_init(self)

        angle = self.turtle.get_odometry()[2]
        if abs(self.degree - angle) > self.step / 2:
            return

        self.turtle.stop()
        return self.end()


# Go forward a set distance.
class MoveStraight(Activity):

    def __init__(self, parent, driver, dist, speed=FORWARD_SPEED):
        Activity.__init__(self, parent, driver)
        self.dist = abs(dist)
        self.speed = speed
        self.step = self.speed * (CONST.SLEEP / 1000)

    def start(self):
        self.turtle.stop()
        self.turtle.reset_odometry()
        self.turtle.set_speed(self.speed, 0)

    def perform(self):
        Activity.perform_init(self)

        odometry = self.turtle.get_odometry()[0]
        if self.dist - abs(odometry) < self.step / 2:
            self.turtle.stop()
            return self.end()


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
        return self.end()


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
