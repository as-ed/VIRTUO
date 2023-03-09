import time
import gpioi

def move_motors(mc, motors, values, duration=None):
    for motor, value in zip(motors, values):
        mc.move_motor(motor, value)
    if duration:
        time.sleep(duration)
        for motor in motors:
            mc.move_motor(motor, 0)

def read_safe_int(prompt, error="Input not int"):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            pass

def read_y_n(prompt):
    while True:
        ans = input(prompt)
        if ans == 'y':
            return True
        elif ans == 'n':
            return False

def setup_motor():
    pins = []
    forward_values = []
    while read_y_n("Add another motor pin? (y/n)"):
        pins += read_safe_int("Pin:")
        forward_values += read_safe_int("Speed:")

    encoder_pin = None
    if read_y_n("Add encoder pin? (y/n)"):
        encoder_pin = read_safe_int("Pin:")

    start_sensor = None
    if read_y_n("Add start sensor? (y/n)"):
        start_sensor = read_safe_int("Pin:")

    return Motor(mc, pins, encoder_pin, forward_values, gpioi.Button(start_sensor))