from flask_mail import Message
from flask import current_app
from extensions import mail


# Send account verification email
def send_verification_email(email, token):
    verification_url = (
        f"{current_app.config['FRONTEND_URL']}/verify-email?token={token}"
    )

    message = Message(
        subject="Verify Your FindIt+ Account",
        recipients=[email],
        body=f"""
Hello!

Thank you for registering on FindIt+.

Click the link below to verify your college email:

{verification_url}

This link expires in 15 minutes.

If you did not create this account, ignore this email.
"""
    )

    mail.send(message)
