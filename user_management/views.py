from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from user_management.forms import RegisterForm, LoginForm
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class UserFeedBackView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "user_feedback.html")

def user_register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            logger.info("New user registered: %s", user.username)
            return redirect('shop:all_books')
        else:
            logger.warning("Invalid registration attempt: %s", register_form.errors)
            return render(request, "register.html", context={"register_form": register_form})
    return render(request, "register.html", context={"register_form": RegisterForm()})

def user_login(request):
    if request.method == "POST":
        login_data = LoginForm(request.POST)
        if login_data.is_valid():
            username  = login_data.cleaned_data["login"]
            password = login_data.cleaned_data["password"]
            user = authenticate(request, username=username , password=password)
            if user is not None:
                login(request, user)
                return redirect('shop:all_books')
            else:
                error = "Invalid login details"
                return render(request, "login.html", context={"login_form": LoginForm(), 'error': error})
        else:
            error = "Invalid form data"
            return render(request, "login.html", context={"login_form": LoginForm(), 'error': error})

    else:
        return render(request, "login.html", context={"login_form": LoginForm()})

def user_logout(request):
    logout(request)
    return redirect('shop:all_books')