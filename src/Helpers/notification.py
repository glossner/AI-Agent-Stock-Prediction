import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os

def send_email_alert(subject, message, recipient_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

def send_sms_alert(message, recipient_phone):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=from_phone,
        to=recipient_phone
    )

def send_sms_alert_curl(message, recipient_phone):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    command = f"curl 'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json' -X POST --data-urlencode 'To={recipient_phone}' --data-urlencode 'From={from_phone}' --data-urlencode 'Body={message}' -u {account_sid}:{auth_token}"
    os.system(command)
