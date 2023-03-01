class Fan:
    def __init__(self, mc, pin):
        self.mc = mc
        self.pin = pin

    def on(self):
        self.mc.move_motor(self.pin, 100)

    def off(self):
        self.mc.move_motor(self.pin, 0)

