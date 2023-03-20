import motors2

from devices import *
from gpioi import *
from util import *

import time

mc = motors2.Motors()


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
tcr = TopClipper(MotorPin(mc, 0, 1), -50)
tcl = TopClipper(MotorPin(mc, 4, 1), 50)

def stop():
    mc.stop_motors(1)
    mc.stop_motors(2)

def turn_page(steps=10, verbose=False):
    mm.reset()

    # Move arm to right angle
    mm.to_angle(4, verbose=verbose)

    # R clipper up
    tcr.unclip(verbose=verbose)

    # Set Slider to correct height
    if verbose:
        print("[INFO] Moving slider down...")
    s.down_step(steps)

    # Fans on
    if verbose:
        print("[INFO] Turing fans on...")
    f.on()

    # Move onto page
    if verbose:
        print("[INFO] Moving onto page...")
    mm.to_angle(0, verbose=verbose)

    # Wait
    if verbose:
        print("[INFO] Waiting for page to attach...")
    time.sleep(1)

    # Raise page
    if verbose:
        print("[INFO] Raising page...")
    mm.to_angle(3, verbose=verbose)

    # R clipper falls
    tcr.clip(verbose=verbose)

    # Base clipper raises
    bc.unclip(verbose=verbose)

    # Turing page
    mm.to_angle(6, verbose=verbose)

    # Base clipper falls
    bc.clip(verbose=verbose)

    # Fans off
    if verbose:
        print("[INFO] Turning fans off...")
    f.off()

    # Raise slider
    if verbose:
        print("[INFO] Raising slider...")
    s.up(0.5)

    # Back to 2
    mm.to_angle(3, verbose=verbose)
    s.down(0.5)
    tcl.unclip(verbose=verbose)
    mm.to_angle(5)
    tcl.clip(verbose=verbose)
    mm.to_angle(3)
    s.up(0.5)

    #Resetting
    if verbose:
        print("[INFO] Resetting...")
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
    tcr.clip()
    tcl.clip()
    mm.reset(verbose=verbose)


    mc.stop_motors(1)
    mc.stop_motors(2)

def calibrate_slider(time_unit=0.08, slider_width=8, total_height=16, verbose=False):
    mm.reset(verbose=verbose)
    mm.to_angle(2, verbose=verbose)

    for i in range(1, total_height):
        if verbose:
            print("[INFO] Checking height {height}".format(height=i))
        for _ in range(i):
            s.down(time_unit)
            time.sleep(0.1)

        mm.to_angle(0)
        correct_height = input("Active sensor?") == 'y'
        mm.to_angle(2)
        s.up(0.5)

        if correct_height:
            i += slider_width
            if verbose:
                print("[INFO] Height found as {movements} movements lasting {time_unit}".format(movements=i, time_unit=time_unit))
            return i








def main():
    stop()

if __name__ == "__main__":
    main()

