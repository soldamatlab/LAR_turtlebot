from __future__ import print_function
from robolab_turtlebot import Rate, get_time

def do_for(duration, action):
    rate = Rate(10)
    t = get_time()
    while get_time() - t < duration:
        action()
        rate.sleep()

def step(turtle):
    turtle.cmd_velocity(linear=0.1, angular=0)

def rot_left(turtle):
    turtle.cmd_velocity(linear=0, angular=1)

def rot_right(turtle):
    turtle.cmd_velocity(linear=0, angular=-1)

def stop(turtle):
    turtle.cmd_velocity(linear=0, angular=0)

def dance(turtlebot):
    turtlebot.play_sound()
    do_for(0.5, lambda: step(turtlebot))
    do_for(0.1, lambda: stop(turtlebot))
    do_for(0.5, lambda: step(turtlebot))
    do_for(0.25, lambda: rot_left(turtlebot))
    do_for(0.25, lambda: rot_right(turtlebot))
    do_for(0.25, lambda: rot_left(turtlebot))
    stop(turtlebot)
