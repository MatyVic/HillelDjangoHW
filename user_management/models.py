from django.db import models


class DeliveryData(models.Model):
    post_service = models.CharField(max_length=200)
    post_service_branch = models.CharField(max_length=200)
    city = models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

class LastViewedData(models.Model):
    book = models.ForeignKey('shop.book', on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)