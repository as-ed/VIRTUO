import time

from hw.control.devices.baseClipper import BaseClipper
from hw.control.devices.encoderPin import EncoderPin
from hw.control.devices.fanGroup import FanGroup
from hw.control.devices.mainMotor import MainMotor
from hw.control.devices.motorPin import MotorPin
from hw.control.devices.slider import Slider
from hw.control.devices.topClipper import TopClipper
from hw.control.gpioi import Button
import hw.motorControlLib.motors2 as motors2


mc = motors2.Motors()

mm = MainMotor(MotorPin(mc, 0, 2),
               reset_sensor=Button(10),
               encoder_pin=EncoderPin(mc, 5, True))
f = FanGroup(mc, [1, 2, 3], 1)
s = Slider([MotorPin(mc, 1, 2), MotorPin(mc, 2, 2)])
bc = BaseClipper(
    MotorPin(mc, 5, 1),
    MotorPin(mc, 3, 2),
    -15, 30)

ep = EncoderPin(mc, 5)
tcr = TopClipper(MotorPin(mc, 0, 1), 100)
tcl = TopClipper(MotorPin(mc, 4, 2), -100)


def stop():
    mc.stop_motors(1)
    mc.stop_motors(2)


def run_actions(actions, verbose=True, interrupt=False):
    for i, action in enumerate(actions):
        func, text = action
        if verbose:
            print("[INFO] Executing action {index} \"{text}\"".format(index=i, text=text))
        func()
        if interrupt:
            input()


def turn_page(down_var=0.55, verbose=True, interrupt=False):
    actions = [
        (lambda: time.sleep(0), "Turning page with down var {down_var}".format(down_var=down_var)),
        (lambda: mm.reset(verbose=verbose), "Making sure are is reset"),
        (lambda: bc.clip(verbose=verbose), "Making sure base is clipped"),
        (lambda: tcl.clip(verbose=verbose), "Making sure left pages are clipped"),
        (lambda: tcr.clip(verbose=verbose), "Making sure right pages are clipped"),
        (lambda: mm.to_angle(5, verbose=verbose), "Moving arm to neutral angle"),
        (lambda: s.down(down_var), "Moving slider down"),
        (lambda: tcl.unclip(verbose=verbose), "Unclipping page to be turned"),
        (lambda: f.on(), "Turning fan on"),
        (lambda: mm.to_angle(1, verbose=verbose), "Moving to pick up page"),
        (lambda: time.sleep(3), "Waiting for page to attach"),
        (lambda: mm.to_angle(2, verbose=verbose), "Making space for re-clipping"),
        (lambda: time.sleep(1), "Waiting for arm to stabilize"),
        (lambda: tcl.clip(verbose=verbose), "Re-clipping..."),
        (lambda: mm.to_angle(1, verbose=verbose), "Moving arm out of the way of base clipper"),
        (lambda: bc.unclip(verbose=verbose), "Unclipping base"),
        (lambda: mm.to_angle(8, verbose=verbose), "Moving past base clipper"),
        (lambda: bc.clip(verbose=verbose), "Clipping base"),
        (lambda: f.off(), "Fans off"),
        (lambda: s.up(2), "Moving slider up"),
        (lambda: mm.to_angle(4, verbose=verbose), "Moving over page"),
        (lambda: s.down(1.0), "Moving slider to push page"),
        (lambda: tcr.unclip(verbose=verbose), "Unclipping turned pages"),
        (lambda: mm.to_angle(9), "Pushing pages into side"),
        (lambda: tcr.clip(verbose=verbose), "Re-clipping turned pages"),
        (lambda: tcl.unclip(verbose=verbose), "Unclipping unturned pages"),
        (lambda: mm.to_angle(0, verbose=verbose), "Pushing unturned pages back"),
        (lambda: tcl.clip(verbose=verbose), "Re-clipping unturned pages"),
        (lambda: mm.to_angle(5, verbose=verbose), "Re-centering main arm"),
        (lambda: s.up(2), "Moving arm to base position"),
        (lambda: mm.reset(verbose=verbose), "Resetting arm"),
    ]

    run_actions(actions, verbose=verbose, interrupt=interrupt)


def load_book(verbose=True, interrupt=False):
   actions = [
       (lambda: mm.reset(verbose=verbose), "Resetting main motor"),
       (lambda: mm.to_angle(5, verbose=verbose), "Moving are to middle"),
       (lambda: s.up(2), "Making sure fans are out the way"),
       (lambda: tcl.unclip(verbose=verbose), "Unclipping left side"),
       (lambda: tcr.unclip(verbose=verbose), "Unclipping right side"),
       (lambda: bc.unclip(verbose=verbose), "Unclipping base"),
   ]

   run_actions(actions, verbose=verbose, interrupt=interrupt)


def reset(verbose=False):
    if verbose:
        print("[INFO] Turning fans off")
    f.off()
    if verbose:
        print("[INFO] Resetting slider")
    s.up(2.0)
    if verbose:
        print("[INFO] Floating base clipper")
    bc.float()
    #tcr.clip()
    #tcl.clip()
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
