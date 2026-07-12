from django.urls import path
from . import views
from .views import UserFeedBackView, user_logout, user_login, user_register

app_name = "user"

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='logout'),
    path('user_feedback/', UserFeedBackView.as_view(), name='user_feedback'),
]