from django.urls import path

from user_management.views import UserFeedBackView

app_name = "user"

urlpatterns = [
    path('user_feedback/', UserFeedBackView.as_view(), name='user_feedback'),
]