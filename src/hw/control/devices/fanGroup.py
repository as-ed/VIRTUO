from hw.control.devices.fan import Fan
from hw.control.devices.motorPin import MotorPin


class FanGroup:
    def __init__(self, mc, fan_pins, board=1, fan_speeds=[]):
        if len(fan_speeds) != len(fan_pins):
            fan_speeds = [80] * len(fan_pins)
        self.fans = [Fan(MotorPin(mc, pin, board, speed)) for pin, speed in zip(fan_pins, fan_speeds)]

    def on(self):
        for fan in self.fans:
            fan.on()

    def off(self):
        for fan in self.fans:
            fan.off()
