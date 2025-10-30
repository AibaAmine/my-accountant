from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from .serializers import (
    AccountantProfileSerializer,
    ClientProfileSerializer,
    AcademicProfileSerializer,
)
from .models import AccountantProfile, ClientProfile, AcademicProfile, ProfileAttachment

from rest_framework.views import APIView

from accounts.models import User


class MyProfileAPIView(generics.RetrieveUpdateAPIView):
  
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        user = self.request.user
        if user.user_type == "accountant":
            return AccountantProfileSerializer
        elif user.user_type == "client":
            return ClientProfileSerializer
        elif user.user_type == "academic":
            return AcademicProfileSerializer
        else:
            raise NotFound("Invalid user type.")

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "accountant":
            return AccountantProfile.objects.all()
        elif user.user_type == "client":
            return ClientProfile.objects.all()
        elif user.user_type == "academic":
            return AcademicProfile.objects.all()
        else:
            return AccountantProfile.objects.none()

    def get_object(self):
        user = self.request.user
        try:
            if user.user_type == "accountant":
                return AccountantProfile.objects.get(user=user)
            elif user.user_type == "client":
                return ClientProfile.objects.get(user=user)
            elif user.user_type == "academic":
                return AcademicProfile.objects.get(user=user)
            else:
                raise NotFound("Profile not found for this user type.")
        except (AccountantProfile.DoesNotExist, ClientProfile.DoesNotExist, AcademicProfile.DoesNotExist):
            raise NotFound("Profile not found.")

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Custom update method to handle form-data with files"""
        instance = self.get_object()

        # Check if this is form-data request with files
        if (
            hasattr(request, "content_type")
            and "multipart/form-data" in request.content_type
        ):
            # Handle form-data
            data = {}
            for key, value in request.data.items():
                if key != "upload_files":
                    data[key] = value

            # Handle multiple file uploads
            upload_files = request.FILES.getlist("upload_files")
            if upload_files:
                # Delete existing attachments
                instance.profile_attachments.all().delete()

                # Create new attachments for the appropriate profile type
                for file in upload_files:
                    attachment_data = {
                        "file": file,
                        "original_filename": file.name,
                        "file_size": file.size,
                    }
                    
                    # Set the appropriate foreign key based on user type
                    if request.user.user_type == "accountant":
                        attachment_data["accountant_profile"] = instance
                    elif request.user.user_type == "client":
                        attachment_data["client_profile"] = instance
                    elif request.user.user_type == "academic":
                        attachment_data["academic_profile"] = instance
                    
                    ProfileAttachment.objects.create(**attachment_data)
        else:
            # Handle JSON data normally
            data = request.data

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class ProfileInfosApiView(APIView):

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=404)

        user_role = user.user_type

        if user_role == "accountant":
            try:
                profile = AccountantProfile.objects.get(user=user)
            except AccountantProfile.DoesNotExist:
                return Response({"error": "accountant profile not found"}, status=404)
            serializer = AccountantProfileSerializer(
                profile, context={"request": request}
            )
        elif user_role == "client":
            try:
                profile = ClientProfile.objects.get(user=user)
            except ClientProfile.DoesNotExist:
                return Response({"error": "client profile not found"}, status=404)
            serializer = ClientProfileSerializer(profile, context={"request": request})
        else:
            try:
                profile = AcademicProfile.objects.get(user=user)
            except AcademicProfile.DoesNotExist:
                return Response({"error": "academic profile not found"}, status=404)
            serializer = AcademicProfileSerializer(
                profile, context={"request": request}
            )

        return Response(serializer.data)
