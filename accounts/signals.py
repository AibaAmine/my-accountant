from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import EmailVerificationOTP, User
from django.conf import settings


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(
        f"[DEBUG] User signal triggered for {instance.email}, created: {created}, user_type: {instance.user_type}"
    )

    if created:
        try:
            from profiles.models import (
                AccountantProfile,
                ClientProfile,
                AcademicProfile,
            )

            if instance.user_type == "accountant":
                profile = AccountantProfile.objects.create(
                    user=instance,
                    phone=instance.phone  
                )
                print(
                    f"[DEBUG] Created AccountantProfile for {instance.email} - ID: {profile.profile_id}"
                )

            elif instance.user_type == "client":
                profile = ClientProfile.objects.create(
                    user=instance,
                    phone=instance.phone  
                )
                print(
                    f"[DEBUG] Created ClientProfile for {instance.email} - ID: {profile.profile_id}"
                )

            elif instance.user_type == "academic":
                profile = AcademicProfile.objects.create(
                    user=instance,
                    phone=instance.phone  
                )
                print(
                    f"[DEBUG] Created AcademicProfile for {instance.email} - ID: {profile.profile_id}"
                )

            else:
                print(f"[DEBUG] No profile created for user_type: {instance.user_type}")

        except Exception as e:
            print(f"[ERROR] Failed to create profile for {instance.email}: {str(e)}")
            import traceback

            traceback.print_exc()


@receiver(post_save, sender=EmailVerificationOTP)
def send_otp_email(sender, instance, created, **kwargs):
    print("[DEBUG] EmailVerificationOTP signal triggered")
    """
    Sends an OTP email every time a new EmailVerificationOTP is created.
    """
    if created:
        subject = "Please VERIFY your email"
        message = f"your OTP code is {instance.code}. It expires in 10 minutes."
        from_email=settings.DEFAULT_FROM_EMAIL,  
        recipient_list = [instance.user.email]
        send_mail(subject, message, from_email, recipient_list)
        print(f"Sent otp email to {instance.user.email} - Code: {instance.code}")
