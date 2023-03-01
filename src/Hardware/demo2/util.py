import time

def move_motors(mc, motors, values, duration=None):
    for motor, value in zip(motors, values):
        mc.move_motor(motor, value)
    if duration:
        time.sleep(duration)
        for motor in motors:
            mc.move_motor(motor, 0)

