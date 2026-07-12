from django.urls import path
from . import views
from .views import UserFeedBackView, CustomLogoutView

app_name = "user"

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('user_feedback/', UserFeedBackView.as_view(), name='user_feedback'),
    path('user_register/', views.user_register, name='user_register'),
]