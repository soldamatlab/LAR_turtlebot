from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def do_for(duration, action):
    rate = Rate(10)
    t = get_time()
    while get_time() - t < duration:
        action()
        rate.sleep()

def step():
    turtle.cmd_velocity(linear=0.1, angular=0)

def rot_left():
    turtle.cmd_velocity(linear=0, angular=1)

def rot_right():
    turtle.cmd_velocity(linear=0, angular=-1)

def stop():
    turtle.cmd_velocity(linear=0, angular=0)

def dance():
    do_for(0.5, step)
    do_for(0.1, stop)
    do_for(0.5, step)
    do_for(0.25, rot_left)
    do_for(0.25, rot_right)
    do_for(0.25, rot_left)
    stop()


if __name__ == '__main__':
    dance()
