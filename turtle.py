from robolab_turtlebot import Turtlebot
import CONST
from camera import *

class Turtle:

    def __init__(self, rgb=True, pc=True, depth=True):
        self.bot = Turtlebot(rgb=rgb, pc=pc, depth=depth)

    def register_button_event_cb(self, cb):
        self.bot.register_button_event_cb(cb) # lambda msg: cb() if msg.state == 0 else None

    def get_rgb_image(self):
        return self.bot.get_rgb_image()

    def get_point_cloud(self, try_again=True, convert_to_bot=True):
        pc = self.bot.get_point_cloud()
        if try_again:
            while pc is None:
                pc = self.bot.get_point_cloud()
        if convert_to_bot:
            pc = pc_cam_to_bot(pc, self.get_depth_K())
        return pc

    def get_depth_K(self):
        return self.bot.get_depth_K()

    def get_segments(self,
        pc=None,
        min_area=CONST.MIN_AREA,
        target_ratio=CONST.TARGET_RATIO,
        max_ratio_diff=CONST.MAX_RATIO_DIFF,
        get_depth=True,
    ):
        rgb = self.get_rgb_image()
        hsv = rgb_to_hsv(rgb)
        bin = img_threshold(hsv)
        segments = segment(bin, min_area=min_area)
        segments = hw_ratio_filter(segments, target=target_ratio, max_diff=max_ratio_diff)
        if get_depth:
            if pc is None:
                pc = self.get_point_cloud()
            segments.get_depth(pc)
        return segments
    
    def play_sound():
        self.bot.play_sound(sound_id=4)
