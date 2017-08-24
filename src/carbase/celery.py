from __future__ import absolute_import, unicode_literals
import os
import urllib

from celery import Celery
from celery import task
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from django.utils.timezone import make_aware
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbase.settings')

app = Celery('carbase')

app.config_from_object('django.conf:settings', namespace='CELERY')


@task
def update_revoked_keys():
    from pki.models import RevokedCertificate
    crl = urllib.request.urlopen('http://crl.pki.gov.kz/rsa.crl')
    cert_crl = x509.load_der_x509_crl(crl.read(), default_backend())
    now = datetime.now()
    for r in cert_crl:
        if (now - r.revocation_date).days == 0:
            RevokedCertificate.objects.get_or_create(
                revocation_date=make_aware(r.revocation_date),
                serial_number=r.serial_number
            )
