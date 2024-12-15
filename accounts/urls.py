from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import UserRegistration, LogoutAPIView

urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutAPIView.as_view()),
    #from rest_framework.authtoken.views import obtain_auth_token
    path('register/', UserRegistration.as_view()),
]
