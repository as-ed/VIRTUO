import motors2

from devices import *
from gpioi import *
from util import *

import time

mc = motors2.Motors()


mm = MainMotor(MotorPin(mc, 0, 2),
               reset_sensor=Button(8),
               encoder_pin=EncoderPin(mc, 5))
f = FanGroup(mc, [1,2,3], 1)
s = Slider([MotorPin(mc, 1, 2), MotorPin(mc, 2, 2)])
bc = BaseClipper(
    MotorPin(mc, 5, 1),
    MotorPin(mc, 3, 2),
    -100,-50)

ep = EncoderPin(mc, 5)
tcl = TopClipper(MotorPin(mc, 0, 1), 100)
tcr = TopClipper(MotorPin(mc, 5, 2), 100)

def stop():
    mc.stop_motors(1)
    mc.stop_motors(2)

def inter(i=True):
    if i:
        input()

def turn_page(verbose=True, interrupt=True):
    # TODO: Reset Position...
    if input("Is the system reset?(y/n)") != 'y':
        return

    actions = [
        lambda: mm.to_angle(15, verbose=verbose),
        lambda: tcr.unclip(verbose=verbose),
        lambda: f.on(),
        lambda: s.down(0.6),
        lambda: mm.to_angle(30, verbose=verbose),
        lambda: time.sleep(1),
        lambda: mm.to_angle(25, verbose=verbose),
        lambda: tcr.clip(verbose=verbose),
        lambda: bc.unclip(verbose=verbose),
        lambda: mm.to_angle(20, verbose=verbose),
        lambda: bc.clip(verbose=verbose),
        lambda: f.off(),
        lambda: s.up(1.0),
        lambda: mm.to_angle(25, verbose=verbose),
        lambda: tcr.unclip(verbose=verbose),
        lambda: s.down(2.0),
        lambda: mm.to_angle(10, verbose=verbose),
        lambda: tcr.clip(verbose=verbose),
        lambda: mm.to_angle(15, verbose=verbose),
        lambda: s.up(2.5),
        lambda: mm.to_angle(0, verbose=verbose)
    ]

    for a in actions:
        if verbose:
            print("[INFO] Executing action " + str(actions.index(a)))
        a()
        inter(interrupt)




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

