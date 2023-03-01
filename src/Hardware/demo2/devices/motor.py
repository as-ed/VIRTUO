import util

class Motor:
    def __init__(self, mc, pins, encoder_pin, forward_values, backward_values):
        self.mc = mc
        self.pins = pins
        self.encoder_pin = encoder_pin
        self.forward_values = forward_values
        self.backward_values = backward_values

        self.angle = 0


    def reset(self, values, check_rate=0.1, check_repeat=5, verbose=False):
        remaining = check_repeat
        while(True):
            self.move(values, check_rate)

            if self.read_encoder_change(verbose=verbose) == 0:
                remaining -= 1
            else:
                remaining = check_repeat

            if remaining == 0:
                break

    def read_encoder_change(self, verbose=False):
        reading = self.mc.read_encoder(self.encoder_pin)

        if reading > 128:
            reading -= 256
        
        if verbose:
            print("encoer_reading:" +  str(reading))

        return reading

    def update_angle(self, verbose):
        reading = self.read_encoder_change()
        self.angle -= reading
        if verbose:
            print("angle:"+ str(self.angle))
        

    def set_angle(self, angle):
        self.angle = angle
        self.read_encoder_change()

    def move(self, values, duration):
        util.move_motors(self.mc, self.pins, values, duration)

    def move_forward(self, duration):
        util.move_motors(self.mc, self.pins, self.forward_values, duration)

    def move_backward(self, duration):
        util.move_motors(self.mc, self.pins, self.backward_values, duration)

    def move_to_angle(self, angle, verbose=False):
        self.update_angle(verbose)
        while True:
            if self.angle < angle:
                util.move_motors(self.mc, self.pins, self.forward_values)
            elif self.angle > angle:
                util.move_motors(self.mc, self.pins, self.backward_values)
            else:
                for p in self.pins:
                    self.mc.move_motor(p, 0)
                break

            self.update_angle(verbose)

