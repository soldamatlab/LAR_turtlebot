import CONST

def drive(turtle):
    sticks = turtle.get_segments(CONST.GREEN)

    print(sticks.params[:][4])

    if sticks.count < 2:
        return
