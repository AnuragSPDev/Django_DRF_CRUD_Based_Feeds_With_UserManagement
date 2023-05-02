from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.RegisterUser.as_view(), name='sign_up'),
    path('validate_otp/', views.ValidateOTPAndGenerateToken.as_view(), name='validate_otp'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('forgot_password/', views.ForgotUserPassword.as_view(), name='forgot_password'),
    path('index/', views.IndexPage.as_view(), name='index'),
]
