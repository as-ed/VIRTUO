from devices.motorPin import MotorPin
import time

class MainMotor:
    def __init__(self, mp):
        self.mp = mp

    def move(self, speed, duration):
        self.mp.move(speed)
        time.sleep(duration)
        self.mp.stop()