from pymeasure.instruments.attocube.anc300 import ANC300Controller, Axis
import threading
from fake_ancinstance import fakeANCController


class AttocubeANC300:
    def __init__(self, address: str = "192.168.0.91"):
        # self.anc300 = ANC300Controller("TCPIP::{:s}::7230::SOCKET".format(address), passwd="123456", axisnames=["axis_x", "axis_y", "axis_z"])  # type: ignore
        self.anc300 = fakeANCController()
        self.axisX = self.anc300.axis_x
        self.axisY = self.anc300.axis_y
        self.axisZ = self.anc300.axis_z
        self.x = int(0)
        self.y = int(0)
        self.z = int(0)

    @property
    def position(self):
        return (self.x, self.y, self.z)

    @position.setter
    def position(self, value):
        self.x, self.y, self.z = value

    @property
    def freq_x(self):
        return self.axisX.frequency

    @freq_x.setter
    def freq_x(self, value: int):
        self.axisX.frequency = int(value)

    @property
    def freq_y(self):
        return self.axisY.frequency

    @freq_y.setter
    def freq_y(self, value: int):
        self.axisY.frequency = int(value)

    @property
    def freq_z(self):
        return self.axisZ.frequency

    @freq_z.setter
    def freq_z(self, value: int):
        self.axisZ.frequency = int(value)

    @property
    def volt_x(self):
        return self.axisX.voltage

    @volt_x.setter
    def volt_x(self, value: float):
        self.axisX.voltage = float(value)

    @property
    def volt_y(self):
        return self.axisY.voltage

    @volt_y.setter
    def volt_y(self, value: float):
        self.axisY.voltage = float(value)

    @property
    def volt_z(self):
        return self.axisZ.voltage

    @volt_z.setter
    def volt_z(self, value: float):
        self.axisZ.voltage = float(value)

    def set_to_origin(self):
        self.position = (0, 0, 0)

    def goto_origin(self):
        self.move_to(0, 0, 0)

    def check_steps(self, axis_name: str, steps: int) -> bool:
        """
        Check if the steps is too large
        - True: continue
        - False: stop
        """
        MAX_STEP = {"X": 100, "Y": 200, "Z": 200}
        if abs(steps) > MAX_STEP[axis_name]:
            a = input(
                "Warning: steps {:s} = {:d} is too large, continue? (y/n)".format(
                    axis_name, steps
                )
            ).strip()
            if a == "y" or a == "Y" or a == "":
                return True
            else:
                print("Move cancelled")
                return False
        else:
            return True

    def move_x(self, steps: int, **kwargs):
        if self.check_steps("X", steps):
            self.axisX.move(steps, **kwargs)
            self.x += steps

    def move_y(self, steps: int, **kwargs):
        if self.check_steps("Y", steps):
            self.axisY.move(steps, **kwargs)
            self.y += steps

    def move_z(self, steps: int, **kwargs):
        if self.check_steps("Z", steps):
            self.axisZ.move(steps, **kwargs)
            self.z += steps

    def move(self, stepsX: int, stepsY: int, stepsZ: int, **kwargs):
        self.move_x(stepsX, **kwargs)
        self.move_y(stepsY, **kwargs)
        self.move_z(stepsZ, **kwargs)

    def move_to(self, x: int, y: int, z: int, **kwargs):
        self.move(x - self.x, y - self.y, z - self.z, **kwargs)

    # def stop(self):
    #     self.anc300.stop_all()


if __name__ == "__main__":
    anc300 = AttocubeANC300()
    anc300.move_x(10)  # X, +10 steps
    anc300.move_y(-10)  # Y, -10 steps
    anc300.move(10, 10, 10)  # X, Y, Z, +10 steps
    anc300.move_to(0, 0, 0)  # X, Y, Z, move to (0, 0, 0)
    # Note: above all methods are blocking
    # anc300.stop()  # stop all
    anc300.set_to_origin()  # set current position to (0, 0, 0)
    anc300.goto_origin()  # move to (0, 0, 0)
    print(anc300.position)  # get current position
    anc300.position = (10, 10, 10)  # set current position to (10, 10, 10)
    print(anc300.freq_x)  # get current frequency on X axis
    anc300.freq_x = 90  # set frequency on X axis to 1000 Hz
