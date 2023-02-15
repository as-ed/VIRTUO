from motors import Motors
from devices import *

import time

mc = Motors()

f = Fan(mc, 0)
m = Motor(mc, [2], 0, [-80], [80])
s = Motor(mc, [1, 3], 1, [60, 60], [-60, -60])


def turn_page():
    print("start up")
    m.set_angle(0)
    s.set_angle(0)

    print("setting up arm")
    m.move_to_angle(-8)
    s.move_forward(0.35)
    f.on()
   
    print("picking up page")
    m.move_to_angle(-18)
    time.sleep(1)

    print("resetting")
    m.move_to_angle(0)
    s.move_backward(0.8)
    f.off()

    

def main():

    pass


if __name__ == "__main__":
    main()

