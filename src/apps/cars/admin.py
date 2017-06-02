from django.contrib import admin
from . import models


class FineInline(admin.TabularInline):
    model = models.Fine
    extra = 0


class TaxInline(admin.TabularInline):
    model = models.Tax
    extra = 0


@admin.register(models.Car)
class CarAdmin(admin.ModelAdmin):
    inlines = (FineInline, TaxInline)
    list_display = ('__str__', 'user')


@admin.register(models.Reregestration)
class ReregestrationAdmin(admin.ModelAdmin):
    list_display = ('car', 'seller', 'buyer')
