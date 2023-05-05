from django.conf import settings
from django.core.mail import send_mail

def send_account_activation_email(email, username, email_token):
    subject = 'Your account needs to be verified'
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, click on this link to activate account http://localhost:8000/accounts/activate/{username}/{email_token}'
    send_mail(subject, message, email_from, [email])