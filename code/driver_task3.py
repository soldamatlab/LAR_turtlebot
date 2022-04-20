import CONST
import numpy as np
from camera import *
import time
import math

INFO = False  # TODO
FORWARD_SPEED = 0.2
TURN_SPEED = np.pi/8
HEIGHT_DIFF_FACTOR = 1.05
FOV_GREEN = (60 + 20) * 2*np.pi / 360
START_GATE_FIND_ATTEMPTS = 1
START_GATE_BACKWARD_DIST = 0.1
MAX_GATE_AREA_DIFF = 20000
GATE_TURN_OFFSET = CONST.ROBOT_WIDTH/2 + 0.05
GATE_OVERSHOOT = 0.05  # CONST.ROBOT_WIDTH/2
GATE_STICK_MIN_AREA = 3000


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
            return self.do(MeasureGateCoordinates(self, self.driver, CONST.GREEN))
            # return self.do(PassStartGate(self, self.driver, fov=FOV_GREEN))

        if isinstance(self.activity, MeasureGateCoordinates):
            print("GATE COORDINATES")
            print(self.pop_ret())

        return self.end()


# Pass the starting gate.
# If find [FindGate] fails, the bot moves backwards and tries again.
class PassStartGate(Activity):

    def __init__(self, parent, driver, color=CONST.GREEN, fov=None, init_dir=1, window=False,
                 turn_offset=GATE_TURN_OFFSET,
                 overshoot=GATE_OVERSHOOT,
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


# Go through a gate given the coordinates of its two sticks.
class GoThroughGate(Activity):

    def __init__(self, parent, driver, stick_A, stick_B,
                 turn_offset=GATE_TURN_OFFSET,
                 overshoot=GATE_OVERSHOOT,
    ):
        Activity.__init__(self, parent, driver)
        self.A = stick_A
        self.B = stick_B
        self.turn_offset = turn_offset
        self.overshoot = overshoot
        self.step = 0
        self.gate_center = None
        self.midturn_point = None

    def start(self):
        self.gate_center = (self.A + self.B) / 2
        self.midturn_point = self.calculate_midturn_point(self.A, self.B, self.gate_center, self.turn_offset)

    def perform(self):
        Activity.perform_init(self)
        if self.busy:
            return self.activity.perform()

        if self.step == 0:
            self.step = 1
            return self.do(GotoCoors(self, self.driver, self.midturn_point))

        if self.step == 1:
            self.step = 2
            return self.do(GotoCoors(self, self.driver, self.gate_center))

        if self.step == 2:
            self.step = 3
            return self.do(MoveStraight(self, self.driver, self.overshoot))

        return self.end()

    # Calculate the first step of the turn. (Vector from start of the turn to the mid-turn point.)
    # B has higher x-coordinate than A
    @staticmethod
    def calculate_midturn_point(A, B, C, turn_offset):
        D = B - A
        N = np.array([D[1], -D[0]])
        N /= math.sqrt(N[0] ** 2 + N[1] ** 2)
        midturn = C + turn_offset * N
        return midturn


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
        self.start_angle = None

    def start(self):
        self.turtle.stop()
        self.start_angle = self.turtle.get_current_angle()
        if self.window:
            self.w_bin = Window("FindTwoSticks")

    def perform(self):
        Activity.perform_init(self)

        # Process image
        hsv = self.turtle.get_hsv_image()
        bin_img = img_threshold(hsv, self.color)
        sticks = self.driver.turtle.get_segments(self.color, bin_img=bin_img, min_area=GATE_STICK_MIN_AREA)

        # Testing window
        if self.window:
            self.w_bin.show(bin_to_rgb(bin_img))

        if sticks.count < 2:
            self.turtle.set_speed(0, self.dir * self.speed)
            return self.continue_search()

        # Pick A,B
        args = np.argsort(sticks.areas())
        A = args[-1]
        B = args[-2]

        # # Check area diff
        # if (abs(sticks.area(A) - sticks.area(B))) > MAX_GATE_AREA_DIFF:
        #     print("AREA DIFF TOO LARGE")  #TODO
        #     self.turtle.set_speed(0, self.dir * self.speed)
        #     return self.continue_search()

        # Center on sticks
        A_centroid = sticks.centroids[A]
        B_centroid = sticks.centroids[B]

        center = (A_centroid + B_centroid) / 2
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
            angle = (self.turtle.get_current_angle() - self.start_angle)
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
        angle = self.turtle.get_current_angle()
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

        # Make sure A left, B right
        args = np.argsort(sticks.areas())
        A = sticks.coors[args[-1]]
        B = sticks.coors[args[-2]]
        if A[0] > B[0]:
            tmp = A
            A = B
            B = tmp

        # Transform coordinates into real world.
        current_position = self.turtle.get_current_position()
        A_real = transform_coors(current_position, A)
        B_real = transform_coors(current_position, B)
        self.parent.ret = (A_real, B_real)
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


def transform_coors(bot_position, cam_coordinates):
    cam_coors = [cam_coordinates[0], cam_coordinates[2]]
    return rotate_vector(cam_coors, bot_position[2]) + bot_position[0:2]


def rotate_vector(vec, alpha):
    s, c = np.sin(alpha), np.cos(alpha)
    R = np.array([[c, -s], [s, c]])
    return np.matmul(R, vec)
