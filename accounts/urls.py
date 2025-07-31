from django.urls import path
from .views import SendEmailOTPView,VerifyEmailOTPView,VerifyPasswordResetAPIView,PasswordRestRequestAPIView




urlpatterns = [
    #verify email endpoints
    path("send-email-otp/",SendEmailOTPView.as_view(),name="send-email-otp"),
    path("verify-email-otp/",VerifyEmailOTPView.as_view(),name="verify-email-otp"),
    #password reset enpoints
    path("password-reset/request/",PasswordRestRequestAPIView.as_view(),name="request-password-reset"),
    path("password-reset/verify/",VerifyPasswordResetAPIView.as_view(),name="verify-password-reset")
    
]