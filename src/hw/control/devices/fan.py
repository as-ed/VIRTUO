
class Fan:
    def __init__(self, pin):
        self.pin = pin

    def on(self):
        self.pin.move(100)

    def off(self):
        self.pin.stop()
