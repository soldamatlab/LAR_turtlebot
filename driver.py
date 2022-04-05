import CONST
import numpy as np

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    if sticks.count < 2:
        turtle.set_speed(0, np.pi / 12)
        return

    max_sticks = np.argsort(sticks.areas())
    A = sticks.coors[max_sticks[0]]
    B = sticks.coors[max_sticks[1]]
    print(str(A) + " ; " + str(B))

    turtle.set_speed(0, 0)
