from labjack import ljm  # type: ignore
import sys

sys.path.append(r"\\QDG-LABBEAR\\Users\\QDG-LABBEAR-SERVER\\Desktop\\LANAS\\DataBear")
from RemoteDevice import RemoteDevice  # type: ignore
from typing import List, Tuple, Union, Any


def init_laser():
    laser = RemoteDevice("SantecTSL570")
    laser.write_laser_status("On")
    laser.write_wavelength(1326.0)
    return laser


def init_picoharp():
    return RemoteDevice("PicoHarp300")


def init_labjack():
    handle = ljm.openS("T7", "ETHERNET", "192.168.0.125")
    info = ljm.getHandleInfo(handle)
    print(info)
    return handle


def ljm_conf_range_resolution(
    handle: Any, numAIN: int, rangeAIN: float, resolutionAIN: int
):
    numFrames = 2
    aNames = ["AIN{:d}_RANGE".format(numAIN), "AIN{:d}_RESOLUTION_INDEX".format(numAIN)]
    aValues = [rangeAIN, resolutionAIN]
    ljm.eWriteNames(handle, numFrames, aNames, aValues)


def ljm_read_range_resolution(handle: Any, numAIN: int):
    numFrames = 2
    aNames = ["AIN{:d}_RANGE".format(numAIN), "AIN{:d}_RESOLUTION_INDEX".format(numAIN)]
    aValues = ljm.eReadNames(handle, numFrames, aNames)
    return aValues


def ljm_auto_range_resolution(handle, numAIN, estimated_v):
    if estimated_v < 0.5:
        ljm_conf_range_resolution(handle, numAIN, 1.00, 4)
    elif estimated_v < 3:
        ljm_conf_range_resolution(handle, numAIN, 10.00, 7)
    elif estimated_v < 20:
        ljm_conf_range_resolution(handle, numAIN, 10.00, 4)
