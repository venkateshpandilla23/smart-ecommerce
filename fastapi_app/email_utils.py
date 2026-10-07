import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USERNAME = "productstore2026@gmail.com"
SMTP_PASSWORD = "fqzukpgedvfiennh"

async def send_test_email():
    message = EmailMessage()
    message["From"] = SMTP_USERNAME
    message["To"] = SMTP_USERNAME
    message["Subject"] = "FastAPI Email Test"
    message.set_content("Email notifications are working successfully!")

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        use_tls=True,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD
    )

async def send_email(to_email, subject, body):
    message = EmailMessage()
    message["From"] = SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        use_tls=True,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD
    )