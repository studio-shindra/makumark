from django.contrib import admin
from django.urls import path, include
from quotes.views import MeView, SubscriptionVerifyView, AppleSignInView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/signin/", AppleSignInView.as_view(), name="apple-signin"),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/subscription/verify/", SubscriptionVerifyView.as_view(), name="subscription-verify"),
    path("api/quotes/", include("quotes.urls")),
    path("api/tracking/", include("tracking.urls")),
]