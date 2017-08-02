from django.contrib import admin
from . import models


@admin.register(models.RevokedCertificate)
class RevokedCertificateAdmin(admin.ModelAdmin):
    list_display = ('revocation_date', 'serial_number')
