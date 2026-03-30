import threading
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_email(subject, message, to_email):
    def _send():
        try:
            print("EMAIL THREAD STARTED")  # debug

            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

            email = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=message
            )

            sg.send(email)
            print("EMAIL SENT SUCCESSFULLY")  # debug

        except Exception as e:
            print("Email error:", str(e))

    thread = threading.Thread(target=_send)
    thread.start()