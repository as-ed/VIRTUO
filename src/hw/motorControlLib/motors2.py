from iotools import MotorControl
from iotools2 import MotorControl2
import smbus
from time import sleep
from datetime import datetime


class Motors(object):
    def __init__(self):
        print("Starting SMBus . . .")
        self.bus = smbus.SMBus(1)
        sleep(2)
        print("SMBus Started.")
        self.mc = MotorControl()
        self.mc2 = MotorControl2()
        self.encoder_address = 0x05
        self.encoder_register = 0x0
        self.num_encoder_ports = 6
        self.refresh_rate = 10  # refresh rate - reduces errors in i2c reading

    def move_motor(self, id, speed, board=1):
        if board == 1:
            self.mc.setMotor(id, speed)
        elif board == 2:
            self.mc2.setMotor(id, speed)
            # self.mc.setMotor(id, speed)

    def stop_motor(self, id, board=1):
        if board == 1:
            self.mc.stopMotor(id)
        elif board == 2:
            self.mc2.stopMotor(id)
        # self.mc.stopMotor(id)

    def stop_motors(self, board=1):
        if board == 1:
            self.mc.stopMotors()
        elif board == 2:
            self.mc2.stopMotors()
        # self.mc.stopMotors()
        # self.mc2.stopMotors()

    def __i2c_read_encoder(self):
        self.encoder_data = self.bus.read_i2c_block_data(self.encoder_address,
                                                         self.encoder_register,
                                                         self.num_encoder_ports)

    def read_encoder(self, id):
        self.__i2c_read_encoder()
        encoder_id_value = self.encoder_data[id]
        return encoder_id_value

    def print_encoder_data(self):
        self.__i2c_read_encoder()
        ts = str(datetime.now())
        print(self.encoder_data, ts.rjust(50, '.'))
