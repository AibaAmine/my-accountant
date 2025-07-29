from django.urls import path
from .views import AccountantProfileAPIView,AccountantProfileCreateAPIView

app_name = 'profiles'

urlpatterns = [
    path("accountant/",AccountantProfileAPIView.as_view(),name ='accountant-profile'),
    path("accountant/create/",AccountantProfileCreateAPIView.as_view(),name="accountant-profile-create"),
    
]