from django.contrib import admin

from .models import NumberPlate


@admin.register(NumberPlate)
class NumberPlateAdmin(admin.ModelAdmin):
    list_display = ('digits', 'characters', 'region', 'is_sold', 'sale_date', 'owner_id',
                    'is_installed')
