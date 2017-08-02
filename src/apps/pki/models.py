from django.db import models


class RevokedCertificate(models.Model):
    serial_number = models.CharField(max_length=64)
    revocation_date = models.DateTimeField()
