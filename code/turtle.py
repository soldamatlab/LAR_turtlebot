import numpy as np
from robolab_turtlebot import Turtlebot
import CONST
from camera import *
from buttons import bumper_cb
import time

INFO = False
WAIT_FOR_ODO = 0.4  # seconds


class Turtle:

    def __init__(self, rgb=True, pc=True, depth=True):
        self.bot = Turtlebot(rgb=rgb, pc=pc, depth=depth)

        self.linear = 0.
        self.angular = 0.

        self.bot.register_button_event_cb(self.button_cb)
        self.button_0 = lambda: None
        self.button_1 = lambda: None
        self.button_2 = lambda: None
        self.bot.register_bumper_event_cb(self.bumper_cb)
        self.bumper_left = lambda: None
        self.bumper_center = lambda: None
        self.bumper_right = lambda: None

    def set_speed(self, linear, angular):
        self.linear = linear
        self.angular = angular  # positive: left, negative: right

    # DON'T SPAM
    def keep_speed(self):
        if INFO: print("TURTLE_SPEED: " + str(self.linear) + " " + str(self.angular))
        self.bot.cmd_velocity(linear=self.linear, angular=self.angular)

    # DON'T SPAM
    def stop(self):
        self.set_speed(0., 0.)
        self.keep_speed()

    def button_cb(self, msg):
        if msg.state == 1:
            if msg.button == 0:
                self.button_0()
            elif msg.button == 1:
                self.button_1()
            elif msg.button == 2:
                self.button_2()

    def register_button_cb(self, button, cb):
        if button == 0:
            self.button_0 = cb
        elif button == 1:
            self.button_1 = cb
        elif button == 2:
            self.button_2 = cb

    def bumper_cb(self, msg):
        if msg.bumper == 0:
            self.bumper_left()
        elif msg.bumper == 1:
            self.bumper_center()
        elif msg.bumper == 2:
            self.bumper_right()

    def register_bumper_cb(self, bumper, cb):
        if bumper == "ALL":
            self.register_bumper_cb("LEFT", cb)
            self.register_bumper_cb("CENTER", cb)
            self.register_bumper_cb("RIGHT", cb)
        elif bumper == "LEFT":
            self.bumper_left = cb
        elif bumper == "CENTER":
            self.bumper_center = cb
        elif bumper == "RIGHT":
            self.bumper_right = cb

    def get_rgb_image(self):
        return self.bot.get_rgb_image()
    
    def get_hsv_image(self):
        rgb = self.get_rgb_image()
        return rgb_to_hsv(rgb)

    def get_point_cloud(self, convert_to_bot=True):
        pc = np.array(self.bot.get_point_cloud())
        if convert_to_bot:
            pc = pc_cam_to_bot(pc)
        return pc

    def get_depth_K(self):
        return self.bot.get_depth_K()

    def get_segments(self, color,
        hsv_img=None,
        bin_img=None,
        pc=None,
        min_area=CONST.MIN_AREA,
        target_ratio=CONST.TARGET_RATIO,
        max_ratio_diff=CONST.MAX_RATIO_DIFF,
        get_coors=False,
        get_dists=False,
        info=False,
    ):
        if bin_img is None:
            if hsv_img is None:
                hsv_img = self.get_hsv_image()
            bin_img = img_threshold(hsv_img, color)
        segments = segment(bin_img, min_area=min_area, info=info)
        segments = hw_ratio_filter(segments, target=target_ratio, max_diff=max_ratio_diff, info=info)
        if get_coors:
            if pc is None:
                pc = self.get_point_cloud(convert_to_bot=True)
            segments.calculate_coors(pc)
            if get_dists:
                segments.calculate_dists()
        return segments

    def play_sound(self):
        self.bot.play_sound(sound_id=4)

    def reset_odometry(self):
        self.bot.reset_odometry()
        time.sleep(WAIT_FOR_ODO)

    # x->forward, y->sideways, z->angle
    # z ... <-pi,+pi>, left: positive, right: negative, forward: zero, backwards: +-pi
    # y ... left positive ? TODO
    def get_odometry(self):
        return self.bot.get_odometry()

    # x, z, angle
    def get_current_position(self):
        odo = self.get_odometry()
        return np.array([-odo[1], odo[0], odo[2]])

    # [x, z]
    # x ... right, z ... forward
    def get_current_coors(self):
        odo = self.get_odometry()
        return np.array([-odo[1], odo[0]])

    # <-pi,+pi>, left: positive, right: negative, forward: zero, backwards: +-pi
    def get_current_angle(self):
        odo = self.get_odometry()
        return odo[2]
