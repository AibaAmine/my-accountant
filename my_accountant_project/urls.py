from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from allauth.account import views as allauth_views
from django.shortcuts import redirect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


# Custom bridge function to handle parameter name mismatch
def password_reset_confirm_bridge(request, uidb64, token):
    """
    Bridge function that converts dj-rest-auth parameters (uidb64, token)
    to allauth parameters (uidb36, key)
    """
    return allauth_views.password_reset_from_key(request, uidb36=uidb64, key=token)


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
    path("auth/", include("dj_rest_auth.urls")),  # Login, logout, user details, etc.
    path(
        "auth/registration/", include("dj_rest_auth.registration.urls")
    ),  # Registration
    # Social Authentication APIs (JSON responses)
    path("auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("", include("allauth.urls")),
    # Bridge URL that converts dj-rest-auth parameters to allauth parameters
    re_path(
        r"^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        password_reset_confirm_bridge,
        name="password_reset_confirm",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # api documentation urls:
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
]
