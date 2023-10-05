from labjack import ljm  # type: ignore
import logging
import os
from time_util import *
from email_test import temp_warning, schedule_report
import threading
from load_data import plot_data, load_data
import numpy as np

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

schedule_report_time_list = [datetime.time(0, 0), datetime.time(6,0), datetime.time(12, 0), datetime.time(18,0)]
flag_schedule_report_list = [False for i in range(len(schedule_report_time_list))]

while 1:
    numSkippedIntervals = ljm.waitForNextInterval(intervalHandle)
    # Get and format a timestamp
    curtime, curTimeStr, curDateStr = get_time_date()
    if curDateStr != fileDateStr:
        # clear flag_schedule_report_list
        flag_schedule_report_list = [False for i in range(len(schedule_report_time_list))]
        #
        fileDateStr = curDateStr
        setup_logging(fileDateStr)
        setup_csv(fileDateStr)
    #
    for k in range(len(schedule_report_time_list)):
        report_time = schedule_report_time_list[k]
        flag = flag_schedule_report_list[k]

        # extract the hour and minute from the report time
        report_time = datetime.datetime.combine(curtime.date(), report_time)

        #if the curtime is after the report time and the report has not been sent
        #and the time difference is within 2 minute
        if (
            curtime.time() > report_time.time()
            and (not flag)
            and (curtime - report_time).total_seconds() < 120
        ):
            flag_schedule_report_list[k] = True
            logging.info("Schedule report at %s" % (report_time))
            # schedule report
            img_fileName = plot_data(fileDateStr, span="1D")
            # create another thread to send email
            threading.Thread(
                target=schedule_report, args=(fileDateStr, img_fileName)
            ).start()

    # Calculate the time since the last interval
    # curTick = ljm.getHostTick()

    # Read AIN0
    result = ljm.eReadName(handle, pinName)
    tempertureK = 55.56 * result + 255.37
    tempertureC = tempertureK - 273.15

    logging.info("Temperature: %0.1f C" % (tempertureC))
    if tempertureC < 0 or tempertureC > 50:
        logging.warning("Temperature out of range: %0.1f C" % (tempertureC))
    else:
        # Write the results to file
        write_csv(
            fileDateStr, "%s, %0.1f, %0.1f\n" % (curTimeStr, tempertureK, tempertureC)
        )

    if tempertureC > TEMPERATURE_THRESHOLD:
        # if last warning is more than 5 minutes ago
        if (
            lastWarning is None
            or (curtime - lastWarning).total_seconds() > ALERT_INTERVAL_S
        ):
            timedata, tempdata = load_data(fileDateStr, span="1H")
            if len(tempdata) > 5 and np.mean(tempdata[-5:]) > TEMPERATURE_THRESHOLD:
                logging.info("Temperature Warning: %0.1f C" % (tempertureC))
                lastWarning = curtime
                img_fileName = plot_data(fileDateStr, span="1H")
                # create another thread to send email
                threading.Thread(
                    target=temp_warning, args=(tempertureC, img_fileName)
                ).start()


_, endTimeStr, _ = get_time_date()
logging.info("Exit time: %s" % (endTimeStr))


ljm.cleanInterval(intervalHandle)
ljm.close(handle)
