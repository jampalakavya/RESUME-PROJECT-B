



# # utils.py
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from django.conf import settings
# from django.core.mail import EmailMessage


# def send_email(subject, message, to_email):
#     """Send HTML email using SendGrid, fallback to SMTP if needed."""
    
#     if not to_email:
#         raise ValueError("to_email is required")

#     if isinstance(to_email, str):
#         to_emails = [to_email]
#     else:
#         to_emails = list(to_email)

#     print("=== EMAIL DEBUG START ===")
#     print("TO:", to_emails)
#     print("FROM:", getattr(settings, "FROM_EMAIL", None))
#     print("SENDGRID KEY EXISTS:", bool(getattr(settings, "SENDGRID_API_KEY", None)))

#     # -------------------------
#     # 1) Try SendGrid first
#     # -------------------------
#     try:
#         if not getattr(settings, "SENDGRID_API_KEY", None):
#             raise ValueError("SENDGRID_API_KEY is not configured")

#         sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

#         email = Mail(
#             from_email=getattr(settings, "FROM_EMAIL", settings.DEFAULT_FROM_EMAIL),
#             to_emails=to_emails,
#             subject=subject,
#             html_content=message
#         )

#         response = sg.send(email)

#         print("SENDGRID STATUS CODE:", response.status_code)
#         print("SENDGRID RESPONSE BODY:", response.body)
#         print("SENDGRID RESPONSE HEADERS:", response.headers)

#         if response.status_code in [200, 202]:
#             print(" EMAIL SENT VIA SENDGRID")
#             print("=== EMAIL DEBUG END ===")
#             return True
#         else:
#             print(" SendGrid failed with non-success status")
#             print("=== EMAIL DEBUG END ===")
#             return False

#     except Exception as e:
#         print("SendGrid error:", repr(e))

#     # -------------------------
#     # 2) SMTP fallback
#     # -------------------------
#     try:
#         fallback = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.FROM_EMAIL),
#             to=to_emails,
#         )
#         fallback.content_subtype = "html"
#         fallback.send(fail_silently=False)

#         print("✅ EMAIL SENT VIA SMTP FALLBACK")
#         print("=== EMAIL DEBUG END ===")
#         return True

#     except Exception as e:
#         print("❌ SMTP fallback email error:", repr(e))
#         print("=== EMAIL DEBUG END ===")
#         return False




from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def send_email(subject, message, to_email):
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY.strip()

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={
                "name": "Resume manager",
                "email": settings.DEFAULT_FROM_EMAIL
            },
            subject=subject,
            html_content=message
        )

        response = api_instance.send_transac_email(send_smtp_email)
        print("BREVO EMAIL SENT:", response)
        return True

    except ApiException as e:
        print("BREVO API ERROR:", e)
        return False

    except Exception as e:
        print("GENERAL EMAIL ERROR:", str(e))
        return False
    
    
    
# utils.py
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
import os

def generate_pdf(resume):
    path = os.path.join(settings.MEDIA_ROOT, f"generated_resumes/resume_{resume.id}.pdf")

    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(resume.full_name, styles['Title']))
    elements.append(Paragraph(resume.email, styles['Normal']))

    elements.append(Paragraph("Summary", styles['Heading2']))
    elements.append(Paragraph(resume.summary, styles['Normal']))

    for exp in resume.experiences.all():
        elements.append(Paragraph(f"{exp.job_title} - {exp.company}", styles['Normal']))

    doc.build(elements)

    return f"generated_resumes/resume_{resume.id}.pdf"