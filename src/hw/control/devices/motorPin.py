import time


class MotorPin:
    def __init__(self, mc, pin, board):
        self.mc = mc
        self.pin = pin
        self.board = board

    def stop(self):
        self.move(0)

    def move(self, speed, duration=None):
        self.mc.move_motor(self.pin, speed, self.board)
        if duration is not None:
            time.sleep(duration)
            self.mc.move_motor(self.pin, 0, self.board)
