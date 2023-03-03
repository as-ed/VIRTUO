import util

class Motor:
    def __init__(self, mc, pins, encoder_pin=None, forward_values=None, start_sensor=None):
        self.mc = mc
        self.pins = pins

        self.encoder_pin = encoder_pin

        if not forward_values:
            forward_values = [100] * len(pins)

        self.forward_values = forward_values
        self.backward_values = [-v for v in forward_values]

        self.start_sensor = start_sensor

        self.angle = 0

    def move_motors(self, values):
        for pin, val in zip(self.pins, values):
            self.mc.move_motor(pin, val)

    def reset(self, direction=0, verbose=False):
        if not self.start_sensor:
            print("Err: no start sensor detected, reset sequence impossible")
            return

        # Resetting back to start if direction == 0
        values = self.backward_values if direction == 0 else self.forward_values

        self.move_motors(values)
        while self.start_sensor.read() == 0:
            pass

        self.move_motors([0] * len(self.pins))
            

    def read_angle_change(self, verbose=False):
        reading = self.mc.read_encoder(self.encoder_pin)

        if reading > 128:
            reading -= 256
        
        if verbose:
            print("encoer_reading:" +  str(reading))

        return reading

    def update_angle(self, verbose=False):
        reading = self.read_encoder_change()
        self.angle -= reading
        if verbose:
            print("angle:"+ str(self.angle))
        

    def set_angle(self, angle):
        self.angle = angle
        self.read_encoder_change()

    def move(self, values, duration):
        util.move_motors(self.mc, self.pins, values, duration)

    def forward(self, duration):
        util.move_motors(self.mc, self.pins, self.forward_values, duration)

    def backward(self, duration):
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

