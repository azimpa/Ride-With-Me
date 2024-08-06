from django.urls import path
from accounts import views

urlpatterns = [
    path("user_login", views.user_login, name="user_login"),
    path("user_signup", views.user_signup, name="user_signup"),
    path("otpcheck/<str:phone_number>,<int:id>", views.otpcheck, name="otpcheck"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("userprofile", views.userprofile, name="userprofile"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("forgot_otpcheck/<str:phone_number>,<int:id>", views.forgot_otpcheck, name="forgot_otpcheck"),
]
