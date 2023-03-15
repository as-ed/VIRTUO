from devices.motorPin import MotorPin
import time

class MainMotor:
    def __init__(self, mp, forward_speed=32, reset_sensor=None):
        self.mp = mp
        self.forward_speed = forward_speed
        self.backward_speed = -forward_speed
        self.reset_sensor = reset_sensor

    def move(self, speed, duration):
        self.mp.move(speed, duration)

    def forward(self, duration):
        self.move(self.forward_speed, duration)

    def backward(self, duration):
        self.move(self.backward_speed, duration)

    def reset(self, verbose=False):
        if self.reset_sensor is None:
            if verbose:
                print("[INFO] No reset sensor setup.")
            return

        self.mp.move(self.backward_speed)
        if verbose:
            print("[INFO] Starting reset.")

        while self.reset_sensor.read() == 0:
            pass

        if verbose:
            print("[INFO] Reset finished.")

        self.mp.stop()