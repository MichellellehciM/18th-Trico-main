from django.urls import path
from .views import (
    register,
    login,
    logout,
    profile,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    user_dashboard,
    apply_freelancer,
    switch_role,
    feedback_view,
    mark_as_read_and_redirect,
    freelancer_financial,
    likes_view,
    purchased_services,
)

app_name = "users"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset_done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("", user_dashboard, name="user_dashboard"),
    path("apply", apply_freelancer, name="apply_freelancer"),
    path("switch_role", switch_role, name="switch_role"),
    path("feedback/", feedback_view, name="feedback"),
    path(
        "notification/mark-as-read-and-redirect/<int:notification_id>/",
        mark_as_read_and_redirect,
        name="mark_as_read_and_redirect",
    ),
    path("freelancer_financial/", freelancer_financial, name="freelancer_financial"),
    path("likes/", likes_view, name="likes"),
    path("purchased_services/", purchased_services, name="purchased_services"),
]
