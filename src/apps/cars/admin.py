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


@admin.register(models.Reregistration)
class ReregistrationAdmin(admin.ModelAdmin):
    list_display = ('car', 'seller', 'buyer')


@admin.register(models.Deregistration)
class DeregistrationAdmin(admin.ModelAdmin):
    list_display = ('car', 'created', 'is_success', 'is_transit_number', 'is_paid')


@admin.register(models.Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('iin', 'email')
