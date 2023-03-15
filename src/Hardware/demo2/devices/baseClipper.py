from devices.motorPin import MotorPin
import time

class BaseClipper:
    def __init__(self, rotator, extender, rotator_forward, extender_forward, extend_time=0.5):
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




