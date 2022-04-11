
RATE = 10
SLEEP = 1000 / RATE

HUE_MAX = 180

# POLE COLORS
GREEN = 0
BLUE = 1
RED = 2

G_HUE = 65
G_HUE_DIFF = 25
G_SATUR_MIN = 60
G_VAL_MIN = 30  #60

B_HUE = 100
B_HUE_DIFF = 25
B_SATUR_MIN = 200
B_VAL_MIN = 100

R_HUE = 0
R_HUE_DIFF = 10
R_SATUR_MIN = 150
R_VAL_MIN = 110

# POLE SHAPE
MIN_AREA = 1000
TARGET_RATIO = 5.35  # ~6 when truly in center, ~3.5 when on the far side
MAX_RATIO_DIFF = 1.85

# CAM
DEPTH_CAM_LAMBDA = 429.363066725704

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
