from labjack import ljm
import logging
import os
from time_util import *


def setup_logging(log_fileName):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s"
    )
    cwd = os.getcwd()
    file_handler = logging.FileHandler(os.path.join(cwd, log_fileName + ".log"))
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
    file_handler.setFormatter(file_formatter)
    #
    logger = logging.getLogger()
    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    # Add the file handler to the root logger
    logger.addHandler(file_handler)


def setup_csv(fileDateStr):
    # if the file exists, do nothing
    if os.path.exists(fileDateStr + ".csv"):
        return
    write_csv(fileDateStr, "Timestamp, Temperature (K), Temperature (C)\n")


def write_csv(fileDateStr, writeline):
    f = open_csv(fileDateStr)
    f.write(writeline)
    f.close()


def open_csv(fileDateStr):
    # Get the current working directory
    cwd = os.getcwd()

    # Build a file-name and the file path.
    fileName = "%s.csv" % (fileDateStr)
    filePath = os.path.join(cwd, fileName)

    # Open the file and write a header line
    f = open(filePath, "a")

    return f


def email_warning(temperature: float):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Email configuration
    sender_email = "quantumdevicesgroup@gmail.com"
    receiver_email = "zsa2056197@hotmail.com"
    subject = "QDG-Lab Temperature Warning: {:.1f} C".format(temperature)
    _, curTimeStr, _ = get_time_date()
    message = "{:s} - Temperature Warning: {:.1f} C".format(curTimeStr, temperature)

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    # Connect to the SMTP server
    smtp_server = "smtp.gmail.com"  # Change this to your SMTP server
    smtp_port = 587  # Change this to the appropriate port
    smtp_username = "quantumdevicesgroup@gmail.com"
    smtp_password = "qdg373!!"

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        server.quit()  # type: ignore


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
        if lastWarning is None or (curtime - lastWarning).total_seconds() > 300:
            logging.info("Temperature Warning: %0.1f C" % (tempertureC))
            email_warning(tempertureC)
            lastWarning = curtime

    # Write the results to file
    write_csv(
        fileDateStr, "%s, %0.1f, %0.1f\n" % (curTimeStr, tempertureK, tempertureC)
    )
    logging.info("Temperature: %0.1f C" % (tempertureC))


_, endTimeStr, _ = get_time_date()
logging.info("Exit time: %s" % (endTimeStr))


ljm.cleanInterval(intervalHandle)
ljm.close(handle)
