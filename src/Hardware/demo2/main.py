import motors

from devices import *
from gpioi import *
from util import *

import time

mc = motors.Motors()

main_motor = Motor(mc, [0], None, [60], Button(8))
slider = Motor(mc, [4,5], None, [60,60], None)
fans = FanGroup(mc, [1,2,3])

def setup_main_motor():
    global main_motor
    main_motor = setup_motor()

def setup_slider():
    global slider
    slider = setup_motor()


def setup_fans():
    global fans

    pins = []
    while read_y_n("Add another fan pin? (y/n)"):
        pins += read_safe_int("Pin:")

    fans = FanGroup(mc, pins)

def setup():
    if read_y_n("Set up main motor? (y/n)"):
        setup_main_motor()

    if read_y_n("Set up slider? (y/n)"):
        setup_slider()

    if read_y_n("Set up fans? (y/n)"):
        setup_fans()

def turn_page():
    m.reset()

def main():
    pass

if __name__ == "__main__":
    main()

