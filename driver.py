import CONST

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    print([sticks.area(i) for i in range(0, sticks.count)])

    if sticks.count < 2:
        return
