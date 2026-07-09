from django.urls import path
from . import views
from .views import UserFeedBackView, CustomLoginView, CustomLogoutView

app_name = "user"

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('user_feedback/', UserFeedBackView.as_view(), name='user_feedback'),
]