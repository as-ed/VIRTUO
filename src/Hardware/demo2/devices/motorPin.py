class MotorPin:
    def __init__(self, mc, pin, board):
        self.mc = mc
        self.pin = pin
        self.board = board

    def stop(self):
        self.move(0)

    def move(self, speed):
        mc.move_motor(self.pin, speed, self.board)