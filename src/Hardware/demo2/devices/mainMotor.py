from devices.motorPin import MotorPin
import time

class MainMotor:
    def __init__(self, mp, forward_speed=-50, reset_sensor=None, encoder_pin=None):
        self.mp = mp
        self.forward_speed = forward_speed
        self.backward_speed = -forward_speed
        self.reset_sensor = reset_sensor

        self.ep = encoder_pin

    def move(self, speed, duration):
        self.mp.move(speed, duration)

    def forward(self, duration):
        self.move(self.forward_speed, duration)

    def backward(self, duration):
        self.move(self.backward_speed, duration)

    def set_angle(self, angle):
        self.ep.set_angle(angle)

    def to_angle(self, target_angle, verbose=False):
        if self.ep is None:
            if verbose:
                print("[INFO] no encoder pin set up")
            return

        target_angle = max(target_angle, 0)
        if verbose:
            print("[INFO] moving to angle " + str(target_angle))

        angle = self.ep.get_angle(verbose=verbose)
        if angle > target_angle:
            while angle > target_angle:
                self.backward(0.2)
                time.sleep(0.1)
                angle = self.ep.get_angle(verbose=verbose)
        else:
            while angle < target_angle:
                self.forward(0.2)
                time.sleep(0.1)
                angle = self.ep.get_angle(verbose=verbose)

        if verbose:
            print("[INFO] moved to angle " + str(angle))

    def get_angle(self, verbose=False):
        return self.ep.get_angle(verbose=verbose)

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

        time.sleep(0.5)

        self.ep.set_angle(0)
        self.mp.stop()