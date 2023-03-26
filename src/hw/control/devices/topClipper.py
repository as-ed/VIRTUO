import time


class TopClipper:
    def __init__(self, motor_pin, speed=100):
        self.mp = motor_pin
        self.speed = speed

    def clip(self, float=False, verbose=False):
        if verbose:
            print("[INFO] Top Clipper clipping...")
        self.mp.move(self.speed)
        if float:
            time.sleep(0.5)
            self.mp.stop()

    def unclip(self, verbose=True):
        if verbose:
            print("[INFO] Top Clipper unclipping...")
        self.mp.move(-self.speed, 0.5)
