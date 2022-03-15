from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

WALKING_SPEED = 0.3

def stop(turtle):
    turtle.cmd_velocity(linear=0, angular=0)

def walk(turtle, speed=WALKING_SPEED):
    turtle.cmd_velocity(linear=speed, angular=0)

def walk_for(turtle, dist, speed=WALKING_SPEED):
    start = turtle.get_odometry()
    rate = Rate(10)

    turtle.cmd_velocity(linear=speed, angular=0)
    #while not turtle.is_shutting_down():
    #    rate.sleep()
    #    if (start - turtle.get_odometry())

