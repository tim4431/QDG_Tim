from labjack import ljm
import logging
import os
from time_util import *
from email_test import email_warning
import threading


# >>> paramters <<<
pinName = "AIN0"
record_interval = 10000  # in ms

#
_, fileTimeStr, fileDateStr = get_time_date()
setup_logging(fileDateStr)
logging.info("Start time : %s" % (fileTimeStr))
setup_csv(fileDateStr)
#
handle = ljm.openS("T4", "ANY", "440013859")
info = ljm.getHandleInfo(handle)
logging.info(
    "\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i"
    % (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])
)


# >>> START <<<
intervalHandle = 0
ljm.startInterval(intervalHandle, record_interval * 1000)
numSkippedIntervals = 0

lastTick = ljm.getHostTick()
duration = 0

lastWarning = None

while 1:
    numSkippedIntervals = ljm.waitForNextInterval(intervalHandle)
    # Get and format a timestamp
    curtime, curTimeStr, curDateStr = get_time_date()
    if curDateStr != fileDateStr:
        fileDateStr = curDateStr
        setup_logging(fileDateStr)
        setup_csv(fileDateStr)

    # Calculate the time since the last interval
    # curTick = ljm.getHostTick()

    # Read AIN0
    result = ljm.eReadName(handle, pinName)
    tempertureK = 100.0 * result
    tempertureC = tempertureK - 273.15

    if tempertureC > 29:
        # if last warning is more than 5 minutes ago
        if lastWarning is None or (curtime - lastWarning).total_seconds() > 60:
            logging.info("Temperature Warning: %0.1f C" % (tempertureC))
            lastWarning = curtime
            # create another thread to send email
            threading.Thread(target=email_warning, args=(tempertureC,)).start()

    # Write the results to file
    write_csv(
        fileDateStr, "%s, %0.1f, %0.1f\n" % (curTimeStr, tempertureK, tempertureC)
    )
    logging.info("Temperature: %0.1f C" % (tempertureC))


_, endTimeStr, _ = get_time_date()
logging.info("Exit time: %s" % (endTimeStr))


ljm.cleanInterval(intervalHandle)
ljm.close(handle)
