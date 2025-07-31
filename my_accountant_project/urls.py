from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.http import JsonResponse
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from drf_yasg.utils import swagger_auto_schema

LogoutView.get = swagger_auto_schema(auto_schema=None)(LogoutView.get)

def account_inactive_view(request):
    return JsonResponse(
        {"detail": "Account inactive. Please verify your email."}, status=403
    )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


schema_view = get_schema_view(
    openapi.Info(
        title="My Accountant API",
        default_version="v1",
        description="Complete API documentation for My Accountant platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myaccountant.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth endpoints (login, logout, user details)
    path("auth/login/", LoginView.as_view(), name="rest_login"),
    path("auth/logout/", LogoutView.as_view(), name="rest_logout"),
    path("auth/user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/", include("accounts.urls")),
    # Registration
    path("auth/registration/", RegisterView.as_view(), name="rest_register"),
    # google login
    path("auth/google/", GoogleLogin.as_view(), name="google_login"),
    path(
        "auth/facebook/", FacebookLogin.as_view(), name="facebook_login"
    ),  # Facebook login
    # JWT token endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API documentation URLs
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
    path("profiles/", include("profiles.urls")),
    path("accounts/inactive/", account_inactive_view, name="account_inactive"),
]
