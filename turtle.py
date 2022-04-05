import numpy as np
from robolab_turtlebot import Turtlebot
import CONST
from camera import *

class Turtle:

    def __init__(self, rgb=True, pc=True, depth=True):
        self.bot = Turtlebot(rgb=rgb, pc=pc, depth=depth)

        self.linear = 0.
        self.angular = 0.

        self.bot.register_button_event_cb(self.button_cb)
        self.button_0 = lambda : None
        self.button_1 = lambda : None
        self.button_2 = lambda : None

    def set_speed(self, linear, angular):
        self.linear = linear
        self.angular = angular  # positive: left, negative: right
        self.bot.cmd_velocity(linear=linear, angular=angular)

    def stop(self):
        self.set_speed(0., 0.)

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

    def get_rgb_image(self):
        return self.bot.get_rgb_image()
    
    def get_hsv_image(self):
        rgb = self.get_rgb_image()
        return rgb_to_hsv(rgb)

    def get_point_cloud(self, convert_to_bot=True):
        pc = np.array(self.bot.get_point_cloud())
        if convert_to_bot:
            pc = pc_cam_to_bot(pc, self.get_depth_K())
        return pc

    def get_depth_K(self):
        return self.bot.get_depth_K()

    def get_segments(self, color,
        pc=None,
        min_area=CONST.MIN_AREA,
        target_ratio=CONST.TARGET_RATIO,
        max_ratio_diff=CONST.MAX_RATIO_DIFF,
        get_coors=True,
    ):
        hsv = self.get_hsv_image()
        bin = img_threshold(hsv, color)
        segments = segment(bin, min_area=min_area)
        segments = hw_ratio_filter(segments, target=target_ratio, max_diff=max_ratio_diff)
        if get_coors:
            if pc is None:
                pc = self.get_point_cloud(convert_to_bot=True)
            segments.get_coors(pc)
        return segments

    def play_sound(self):
        self.bot.play_sound(sound_id=4)

    def reset_odometry(self):
        self.bot.reset_odometry()

    def get_odometry(self):
        return self.bot.get_odometry()
