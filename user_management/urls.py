from django.urls import path
from . import views
from .views import UserFeedBackView, CustomLogoutView, user_login, user_register

app_name = "user"

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('user_feedback/', UserFeedBackView.as_view(), name='user_feedback'),
]