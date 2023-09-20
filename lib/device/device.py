from labjack import ljm  # type: ignore
import sys
from typing import List, Tuple, Union, Any


sys.path.append(r"\\QDG-LABBEAR\\Users\\QDG-LABBEAR-SERVER\\Desktop\\LANAS\\DataBear")


def init_laser():
    from RemoteDevice import RemoteDevice  # type: ignore

    laser = RemoteDevice("SantecTSL570")
    laser.write_laser_status("On")
    laser.write_wavelength(1326.0)
    laser.write_power(-15.0)
    laser.write_coherence_control("Off")
    return laser


def init_picoharp():
    from RemoteDevice import RemoteDevice  # type: ignore

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


def ljm_auto_range_resolution(handle, numAIN):
    ljm_conf_range_resolution(handle, numAIN, 10.00, 1)
    estimated_v = ljm.eReadName(handle, "AIN{:d}".format(numAIN))
    if abs(estimated_v) < 0.8:
        ljm_conf_range_resolution(handle, numAIN, 1.00, 8)
    elif abs(estimated_v) < 20:
        ljm_conf_range_resolution(handle, numAIN, 10.00, 8)


def ljm_auto_range_read(handle, numAIN):
    ljm_auto_range_resolution(handle, numAIN)
    return ljm.eReadName(handle, "AIN{:d}".format(numAIN))
