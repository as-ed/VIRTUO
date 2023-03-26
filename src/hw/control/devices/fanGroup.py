from hw.control.devices.fan import Fan
from hw.control.devices.motorPin import MotorPin


class FanGroup:
    def __init__(self, mc, fan_pins, board=1):
        self.fans = [Fan(MotorPin(mc, pin, board)) for pin in fan_pins]

    def on(self):
        for fan in self.fans:
            fan.on()

    def off(self):
        for fan in self.fans:
            fan.off()
