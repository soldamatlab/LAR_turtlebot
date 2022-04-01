
# POLE COLOR
GREEN = 65  # 45 - 75
G_HUE_DIFF = 25
G_SATUR_MIN = 60
G_VAL_MIN = 60

BLUE = 100  # 95 - 
B_HUE_DIFF = 25
B_SATUR_MIN = 60
B_VAL_MIN = 60

RED = 5     #  0 - 
R_HUE_DIFF = 5
R_SATUR_MIN = 60
R_VAL_MIN = 60

# POLE SEGMENT
MIN_AREA = 1000
TARGET_RATIO = 5.35 # ~6 when truly in center, ~3.5 when on the far side
MAX_RATIO_DIFF = 1.85


def get_color_consts(color):
    if color == 0:
        target_hue = GREEN
        hue_diff = G_HUE_DIFF
        satur_min = G_SATUR_MIN
        val_min = G_VAL_MIN
    elif color == 1:
        target_hue = BLUE
        hue_diff = B_HUE_DIFF
        satur_min = B_SATUR_MIN
        val_min = B_VAL_MIN
    elif color == 2:
        target_hue = RED
        hue_diff = R_HUE_DIFF
        satur_min = R_SATUR_MIN
        val_min = R_VAL_MIN
    else:
        print("ERROR:get_color_consts called with [color]=" + str(color) + ". Choose from [0,1,2].")
    
    return [target_hue, hue_diff, satur_min, val_min]
