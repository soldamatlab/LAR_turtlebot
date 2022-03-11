from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2
from scipy.misc import imsave

turtle = Turtlebot(rgb=True)

def main():
    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

if __name__ == '__main__':
    turtle.wait_for_rgb_image()
    rgb = turtle.get_rgb_image()
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    imsave("rgb.png", rgb)
    imsave("hsv.png", hsv)

    main()
