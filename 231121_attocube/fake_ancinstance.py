import time


class fakeAxis:
    def __init__(self, name=""):
        self.name = name
        self._frequency = 100
        self._voltage = 30

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value: int):
        print("set {:s} frequency to {:d}".format(self.name, value))
        self._frequency = value

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value: float):
        print("set {:s} voltage to {:.1f}".format(self.name, value))
        self._voltage = value

    def move(self, steps, **kwargs):
        time.sleep(0.001)
        print("move {:s} by {:d} steps".format(self.name, steps))


class fakeANCController:
    def __init__(self):
        self.axis_x = fakeAxis("X")
        self.axis_y = fakeAxis("Y")
        self.axis_z = fakeAxis("Z")
        self.version = "fake ANC300"
