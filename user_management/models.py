from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class DeliveryData(models.Model):
    post_service = models.CharField(max_length=200)
    post_service_branch = models.CharField(max_length=200)
    city = models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)

class LastViewedData(models.Model):
    book = models.ForeignKey('shop.book', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class CustomUser(AbstractUser):
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
