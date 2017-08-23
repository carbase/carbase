from django.contrib import admin
from . import models


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('created', 'url')
