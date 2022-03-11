from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

from dance import dance

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def button_cb(msg):
    state = state_names[msg.state]
    print('{} button {}'.format(msg.button, state))

    if state_names[msg.state] == 'PRESSED':
        dance()

def bumper_cb(msg):
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    print('{} bumper {}'.format(bumper, state))

    if state_names[msg.state] == 'PRESSED':
        odometry = turtle.get_odometry()
        print('odometry: {}'.format(odometry))

turtle = Turtlebot()
def main():
    turtle.register_button_event_cb(button_cb)
    turtle.register_bumper_event_cb(bumper_cb)

    turtle.wait_for_odometry()
    turtle.reset_odometry()

    rate = Rate(10)
    while not turtle.is_shutting_down():
        rate.sleep()

if __name__ == '__main__':
    main()
