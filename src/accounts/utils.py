from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user_email, username):
    subject = 'Welcome to Our Website!'
    html_message = render_to_string('welcome_email.html', {'username': username})
    plain_message = strip_tags(html_message)  # نسخة نصية للبريد الإلكتروني
    from_email = 'm.i.aljazzar19@gmail.com'  # البريد الإلكتروني المرسل
    to_email = user_email  # البريد الإلكتروني الخاص بالمستخدم

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)