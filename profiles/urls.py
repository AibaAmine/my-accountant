from django.urls import path
from .views import (
    AccountantProfileAPIView, AccountantProfileCreateAPIView,
    ClientProfileAPIView, ClientProfileCreateAPIView,
    AcademicProfileAPIView, AcademicProfileCreateAPIView
)

app_name = 'profiles'

urlpatterns = [
    # Accountant Profile URLs
    path("accountant/", AccountantProfileAPIView.as_view(), name='accountant-profile'),
    path("accountant/create/", AccountantProfileCreateAPIView.as_view(), name="accountant-profile-create"),
    
    # Client Profile URLs
    path("client/", ClientProfileAPIView.as_view(), name='client-profile'),
    path("client/create/", ClientProfileCreateAPIView.as_view(), name="client-profile-create"),
    
    # Academic Profile URLs
    path("academic/", AcademicProfileAPIView.as_view(), name='academic-profile'),
    path("academic/create/", AcademicProfileCreateAPIView.as_view(), name="academic-profile-create"),
]