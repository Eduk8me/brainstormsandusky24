# This is my sendemail function for Python so I don't have to keep re-creating it in all of the python scripts

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendemail(sender,receiver,subject,msg):
    smtp_server = "mailserver.school.org"
    smtp_port = 25

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(receiver)
    message["Subject"] = subject

    message.attach(MIMEText(msg,"plain"))
    # Connect to the server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    # No need for server.starttls() and server.login()
    server.sendmail(sender, receiver, message.as_string())
    server.quit()

def sendhtmlemail(sender,receiver,subject,msgfile):
    smtp_server = "mailserver.school.org"
    smtp_port = 25

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = ", ".join(receiver)
    message["Subject"] = subject

    with open(msgfile, "r") as file:
        msg = file.read()

    html_part = MIMEText(msg, "html")
    message.attach(html_part)
    # Connect to the server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    # No need for server.starttls() and server.login()
    server.sendmail(sender, receiver, message.as_string())
    server.quit()
