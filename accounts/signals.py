from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import EmailVerificationOTP


@receiver(post_save, sender=EmailVerificationOTP)
def send_otp_email(sender, instance, created, **kwargs):
    print("[DEBUG] EmailVerificationOTP signal triggered")
    """
    Sends an OTP email every time a new EmailVerificationOTP is created.
    """
    if created:
        subject = "Please VERIFY your email"
        message = f"your OTP code is {instance.code}. It expires in 10 minutes."
        from_email = "myaccountant@gmail.com"
        recipient_list = [instance.user.email]
        send_mail(subject, message, from_email, recipient_list)
        print(f"Sent otp email to {instance.user.email} - Code: {instance.code}")


