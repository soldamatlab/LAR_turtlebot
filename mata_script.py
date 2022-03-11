from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def do_for(duration, action):
    rate = Rate(1)
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

def dance():
    do_for(0.2, step)
    do_for(0.2, step)
    do_for(0.1, rot_left)
    do_for(0.1, rot_right)
    do_for(0.1, rot_left)



def bumper_cb(msg):
    # Print the event
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    print('{} bumper {}'.format(bumper, state))

    if state_names[msg.state] == 'PRESSED':
        dance()


def main():
    turtle.register_bumper_event_cb(bumper_cb)

    rate = Rate(1)
    while not turtle.is_shutting_down():
        rate.sleep()


if __name__ == '__main__':
    main()
