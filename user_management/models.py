from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DeliveryData(models.Model):
    post_service = models.CharField(max_length=200, verbose_name=_("Post Service"))
    post_service_branch = models.CharField(max_length=200, verbose_name=_("Post Service Branch"))
    city = models.CharField(max_length=150, verbose_name=_("City"))
    street = models.CharField(max_length=150, verbose_name=_("Street"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE, verbose_name=_("Owner"))

class LastViewedData(models.Model):
    book = models.ForeignKey('shop.book', on_delete=models.CASCADE, verbose_name=_("Book"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Owner"))

class CustomUser(AbstractUser):
    birth_date = models.DateField(blank=True, null=True, verbose_name=_("Birth Date"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Phone Number"))
