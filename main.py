from __future__ import print_function
from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2
from camera_controller import Window

turtle = Turtlebot(rgb=True, pc=True, depth=True)


def button_cb(msg):
    print('button cb')
    if msg.state == 0:
        rgb = turtle.get_rgb_image()
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        shape = hsv.shape
        print(hsv[np.astype(shape[0]/2, int),np.astype(shape[1]/2, int),:])


def main():
    turtle.register_button_event_cb(button_cb)

    rate = Rate(10)
    window = Window("view")

    while not turtle.is_shutting_down():
        rate.sleep()

        rgb = turtle.get_rgb_image()
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        window.show(hsv)


if __name__ == '__main__':
    main()
