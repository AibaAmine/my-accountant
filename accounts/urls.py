from django.urls import path
from .views import SendEmailOTPView,VerifyEmailOTPView




urlpatterns = [
    path("send-email-otp/",SendEmailOTPView.as_view(),name="send-email-otp"),
    path("verify-email-otp/",VerifyEmailOTPView.as_view(),name="verify-email-otp")
    
]