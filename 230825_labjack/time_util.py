import datetime


TIME_STAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # year-month-day hour:minute:second.microsecond
DATE_FORMAT = "%Y-%m-%d"


def get_time_date():
    curtime = datetime.datetime.now()
    curTimeStr = curtime.strftime(TIME_STAMP_FORMAT)
    curDateStr = curtime.strftime(DATE_FORMAT)
    return curtime, curTimeStr, curDateStr
