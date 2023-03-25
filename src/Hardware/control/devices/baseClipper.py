from control.devices.motorPin import MotorPin
import time

class BaseClipper:
    def __init__(self, rotator, extender, rotator_forward, extender_forward, extend_time=0.4):
        self.rotator = rotator
        self.rotator_forward = rotator_forward


        self.extender = extender
        self.extender_forward = extender_forward
        self.extend_time = extend_time

    def extend(self):
        self.extender.move(self.extender_forward)
        time.sleep(self.extend_time)
        self.extender.stop()

    def retract(self):
        self.extender.move(-self.extender_forward, self.extend_time)

    def fall(self):
        self.rotator.move(self.rotator_forward)

    def rise(self):
        self.rotator.move(-self.rotator_forward)

    def float(self):
        self.rotator.move(0)

    def unclip(self, float=True, verbose=False):
        if verbose:
            print("[INFO] Base Clipper unclipping...")
        self.rise()
        self.retract()
        if float:
            time.sleep(0.2)
            self.float()

    def clip(self, float=True, verbose=False):
        if verbose:
            print("[INFO] Base Clipper clipping...")
        self.rise()
        self.extender.move(self.extender_forward)
        time.sleep(self.extend_time)
        self.fall()
        time.sleep(self.extend_time)
        self.extender.move(0)
        if float:
            time.sleep(0.2)
            self.float()





