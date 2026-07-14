from time import sleep

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def hello(name):
    print("Start task hello")
    sleep(20)
    print(f"Hello {name}")
    return f"Hello {name}"


@shared_task
def send_otp_mail(email, code):
    send_mail(
        subject="Your OTP code",
        message=f"Code: {code}",
        from_email="B-64-1",
        recipient_list=[email],
        fail_silently=False,
    )
    return "OK"


@shared_task
def send_report():
    send_mail(
        subject="[Report]",
        message="Что-то очень важное",
        from_email="B-64-1",
        recipient_list=[
            "riszav.01@gmail.com",
            "java2geektech@gmail.com",
            "fourdeltaone90@gmail.com",
        ],
        fail_silently=False,
    )
    return "OK"