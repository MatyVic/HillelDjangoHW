from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from user_management.forms import RegisterForm


class CustomLoginView(LoginView):
    template_name = "login.html"


class CustomLogoutView(LogoutView):
    next_page = "shop:all_books"


# Create your views here.
class UserFeedBackView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "user_feedback.html")

def user_register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponse("success")
        else:
            return render(request, "register.html")
    return render(request, "register.html", context={"register_form": RegisterForm()})