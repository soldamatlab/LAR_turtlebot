import CONST

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    if sticks.count < 2:
        return

    max_sticks = np.argmax(sticks.areas())
