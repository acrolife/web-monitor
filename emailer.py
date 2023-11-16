import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
MAILJET_API_KEY = st.secrets["MAILJET_API_KEY"]
MAILJET_SECRET_KEY = st.secrets["MAILJET_SECRET_KEY"]

def send_email(sender_email, receiver_email, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email # Your registered Mailjet email
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('in-v3.mailjet.com', 587)
    server.starttls()
    server.login(MAILJET_API_KEY, MAILJET_SECRET_KEY)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

# Usage example
# send_email("recipient@example.com", "New Slot Available", "A new slot has become available: [Slot Details]")
