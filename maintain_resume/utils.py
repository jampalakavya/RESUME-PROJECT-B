
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