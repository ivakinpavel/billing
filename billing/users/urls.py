from django.urls import path
from rest_framework.authtoken import views

from billing.users.views import (
    UserCreateView
)

app_name = "users"
urlpatterns = [
    path("", UserCreateView.as_view(), name="register"),
    path("login/", views.obtain_auth_token, name="login"),
]
