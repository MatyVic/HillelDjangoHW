from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_management.models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth_date', 'phone_number')

class LoginForm(forms.Form):
    login = forms.CharField(max_length=250, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
