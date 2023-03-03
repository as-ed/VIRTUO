from fan import Fan

class FanGroup:
    def __init__(self, mc, fan_pins):
        self.fans = [Fan(mc, pin) for pin in fan_pins]

    def on(self):
        for fan in self.fans:
            fan.on()

    def off(self):
        for fan in self.fans:
            fan.off()

