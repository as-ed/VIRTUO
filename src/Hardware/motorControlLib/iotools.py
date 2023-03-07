#!/usr/bin/python

import os
import time

import cv2
import numpy as np

import smbus2 as smbus
from picamera import PiCamera
from picamera.array import PiRGBArray


class Camera:
    __camera_resolution = {'low':    (160, 128),
                           'medium': (640, 480),
                           'high':   (800, 608)}

    def __init__(self, onRobot):
        self.__onRobot = onRobot
        self.__openCam = False

    def initCamera(self, camera='pi', resolution='low'):
        """
        Keyword arguments:
            camera -- which camera hardware to use:
                pi, logitech (default 'pi')

            resolution -- the camera resolution to use:
                low, medium, high (default 'low')
        """
        if resolution not in Camera.__camera_resolution:
            print('[ERROR] Camera.__init__(): Unknown \'{}\' camera resolution.'.format(resolution))
            return

        if camera == 'pi':
            self.__camera = PiCamera(resolution=Camera.__camera_resolution[resolution])
            self.__rawCapture = PiRGBArray(self.__camera, size=Camera.__camera_resolution[resolution])
            time.sleep(0.2)
            self.getFrame = self.__getFramePi
        elif camera == 'logitech':
            self.__openLogitech()
            self.__setLogitechResolution(resolution)
            self.getFrame = self.__getFrameLogitech
        else:
            print('[ERROR] Camera.__init__(): Unknown \'{}\' camera.'.format(camera))

        return self

    def imshow(self, wnd, img):
        if not self.__onRobot:
            if img.__class__ != np.ndarray:
                print('[ERROR] Camera.imshow(): Invalid image.')
                return False
            else:
                cv2.imshow(wnd, img)
                cv2.waitKey(1) & 0xFF

    def destroy(self):
        if self.__openCam:
            self.__cap.release()
        self.__openCam = False

    def __getFramePi(self):
        self.__camera.capture(self.__rawCapture, format='bgr', use_video_port=True)
        frame = self.__rawCapture.array
        self.__rawCapture.truncate(0)
        return frame

    def __getFrameLogitech(self):
        self.__cap.grab()
        (_, img) = self.__cap.retrieve()
        return img

    def __openLogitech(self):
        if not os.path.exists('/dev/video0'):
            return False
        self.__cap = cv2.VideoCapture()
        if not self.__cap.open(-1):
            return False
        self.__openCam = True

    def __setLogitechResolution(self, resolution):
        while not self.__openCam:
            print('Setting camera resolution to {} - {}'.format(resolution, self.__openCam))
            time.sleep(0.2)
        if self.__openCam:
            self.__cap.set(3, Camera.__camera_resolution[resolution][0])
            self.__cap.set(4, Camera.__camera_resolution[resolution][1])


class MotorControl:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address = 0x04

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


class ServoControl:
    __ready = False

    def __init__(self):
        # Create an advancedServo object
        try:
            self.__advancedServo = AdvancedServo()
        except RuntimeError as e:
            print('[ERROR] [ServoControl] Runtime Exception: %s' % e.details)
            return 1

        # set up our event handlers
        try:
            # logging example, uncomment to generate a log file
            #self.__advancedServo.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, 'phidgetlog.log')

            self.__advancedServo.setOnAttachHandler(self.__attached)
            self.__advancedServo.setOnDetachHandler(self.__detached)
            self.__advancedServo.setOnErrorhandler(self.__error)
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))
            return 1

        print('[INFO] [ServoControl] Opening phidget object....')

        try:
            self.__advancedServo.openPhidget()
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))
            return 1

        print('[INFO] [ServoControl] Waiting for attach....')

        try:
            self.__advancedServo.waitForAttach(10000)
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))
            try:
                self.__advancedServo.closePhidget()
            except PhidgetException as e:
                print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))
                return 1
            return 1
        else:
            # self.__DisplayDeviceInfo()
            pass

    def engage(self):
        if self.__ready:
            try:
                print('[INFO] [ServoControl] Engaging servo...')
                self.__advancedServo.setEngaged(0, True)
            except PhidgetException as e:
                print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))

    def disengage(self):
        if self.__ready:
            try:
                print('[INFO] [ServoControl] Disengaging servo...')
                self.__advancedServo.setEngaged(0, False)
                self.__ready = False
            except PhidgetException as e:
                print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))

    def setPosition(self, position):
        if self.__ready:
            try:
                position = np.clip(position,
                                   self.__advancedServo.getPositionMin(0),
                                   self.__advancedServo.getPositionMax(0))
                print('[INFO] [ServoControl] Moving servo to {}'.format(position))
                self.__advancedServo.setPosition(0, position)
            except PhidgetException as e:
                print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))

    def destroy(self):
        print('[INFO] [ServoControl] Closing advanced servo phidget...')

        try:
            self.disengage()
            self.__advancedServo.closePhidget()
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))
            return 1

    def __displayDeviceInfo(self):
        """
        Information Display Function
        """
        print('|------------|----------------------------------|--------------|------------|')
        print('|- Attached -|-              Type              -|- Serial No. -|-  Version -|')
        print('|------------|----------------------------------|--------------|------------|')
        print('|- %8s -|- %30s -|- %10d -|- %8d -|' % (self.__advancedServo.isAttached(),
                                                       self.__advancedServo.getDeviceName(),
                                                       self.__advancedServo.getSerialNum(),
                                                       self.__advancedServo.getDeviceVersion()))
        print('|------------|----------------------------------|--------------|------------|')
        print('Number of motors: %i' % (self.__advancedServo.getMotorCount()))

    def __attached(self, e):
        """
        Event Handler Callback Functions
        """
        attached = e.device
        print('[INFO] [ServoControl] Servo %i Attached!' % (attached.getSerialNum()))

        try:
            self.__advancedServo.setServoType(0, ServoTypes.PHIDGET_SERVO_HITEC_HS322HD)
            self.__advancedServo.setAcceleration(0, self.__advancedServo.getAccelerationMax(0))
            self.__advancedServo.setVelocityLimit(0, self.__advancedServo.getVelocityMax(0))
            self.__ready = True
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))

    def __detached(self, e):
        detached = e.device
        print('[INFO] [ServoControl] Servo %i Detached!' % (detached.getSerialNum()))
        self.__ready = False

    def __error(self, e):
        try:
            source = e.device
            print('[ERROR] Phidget Error %i: %s' % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print('[ERROR] Phidget Exception %i: %s' % (e.code, e.details))


class IOTools:
    __version = '2018a'

    def __init__(self, onRobot):
        print('[IOTools] R:SS IOTools ' + IOTools.__version)

        self.camera = Camera(onRobot)
        self.motor_control = MotorControl()

    def destroy(self):
        self.camera.destroy()
        self.motor_control.stopMotors()
