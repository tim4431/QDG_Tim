# https://github.com/mgraupe/SutterMP285/blob/master/sutterMP285.py#L6
#
import serial
import struct
import time
import sys
from numpy import *
import time 


class SutterMP285:

    def __init__(self, port='COM7', timeout=5):
        ''' Initialize serial connection with 5s timeout
            Set velocity to 200 '''
        self.ser = serial.Serial(port=port, baudrate=9600,
                                    bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE, timeout=timeout)
        self.connected = 1
        self.setVelocity(200, 10)
        self.updatePanel()  # update controller panel
        (self.stepMult, self.currentVelocity, self.vScaleFactor) = self.getStatus()

    def getPosition(self):
        ''' Get a list of format (x,y,z) for current stage position '''
        self.ser.write(b'c\r') # send command to get position
        xyzb = self.ser.read(13) # read position from controller
        # convert bytes into 'signed long' numbers
        xyz_um = array(struct.unpack('lll', xyzb[:12]))/self.stepMult
        return (xyz_um[0], xyz_um[1], xyz_um[2])

    def get_x_position(self):
        ''' Returns the x coordinate '''
        self.ser.write(b'c\r')
        xyzb = self.ser.read(13)
        xyz_um = array(struct.unpack('lll', xyzb[:12]))/self.stepMult
        return xyz_um[0]
    def get_y_position(self):
        ''' Returns the y coordinate '''
        self.ser.write(b'c\r')
        xyzb = self.ser.read(13)
        xyz_um = array(struct.unpack('lll', xyzb[:12]))/self.stepMult
        return xyz_um[1]
    def get_z_position(self):
        ''' Returns the z coordinate '''
        self.ser.write(b'c\r')
        xyzb = self.ser.read(13)
        xyz_um = array(struct.unpack('lll', xyzb[:12]))/self.stepMult
        return xyz_um[2]

    def set_x_position(self, x, read = False):
        ''' Sets the x coordinate '''
        xyz = self.getPosition()
        pos = (x, xyz[1], xyz[2])
        # convert integer values into bytes
        xyzb = struct.pack('lll', int(pos[0]*self.stepMult), int(pos[1]*self.stepMult), int(pos[2]*self.stepMult))  
        self.ser.write(b'm'+xyzb+b'\r')
        self.ser.read(1) # reading a carriage return?
        if read:
            cr = []
            cr = self.ser.read(1)  # read carriage return and ignore
               
    def set_y_position(self, y, read = False):
        ''' Sets the y coordinate '''
        xyz = self.getPosition()
        pos = (xyz[0], y, xyz[2])
        # convert integer values into bytes
        xyzb = struct.pack('lll', int(pos[0]*self.stepMult), int(pos[1]*self.stepMult), int(pos[2]*self.stepMult))  
        self.ser.write(b'm'+xyzb+b'\r')
        self.ser.read(1) # reading a carriage return?
        if read:
            cr = []
            cr = self.ser.read(1)  # read carriage return and ignore
    def set_z_position(self, z, read = False):
        ''' Sets the z coordinate '''
        xyz = self.getPosition()
        pos = (xyz[0], xyz[1], z)
        # convert integer values into bytes
        xyzb = struct.pack('lll', int(pos[0]*self.stepMult), int(pos[1]*self.stepMult), int(pos[2]*self.stepMult))  
        self.ser.write(b'm'+xyzb+b'\r')
        self.ser.read(1) # reading a carriage return?
        if read:
            cr = []
            cr = self.ser.read(1)  # read carriage return and ignore

    def setPosition(self, pos, read = False):
        ''' Sets the position to (x,y,z) = pos '''
        if len(pos) != 3:
            print('Length of position argument has to be three')
            sys.exit(1)
        xyzb = struct.pack('lll', int(pos[0]*self.stepMult), int(pos[1]*self.stepMult), int(pos[2]*self.stepMult))
        # send position to controller; add the "m" and the CR to create the move command
        self.ser.write(b'm'+xyzb+b'\r')
        self.ser.read(1) # reading a carriage return?
        if read:
            cr = []
            cr = self.ser.read(1)  # read carriage return and ignore

    def setVelocity(self, Vel, vScalF=10):
        ''' Set the velocity '''
        # Change velocity command 'V'xxCR where xx= unsigned short (16bit) int velocity
        # set by bits 14 to 0, and bit 15 indicates ustep resolution  0=10, 1=50 uSteps/step
        # V is ascii 86.'''
		
		#convert velocity into unsigned short - 2-byte - integeter
        velb = struct.pack('H', int(Vel))
        # change last bit of 2nd byte to 1 for ustep resolution = 50
        if vScalF == 50:
            velb2 = struct.unpack('B', velb[1:])[0] + 128 # double()
            velb = velb[0:1] + struct.pack('B', velb2)
        self.ser.write(b'V'+velb+b'\r')
        self.ser.read(1)
        self.getStatus()
    
    def updatePanel(self):
        ''' causes the Sutter to display the XYZ info on the front panel '''
        self.ser.write(b'n\r')  # Sutter replies with a CR
        self.ser.read(1)  # read and ignore the carriage return

    def setOrigin(self):
        ''' sets the origin of the coordinate system to the current position '''
        self.ser.write(b'o\r')  # Sutter replies with a CR
        self.ser.read(1)  # read and ignor the carrage return
 
    def sendReset(self):
        ''' Resets the controller '''
        self.ser.write(b'r\r')  # Sutter does not reply
    
    def getStatus(self):
        ''' Queries the status of the controller '''
        self.ser.write(b's\r')  # send status command
        rrr = self.ser.read(32) # read return of 32 bytes without carriage return
        self.ser.read(1) # read and ignore the carriage return
        statusbytes = struct.unpack(32*'B', rrr)
        # the value of STEP_MUL ("Multiplier yields msteps/nm") is at bytes 25 & 26
        self.stepMult = double(statusbytes[25])*256 + double(statusbytes[24])
        # the value of "XSPEED"  and scale factor is at bytes 29 & 30
        if statusbytes[29] > 127:
            self.vScaleFactor = 50
        else:
            self.vScaleFactor = 10
        self.currentVelocity = double(
            127 & statusbytes[29])*256+double(statusbytes[28])
        return (self.stepMult, self.currentVelocity, self.vScaleFactor)
    
    def __del__(self):
        ''' Close the serial connection '''
        self.ser.close()