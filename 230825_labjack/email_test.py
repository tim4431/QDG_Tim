from time_util import *


def email_warning(temperature: float):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Email configuration
    sender_email = "quantumdevicesgroup@outlook.com"
    receiver_email_list = [
        "quantumdevicesgroup@outlook.com",
        "qdglab-monitor-aaaakuknki5idmca7uehje3bpq@quantumdevicesgroup.slack.com",
    ]
    subject = "QDG-Lab Temperature Warning: {:.1f} C".format(temperature)
    _, curTimeStr, _ = get_time_date()
    message = (
        "{:s} - Cooling water temperature Warning: {:.1f} C".format(
            curTimeStr, temperature
        )
        + "\n This is an email for testing"
    )
    # Connect to the SMTP server
    smtp_server = "smtp.office365.com"  # Change this to your SMTP server
    smtp_port = 587  # Change this to the appropriate port
    smtp_username = "quantumdevicesgroup@outlook.com"
    smtp_password = "qdg373!!"

    # Create the email
    for receiver_email in receiver_email_list:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

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
    email_warning(100)
