class EncoderPin:
    def __init__(self, mc, pin, inverted=False):
        self.mc = mc
        self.pin = pin
        self.inverted = inverted
        self.angle = 0

    def get_change(self, verbose=False):
        delta = self.mc.read_encoder(self.pin)
        if verbose:
            print("[INFO] delta " + str(delta))

        if delta > 128:
            delta -= 256

        if self.inverted:
            delta = -delta

        return delta

    def set_angle(self, angle):
        self.mc.read_encoder(self.pin)
        self.angle = angle

    def get_angle(self, verbose=False):
        self.update(verbose=verbose)
        return self.angle


    def update(self, verbose=False):
        self.angle += self.get_change()
        if verbose:
            print("[INFO] angle " + str(self.angle))