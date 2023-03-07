from iotools import MotorControl
import smbus
from time import sleep
from datetime import datetime

class Motors(object):
	def __init__(self):
		print "Starting SMBus . . ."
		self.bus = smbus.SMBus(1)
		sleep(2)
		print "SMBus Started."
		self.mc = MotorControl()
		self.encoder_address = 0x05
		self.encoder_register = 0x0
		self.num_encoder_ports = 6
		self.refresh_rate = 10 #refresh rate - reduces errors in i2c reading

	def move_motor(self,id,speed):
		self.mc.setMotor(id, speed)

	def stop_motor(self,id):
		self.mc.stopMotor(id)

	def stop_motors(self):
		self.mc.stopMotors()

	def __i2c_read_encoder(self):
		self.encoder_data = self.bus.read_i2c_block_data(self.encoder_address, 	\
							self.encoder_register, 	\
							self.num_encoder_ports)
	def read_encoder(self,id):
		self.__i2c_read_encoder()
		encoder_id_value =self.encoder_data[id]
		return encoder_id_value

	def print_encoder_data(self):
		self.__i2c_read_encoder()
		ts = str(datetime.now())
		print self.encoder_data, ts.rjust(50,'.')
