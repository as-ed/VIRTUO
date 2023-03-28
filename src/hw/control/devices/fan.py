
class Fan:
    def __init__(self, pin, speed=80):
        self.pin = pin
        self.speed = speed

    def on(self):
        self.pin.move(self.speed)

    def off(self):
        self.pin.stop()
