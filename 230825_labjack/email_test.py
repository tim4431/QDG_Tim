from time_util import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import List

EMAIL_SELF = "quantumdevicesgroup@outlook.com"
EMAIL_SLACK = "qdglab-monitor-aaaakuknki5idmca7uehje3bpq@quantumdevicesgroup.slack.com"
EMAIL_GROUP = " quantumdevices@lists.berkeley.edu"
emergency_email_list = [EMAIL_SELF, EMAIL_SLACK, EMAIL_GROUP]
notice_email_list = [EMAIL_SELF, EMAIL_SLACK]
# emergency_email_list = [EMAIL_SELF]
# notice_email_list = [EMAIL_SELF]


def temp_warning(temperature: float, img_fileName=None):
    # Email configuration
    _, curTimeStr, _ = get_time_date()
    subject = "[TEST] QDG-Lab temperature Warning: {:.1f} C".format(temperature)
    message = (
        "{:s} - Cooling water temperature Warning: {:.1f} C\n".format(
            curTimeStr, temperature
        )
        + "This is an email for testing"
    )
    send_email(
        emergency_email_list, subject=subject, msgstr=message, img_fileName=img_fileName
    )


def schedule_report(dateStr: str, img_fileName=None):
    subject = "[TEST] QDG-Lab temperature schedule report: {:s}".format(dateStr)
    message = (
        "{:s} - Cooling water temperature schedule report:\n".format(dateStr)
        + "This is an email for testing"
    )
    send_email(
        notice_email_list, subject=subject, msgstr=message, img_fileName=img_fileName
    )


def send_email(receiver_list: List, subject: str, msgstr: str, img_fileName=None):
    # Email configuration
    sender_email = "quantumdevicesgroup@outlook.com"

    # Connect to the SMTP server
    smtp_server = "smtp.office365.com"  # Change this to your SMTP server
    smtp_port = 587  # Change this to the appropriate port
    smtp_username = "quantumdevicesgroup@outlook.com"
    smtp_password = "qdg373!!"

    # Create the email
    for receiver_email in receiver_list:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(msgstr, "plain"))
        # add picture as attachment
        if img_fileName is not None:
            with open(img_fileName, "rb") as fp:
                img = MIMEImage(fp.read())
            msg.attach(img)

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


if __name__ == "__main__":
    temp_warning(25.0)
    schedule_report("2023-09-1")
