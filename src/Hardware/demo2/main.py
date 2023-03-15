import motors2

from devices import *
from gpioi import *
from util import *

import time

mc = motors2.Motors()
mc.stop_motors(1)
mc.stop_motors(2)

mm = MainMotor(MotorPin(mc, 1, 2), reset_sensor=Button(8))
f = FanGroup(mc, [1,2,3], 1)
s = Slider([MotorPin(mc, 0, 2), MotorPin(mc, 3, 2)])
bc = BaseClipper(
    MotorPin(mc, 5, 2),
    MotorPin(mc, 4, 2),
    100,-50)

def main():
    pass

if __name__ == "__main__":
    main()

