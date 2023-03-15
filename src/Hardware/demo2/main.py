import motors2

from devices import *
from gpioi import *
from util import *

import time

mc = motors2.Motors()
mc.stop_motors(1)
mc.stop_motors(2)

mm = MainMotor(MotorPin(mc, 1, 2),
               reset_sensor=Button(8),
               encoder_pin=EncoderPin(mc, 5))
f = FanGroup(mc, [1,2,3], 1)
s = Slider([MotorPin(mc, 0, 2), MotorPin(mc, 3, 2)])
bc = BaseClipper(
    MotorPin(mc, 5, 2),
    MotorPin(mc, 4, 2),
    100,-50)

ep = EncoderPin(mc, 5)

def turn_page(height_var=0.13, verbose=False):
    mm.to_angle(0)

    # R clipper up
    if verbose:
        print("[INFO] Raising L Clipper")

    # Move arm to right angle
    mm.to_angle(2, verbose=verbose)

    # Set Slider to correct height
    if verbose:
        print("[INFO] Moving slider down")
    s.down(height_var)

    # Fans on
    if verbose:
        print("[INFO] Turing fans on")
    f.on()

    # Move onto page
    if verbose:
        print("[INFO] Moving onto page")
    mm.to_angle(0, verbose=verbose)

    # Wait
    if verbose:
        print("[INFO] Waiting for page to attach")
    time.sleep(1)

    # Raise page
    if verbose:
        print("[INFO] Raising page")
    mm.to_angle(2, verbose=verbose)

    # R clipper falls

    # Base clipper raises
    if verbose:
        print("[INFO] Raising base clipper")
    bc.rise()
    time.sleep(0.5)
    bc.float()

    # Turing page
    if verbose:
        print("[INFO] Turning page")
    mm.to_angle(6, verbose=verbose)

    # Base clipper falls
    if verbose:
        print("[INFO] Lowering base clipper")
    bc.fall()
    time.sleep(0.5)
    bc.float()

    # Fans off
    if verbose:
        print("[INFO] Turning fans off")
    f.off()

    # Raise slider
    if verbose:
        print("[INFO] Raising slider")
    s.up(0.5)

    #Resetting
    if verbose:
        print("[INFO] Resetting")
    mm.reset(verbose=verbose)


def reset(verbose=False):
    if verbose:
        print("[INFO] Turning fans off")
    f.off()
    if verbose:
        print("[INFO] Resetting slider")
    s.up(0.5)
    if verbose:
        print("[INFO] Floating base clipper")
    bc.float()
    mm.reset(verbose=verbose)

    mc.stop_motors(1)
    mc.stop_motors(2)



def main():
    pass

if __name__ == "__main__":
    main()

