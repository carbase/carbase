from django.contrib import admin
from . import models


@admin.register(models.Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('city', 'address')


@admin.register(models.Inspector)
class InspectorAdmin(admin.ModelAdmin):
    list_display = ('user', 'center')


@admin.register(models.Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('center', 'reregestration')
