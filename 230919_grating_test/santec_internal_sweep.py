from datetime import datetime
import sys
import numpy as np
from matplotlib import pyplot as plt
from labjack import ljm
import ljm_stream_util
import time


def santec_internal_sweep(
    Laser, power, scanRate=100000, start=1245, end=1375, sweeprate=10
):
    # seems to be following the code here: https://github.com/labjack/labjack-ljm-python/blob/master/Examples/More/Stream/stream_triggered.py
    handle = ljm.openS("T7", "ETHERNET", "192.168.0.125")
    aScanList = ljm.namesToAddresses(1, ["AIN2"])[0]
    TRIGGER_NAME = "DIO0"
    scansPerRead = int(scanRate * abs(start - end) / sweeprate)

    def configureDeviceForTriggeredStream(handle, triggerName):
        address = ljm.nameToAddress(triggerName)[0]
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", address)
        ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 0)
        ljm.eWriteName(handle, "%s_EF_INDEX" % triggerName, 5)
        ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 1)

    def configureLJMForTriggeredStream():
        ljm.writeLibraryConfigS(
            ljm.constants.STREAM_SCANS_RETURN,
            ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE,
        )
        ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 0)

    Laser.write_laser_status("On")
    Laser.write_coherence_control("Off")  # turn off coherence control
    Laser.write_start_wav(start)
    Laser.write_stop_wav(end)
    Laser.write_sweep_mode("Continuous sweep mode and One way")
    Laser.write_sweep_speed(sweeprate)
    Laser.write_power(power)
    Laser.write_sweep_state("On")
    MAX_REQUESTS = 1
    i = 1
    ljmScanBacklog = 0
    aData = np.zeros(10)
    try:
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)
        aNames = [
            "AIN_ALL_NEGATIVE_CH",
            "AIN0_RANGE",
            "STREAM_SETTLING_US",
            "STREAM_RESOLUTION_INDEX",
        ]
        aValues = [ljm.constants.GND, 10.0, 0, 0]
        numFrames = len(aNames)
        ljm.eWriteNames(handle, numFrames, aNames, aValues)
        configureDeviceForTriggeredStream(handle, TRIGGER_NAME)
        configureLJMForTriggeredStream()
        scanRate = ljm.eStreamStart(handle, scansPerRead, 1, aScanList, scanRate)
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)
        while i <= MAX_REQUESTS:
            ljm_stream_util.variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)
            try:
                ret = ljm.eStreamRead(handle)
                aData = ret[0]
                ljmScanBacklog = ret[2]
                i += 1
            except ljm.LJMError as err:
                if err.errorCode == ljm.errorcodes.NO_SCANS_RETURNED:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    continue
                else:
                    raise err
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)

    ljm.close(handle)

    Laser.write_sweep_state("Off")
    Laser.write_laser_status("Off")
    return np.linspace(start, end, len(aData)), np.array(aData)


if __name__ == "__main__":
    import sys

    sys.path.append("../")
    from lib.device.device import init_laser

    laser = init_laser()
    l, v = santec_internal_sweep(
        laser, power=5, scanRate=100000, start=1245, end=1375, sweeprate=10
    )
    import matplotlib.pyplot as plt

    plt.plot(l, v)
