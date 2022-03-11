from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

from dance import dance

turtle = Turtlebot()

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def bumper_cb(msg):
    # Print the event
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    print('{} bumper {}'.format(bumper, state))

    if state_names[msg.state] == 'PRESSED':
        dance()

def main():
    turtle.register_bumper_event_cb(bumper_cb)

    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

if __name__ == '__main__':
    main()
