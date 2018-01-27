from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings



def send_email_verfication_mail(username, email, key, domain):
    #creating verification email link
    link = "http://{}/user/email-verification/{}/".format(
        domain, key
    )
    #gettings the html template
    html_template = get_template("email/verification_mail.html")
    content_passed = {
        'name': username,
        'link': link,
    }
    #passing the values to the email template
    html_content = html_template.render(content_passed)
    send_email = EmailMessage(
        subject='Aspirants: Email Verification',
        body=html_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email, ] #this must be a list
    )
    send_email.content_subtype = 'html'
    send_email.send()