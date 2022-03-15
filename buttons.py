from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

# ___ Usage _______________________________________
# Callback examples:
def button_cb(msg):
    state = state_names[msg.state]
    print('button {} {}'.format(msg.button, state))

    if state_names[msg.state] == 'PRESSED':
        print("Do something")

def bumper_cb(msg):
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    print('{} bumper {}'.format(bumper, state))

    if state_names[msg.state] == 'PRESSED':
        print("Do something")

# Register callback with:
#turtle.register_button_event_cb(button_cb)
#turtle.register_bumper_event_cb(bumper_cb)

