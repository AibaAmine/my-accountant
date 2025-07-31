from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import SendEmailOTPSerializer, VerifyEmailOTPSerializer,PasswordResetRequestSerializer,VerifyPasswordResetSerializer

User = get_user_model()

class SendEmailOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "OTP sent to your email"},
                status=status.HTTP_200_OK
            )
        print("DEBUG here ")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailOTPView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"detail": "Email verified successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordRestRequestAPIView(APIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes=[AllowAny]

    def post(self,request,*args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response({"message": "OTP sent to email."},status=status.HTTP_200_OK)


class VerifyPasswordResetAPIView(APIView):
    serializer_class = VerifyPasswordResetSerializer
    permission_classes=[AllowAny]

    
    
    def post(self,request,*args,**kwargs):
        serializer = VerifyPasswordResetSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Password reset successfully."},status=status.HTTP_200_OK)

