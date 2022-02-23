from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()
rate = Rate(10)

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def do_for(duration, action):
    t = get_time()
    while get_time() - t < duration:
        action()
        rate.sleep()

def step():
    turtle.cmd_velocity(linear=0.1, angular=0)

def rot1():
    turtle.cmd_velocity(linear=0, angular=1)

def rot2():
    turtle.cmd_velocity(linear=0, angular=-1)

def dance():
    do_for(0.2, step)
    do_for(0.2, step)
    do_for(0.1, rot1)
    do_for(0.1, rot2)
    do_for(0.1, rot1)



def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))

    if state_names[msg.state] == 'PRESSED':
        dance()


def main():
    # Register bumper callback
    turtle.register_bumper_event_cb(bumper_cb)

    # Do something, the program would end otherwise
    rate = Rate(1)
    while not turtle.is_shutting_down():
        rate.sleep()


if __name__ == '__main__':
    main()
