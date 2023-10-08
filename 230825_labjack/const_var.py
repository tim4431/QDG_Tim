pinName = "AIN2"
RECORD_INTERVAL_S = 20  # in s
ALERT_INTERVAL_S = 60 * 30  # in s
TEMPERATURE_THRESHOLD = 16  # in C
record_interval = RECORD_INTERVAL_S * 1000  # in ms
DEBUG = False # if True, only send email to myself
import datetime
schedule_report_time_list = [datetime.time(0, 0)]