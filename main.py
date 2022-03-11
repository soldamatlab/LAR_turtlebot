from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2

turtle = Turtlebot(rgb=True, pc=True, depth=True)


def main():
    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        # hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        window = 'view'

        cv2.namedWindow(window)
        cv2.imshow(window, rgb)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
