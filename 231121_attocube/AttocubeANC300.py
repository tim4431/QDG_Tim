from pymeasure.instruments.attocube.anc300 import ANC300Controller,Axis
import threading

class AttocubeANC300:
    def __init__(self,address:str ="192.168.0.91"):
        self.anc300 = ANC300Controller("TCPIP::{:s}::7230::SOCKET".format(address),passwd="123456",axisnames=["axis_x","axis_y","axis_z"]) # type: ignore
        self.axisX = self.anc300.axis_x
        self.axisY = self.anc300.axis_y
        self.axisZ = self.anc300.axis_z
        self.x = 0
        self.y = 0
        self.z = 0

    @property
    def position(self):
        return (self.x,self.y,self.z)

    def check_steps(self,axis_name:str,steps:int)->bool:
        """
        Check if the steps is too large
        - True: continue
        - False: stop
        """
        MAX_STEP = {"X":100,"Y":200,"Z":200}
        if abs(steps) > MAX_STEP[axis_name]:
            a = input("Warning: steps {:s} = {:d} is too large, continue? (y/n)".format(axis_name,steps)).strip()
            if a=="y" or a=="Y" or a=="":
                return True
            else:
                print("Move cancelled")
                return False
        else:
            return True

    def move_x(self, steps: int,**kwargs):
        if self.check_steps("X",steps):
            self.axisX.move(steps,**kwargs)
            self.x += steps


    def move_y(self, steps: int,**kwargs):
        if self.check_steps("Y",steps):
            self.axisY.move(steps,**kwargs)
            self.y += steps

    def move_z(self,steps:int,**kwargs):
        if self.check_steps("Z",steps):
            self.axisZ.move(steps,**kwargs)
            self.z += steps

    def move_steps(self,stepsX:int,stepsY:int,stepsZ:int,**kwargs):
        self.move_x(stepsX,**kwargs)
        self.move_y(stepsY,**kwargs)
        self.move_z(stepsZ,**kwargs)

    def move_to(self,x:int,y:int,z:int,**kwargs):
        self.move_steps(x-self.x,y-self.y,z-self.z,**kwargs)

    def stop(self):
        self.anc300.stop_all()

if __name__ == "__main__":
    anc300 = AttocubeANC300()
    anc300.axisY.frequency=80
    anc300.axisY.voltage=30

