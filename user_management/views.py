from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


# Create your views here.
class UserFeedBackView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "user_feedback.html")
