from django.urls import path

from account import views


app_name = 'account'

urlpatterns = [
    path('signup/', views.OTPRequestView.as_view(), name='signup'),
    path('verify/', views.VerifyUserView.as_view(), name='verify_user'),
    path('user/', views.UserRetrieveUpdateView.as_view(), name="user_info"),
]
