from robolab_turtlebot import Turtlebot, Rate

turtle = Turtlebot(rgb=True)

def main():
    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

if __name__ == '__main__':
    img = turtle.get_rgb_image()
    print(img)

    main()
