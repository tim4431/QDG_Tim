from datetime import datetime
import sys
import numpy as np
from matplotlib import pyplot as plt
from labjack import ljm
from . import ljm_stream_util
import time
from typing import List, Tuple, Union, Any


def santec_internal_sweep(
    handle: Any,
    laser: Any,
    power: float = 5,
    aScanListNames: List[str] = ["AIN0", "AIN1"],
    aRangeList: List[float] = [10.0, 10.0],
    scanRate: float = 1000,
    start: float = 1245,
    end: float = 1375,
    sweeprate: float = 10,
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    - laser: RemoteDevice object
    - power: float, in dBm
    - scanRate: int, in Hz
    - start: start wavelength, in nm
    - end: end wavelength, in nm
    - sweeprate: sweep rate, in nm/s
    """
    # seems to be following the code here: https://github.com/labjack/labjack-ljm-python/blob/master/Examples/More/Stream/stream_triggered.py
    # handle = ljm.openS("T7", "ETHERNET", "192.168.0.125")
    # aScanListNames = ["AIN0", "AIN1"]
    numAddresses = len(aScanListNames)
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
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

    laser.write_laser_status("On")
    laser.write_coherence_control("Off")  # turn off coherence control
    laser.write_start_wav(start)
    laser.write_stop_wav(end)
    laser.write_sweep_mode("Continuous sweep mode and One way")
    laser.write_sweep_speed(sweeprate)
    laser.write_power(power)
    laser.write_sweep_state("On")
    #
    MAX_REQUESTS = 1
    i = 1
    ljmScanBacklog = 0
    aData = np.zeros(10)
    datas = []  # [data0, data1, ...]
    #
    try:
        # first set as internal clock triggered sweep
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)
        aNames = [
            "AIN_ALL_NEGATIVE_CH",
            "STREAM_SETTLING_US",
            "STREAM_RESOLUTION_INDEX",
        ]
        #
        aValues = [ljm.constants.GND, 0, 4]
        for i in range(numAddresses):
            aNames.append("{:s}_RANGE".format(aScanListNames[i]))
            aValues.append(aRangeList[i])
        #
        numFrames = len(aNames)
        ljm.eWriteNames(handle, numFrames, aNames, aValues)
        # Then set to external trigger stream mode
        configureDeviceForTriggeredStream(handle, TRIGGER_NAME)
        configureLJMForTriggeredStream()
        scanRate = ljm.eStreamStart(
            handle, scansPerRead, numAddresses, aScanList, scanRate
        )
        #
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)
        print(
            "\nEstimated aquisition time: %0.3f seconds."
            % (float(abs(start - end) / sweeprate))
        )
        print("Wavelength resolution: %0.3f nm." % (float(sweeprate / scanRate)))
        #
        while i <= MAX_REQUESTS:
            ljm_stream_util.variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)
            try:
                ret = ljm.eStreamRead(handle)
                aData = ret[0]
                print(len(aData))
                for j in range(numAddresses):
                    aDataj = [aData[numAddresses * i + j] for i in range(scansPerRead)]
                    datas.append(aDataj)
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
    finally:
        # ljm.close(handle)

        laser.write_sweep_state("Off")
        laser.write_laser_status("Off")
    return np.linspace(start, end, scansPerRead), list(
        np.array(datas[j]) for j in range(numAddresses)
    )


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    sys.path.append("..")
    from lib.device.device import init_laser

    laser = init_laser()
    l, vs = santec_internal_sweep(
        handle=None,
        laser=laser,
        power=5,
        aScanListNames=["AIN2", "AIN3"],
        scanRate=10000,
        start=1355,
        end=1356,
        sweeprate=10,
    )
    v1, v2 = vs

    plt.plot(l, v1, label="AIN2")
    plt.plot(l, v2, label="AIN3")
    plt.show()
