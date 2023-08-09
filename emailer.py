from flask import session
import smtplib, ssl, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

PORT = 465
CONTEXT = ssl.create_default_context()
HELPERBOT_EMAIL = "helperbot3000.noreply@gmail.com"
APP_PASSWORD = os.getenv("APP_PASSWORD")

def get_server():
    return smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=CONTEXT)

def send_email(reciever, subject, message_text):
    """ Sends an email from HelperBot through SSL """

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = HELPERBOT_EMAIL
    message["To"] = reciever

    message.attach(MIMEText(message_text, "html"))

    with get_server() as server:
        server.login(HELPERBOT_EMAIL, APP_PASSWORD)
        server.sendmail(
            HELPERBOT_EMAIL, reciever, message.as_string()
        )