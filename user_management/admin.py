from django.contrib import admin

from user_management.models import DeliveryData,LastViewedData

# Register your models here.

admin.site.register(DeliveryData)
admin.site.register(LastViewedData)