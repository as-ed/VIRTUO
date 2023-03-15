from devices.motorPin import MotorPin
import time

class Slider:
    def __init__(self, pins, up=60, down=-60):
        self.pins = pins
        self.up_speed = up
        self.down_speed = down

    def move(self, speed, duration):
        [pin.move(speed) for pin in self.pins]
        time.sleep(duration)
        [pin.stop() for pin in self.pins]

    def up(self, duration):
        self.move(self.up_speed, duration)

    def down(self, duration):
        self.move(self.down_speed, duration)