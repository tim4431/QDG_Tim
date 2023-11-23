from pymeasure.instruments.attocube.anc300 import ANC300Controller, Axis
import threading
from fake_ancinstance import fakeANCController
import time


class AttocubeANC300:
    def __init__(self, address: str = "192.168.0.91", commandline=True):
        self.address = address
        # self.anc300 = ANC300Controller(
        #     "TCPIP::{:s}::7230::SOCKET".format(self.address),
        #     passwd="123456",
        #     axisnames=["axis_x", "axis_y", "axis_z"], # type: ignore
        #     query_delay=0,
        # )  # type: ignore
        self.anc300 = fakeANCController()
        print(self.anc300.version)
        self.axisX = self.anc300.axis_x
        self.axisY = self.anc300.axis_y
        self.axisZ = self.anc300.axis_z
        self._commandline = commandline
        #
        self.displace_limit = [100, 600, 600]
        self._x = int(0)  # read only
        self._y = int(0)  # read only
        self._z = int(0)  # read only
        self.x_tar = int(0)  # read-write
        self.y_tar = int(0)  # read-write
        self.z_tar = int(0)  # read-write
        #
        self.freq_x = 500
        self.freq_y = 500
        self.freq_z = 500
        self.volt_x = 30
        self.volt_y = 30
        self.volt_z = 30
        #

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def position(self):
        return (self._x, self._y, self._z)

    @property
    def target(self):
        return (self.x_tar, self.y_tar, self.z_tar)

    @target.setter
    def target(self, value: tuple):
        self.x_tar, self.y_tar, self.z_tar = value

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
        self._x = 0
        self._y = 0
        self._z = 0
        self.x_tar = 0
        self.y_tar = 0
        self.z_tar = 0

    def goto_origin(self):
        self.move_to(0, 0, 0)

    def check_steps(self, axis_name: str, steps: int, force_move=False) -> bool:
        """
        Check if the steps is too large
        - True: continue
        - False: stop
        """
        MAX_STEP = {"X": 100, "Y": 600, "Z": 200}
        if abs(steps) > MAX_STEP[axis_name]:
            if not force_move and self._commandline:
                a = input(
                    "Warning: steps {:s} = {:d} is too large, continue? (y/n)".format(
                        axis_name, steps
                    )
                ).strip()
            elif not force_move and not self._commandline:
                a = "N"
            else:
                a = "Y"
            #
            if a == "y" or a == "Y" or a == "":
                return True
            else:
                print("Move cancelled")
                return False
        else:
            return True

    def _perform_move_x(self, steps: int, force_move=False):
        if force_move or self.check_steps("X", steps):
            self.axisX.move(steps)
            self._x += steps
            return True
        else:
            return False

    def _perform_move_y(self, steps: int, force_move=False):
        if force_move or self.check_steps("Y", steps):
            self.axisY.move(steps)
            self._y += steps
            return True
        else:
            return False

    def _perform_move_z(self, steps: int, force_move=False):
        if force_move or self.check_steps("Z", steps):
            self.axisZ.move(steps)
            self._z += steps
            return True
        else:
            return False

    def move_x(self, steps: int, force_move=False):
        self.x_tar += steps
        return self._perform_move_x(steps, force_move)

    def move_y(self, steps: int, force_move=False):
        self.y_tar += steps
        return self._perform_move_y(steps, force_move)

    def move_z(self, steps: int, force_move=False):
        self.z_tar += steps
        return self._perform_move_z(steps, force_move)

    def move(self, stepsX: int, stepsY: int, stepsZ: int, **kwargs):
        return (
            self.move_x(stepsX, **kwargs)
            and self.move_y(stepsY, **kwargs)
            and self.move_z(stepsZ, **kwargs)
        )

    def move_to(self, x: int, y: int, z: int, **kwargs):
        self.target = (x, y, z)
        return self.move_to_target(**kwargs)

    def move_to_target(self, **kwargs):
        return (
            self.move_x(self.x_tar - self._x, **kwargs)
            and self.move_y(self.y_tar - self._y, **kwargs)
            and self.move_z(self.z_tar - self._z, **kwargs)
        )

    def _constant_move_to_target(self, **kwargs):
        while 1:
            self.move_to_target(**kwargs)

    def constant_move_to_target(self):
        self._thread = threading.Thread(target=self._constant_move_to_target)
        self._thread.start()

    def stop_constant_move(self):
        # kill the thread
        self._thread.join()

    def __del__(self):
        self.stop_constant_move()

    # def stop(self):
    #     self.anc300.stop_all()


if __name__ == "__main__":
    anc300 = AttocubeANC300()
    # anc300.move_x(10)  # X, +10 steps
    # anc300.move_y(-10)  # Y, -10 steps
    # anc300.move(10, 10, 10)  # X, Y, Z, +10 steps
    # anc300.move_to(0, 0, 0)  # X, Y, Z, move to (0, 0, 0)
    # # Note: above all methods are blocking
    # # anc300.stop()  # stop all
    # anc300.set_to_origin()  # set current position to (0, 0, 0)
    # anc300.goto_origin()  # move to (0, 0, 0)
    # print(anc300.position)  # get current position
    # anc300.position = (10, 10, 10)  # set current position to (10, 10, 10)
    # print(anc300.freq_x)  # get current frequency on X axis
    # anc300.freq_x = 90  # set frequency on X axis to 1000 Hz
    ###
    # repeatability test
    # for i in range(10):
    #     anc300.freq_y = 500
    #     anc300.move_y(500)
    #     anc300.freq_y = 2000
    #     anc300.move_y(-500)
    ###
    # constant move
    anc300.constant_move_to_target()
    for i in range(1):
        anc300.x_tar += 10
        anc300.y_tar -= 10
        time.sleep(0.1)
