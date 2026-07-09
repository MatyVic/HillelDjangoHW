from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_management.models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth_date', 'phone_number')