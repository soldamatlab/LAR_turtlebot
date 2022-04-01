import CONST

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    if sticks.count < 2:
        return

    max_sticks = np.argmax(sticks.areas())
    A = sticks.coors[max_sticks[0]]
    B = sticks.coors[max_sticks[1]]
    print(A)
    print(B)
