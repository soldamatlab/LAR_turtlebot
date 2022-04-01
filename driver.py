import CONST

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    print(sticks.areas())

    if sticks.count < 2:
        return
