import numpy as np

import smbus2 as smbus


class MotorControl2:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address = 0x06

    def setMotor(self, id, speed):
        """
        Mode 2 is Forward.
        Mode 3 is Backwards.
        """
        direction = 2 if speed >= 0 else 3
        speed = np.clip(abs(speed), 0, 100)
        byte1 = id << 5 | 24 | direction << 1
        byte2 = int(speed * 2.55)
        self.__write_block([byte1, byte2])

    def stopMotor(self, id):
        """
        Mode 0 floats the motor.
        """
        direction = 0
        byte1 = id << 5 | 16 | direction << 1
        self.__write(byte1)

    def stopMotors(self):
        """
        The motor board stops all motors if bit 0 is high.
        """
        print('[INFO] [MotorControl] Stopping all motors...')
        self.__write(0x01)

    def __write(self, value):
        try:
            self.bus.write_byte_data(self.address, 0x00, value)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))

    def __write_block(self, values):
        try:
            msg = smbus.i2c_msg.write(self.address, values)
            self.bus.i2c_rdwr(msg)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
