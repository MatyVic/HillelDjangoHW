from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from user_management.models import CustomUser



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth_date', 'phone_number')
        labels = {
            'username': _("Username"),
            'birth_date': _("Birth date"),
            'phone_number': _("Phone number"),
        }

class LoginForm(forms.Form):
    login = forms.CharField(max_length=250, required=True, label=_("Login"))
    password = forms.CharField(widget=forms.PasswordInput, required=True, label=_("Password"))
