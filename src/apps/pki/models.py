from django.db import models


class RevokedCertificate(models.Model):
    ''' Сертификаты отозванные НУЦ РК '''
    serial_number = models.CharField(max_length=64)
    revocation_date = models.DateTimeField()
