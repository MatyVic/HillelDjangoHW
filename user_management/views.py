from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from user_management.forms import RegisterForm, LoginForm


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

def user_login(request):
    if request.method == "POST":
        login_data = LoginForm(request.POST)
        if login_data.is_valid():
            login = login_data.cleaned_data["login"]
            password = login_data.cleaned_data["password"]
            user = authenticate(request, username=login, password=password)
            if user is not None:
                login(request, user)
                return redirect('shop:all_books')
            else:
                error = "Invalid login details"
                return render(request, "login.html", context={"register_form": LoginForm(), 'error': error})
        else:
            error = "Invalid form data"
            return render(request, "login.html", context={"register_form": LoginForm(), 'error': error})

    else:
        return render(request, "login.html", context={"register_form": LoginForm()})