from django.contrib import admin

from .import models

# Register your models here.
admin.site.register(models.BankAccount)
admin.site.register(models.Transaction)