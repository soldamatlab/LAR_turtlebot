from robolab_turtlebot import Turtlebot, Rate

turtle = Turtlebot(rgb=True)

def main():
    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

if __name__ == '__main__':
    turtle.wait_for_rgb_image()
    rgb = turtle.get_rgb_image()
    print(type(rgb))

    main()
