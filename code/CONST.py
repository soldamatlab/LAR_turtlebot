
ROBOT_WIDTH = 0.35
STICK_WIDTH = 0.054

RATE = 10
SLEEP = 1000 / RATE

HUE_MAX = 180

# POLE COLORS
GREEN = 0
BLUE = 1
RED = 2

G_HUE = 65  # 45 - 85
G_HUE_DIFF = 25
G_SATUR_MIN = 80  # 30 -> 80  to reduce noise (dark parts of the floor)
G_VAL_MIN = 40#60  # 80 chips off dark bits of stick

B_HUE = 100
B_HUE_DIFF = 25
B_SATUR_MIN = 150#230  # tight to eliminate green, if softened -> make hue tighter
B_VAL_MIN = 40#80  # 90 and 100 work but chip off dark bits of stick

R_HUE = 2
R_HUE_DIFF = 8  # 25 accepts light wood color
R_SATUR_MIN = 150  # always observed over 160
R_VAL_MIN = 40#70  # 110 and 120 work but chip off dark bits of stick

# POLE SHAPE
MIN_AREA = 2500
TARGET_RATIO = 5.1  # 5.35  # ~6 when truly in center, ~3.5 when on the far side
MAX_RATIO_DIFF = 3  # 1.85

# CAM
DEPTH_CAM_OFFSET = (-0.03) + (-0.01)

# UTILS
def get_color_consts(color):
    if color == GREEN:
        target_hue = G_HUE
        hue_diff = G_HUE_DIFF
        satur_min = G_SATUR_MIN
        val_min = G_VAL_MIN
    elif color == BLUE:
        target_hue = B_HUE
        hue_diff = B_HUE_DIFF
        satur_min = B_SATUR_MIN
        val_min = B_VAL_MIN
    elif color == RED:
        target_hue = R_HUE
        hue_diff = R_HUE_DIFF
        satur_min = R_SATUR_MIN
        val_min = R_VAL_MIN
    else:
        print("ERROR:get_color_consts called with [color]=" + str(color) + ". Choose from [0,1,2].")
    return [target_hue, hue_diff, satur_min, val_min]
