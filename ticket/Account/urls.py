from django.urls import path
from .viewsAccount import signup_user, edit_user, profiles_view, login_user, profile_view

urlpatterns = [
    path("signup/", signup_user, name="signup"),
    path("login/", login_user, name="login"),
    path("profiles/", profiles_view, name="profile_list"),
    path("profile/<int:pk>/", profile_view, name="profile"),
    path("update/", edit_user, name="edit_user"),
]
