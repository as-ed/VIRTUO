from devices.motorPin import MotorPin
import time

class Slider:
    def __init__(self, pins, up=50, down=-50, time_unit=0.08):
        self.pins = pins
        self.up_speed = up
        self.down_speed = down
        self.time_unit=time_unit

    def move(self, speed, duration):
        [pin.move(speed) for pin in self.pins]
        time.sleep(duration)
        [pin.stop() for pin in self.pins]

    def up(self, duration):
        self.move(self.up_speed, duration)

    def down(self, duration):
        self.move(self.down_speed, duration)

    def down_step(self, steps):
        for _ in range(steps):
            time.sleep(0.1)
            self.down(self.time_unit)