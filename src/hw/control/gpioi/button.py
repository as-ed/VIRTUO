import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Button:
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.IN)
        self.pin = pin

    def read(self):
        return GPIO.input(self.pin)
