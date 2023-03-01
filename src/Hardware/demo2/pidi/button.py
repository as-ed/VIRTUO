import RPi.GPIO as GPIO

class Button:
    def __init__(self, pin):
        GPIO.setupt(pin, GPIO.IN)
        self.pin = pin

    def read(self):
        return GPIO.input(self.pin)
