from datetime import datetime

from django.db import models
from django.conf import settings

from controller.models import Center

class NumberPlate(models.Model):
    # 001,100,777,etc.
    digits = models.CharField(max_length=3)
    # RRR,NNN,ABC,etc.
    characters = models.CharField(max_length=3)
    # 01,02,03,etc.
    region = models.CharField(max_length=2)
    # True if sold
    is_sold = models.BooleanField(default=False)
    # When was sold
    sale_date = models.DateField(null=True, blank=True)
    # Owner IIN
    owner_id = models.CharField(max_length=12, blank=True)
    # Buyer IIN
    buyer_id = models.CharField(max_length=12, blank=True)
    # Form setup
    is_installed = models.BooleanField(default=False)
    # CON
    center = models.ForeignKey(Center, null=True)

    class Meta:
        ordering = ['digits']

    def __str__(self):
        return '{}{}{}'.format(self.digits, self.characters, self.region)

    def set_owner(self, user_id):
        self.buyer_id = user_id
        self.owner_id = user_id
        self.is_sold = True
        self.sale_date = datetime.now()

    def get_price(self):
        if self.digits in settings.VIP1:
            return settings.VIP1_TAX * settings.MCI
        elif self.digits in settings.VIP2:
            return settings.VIP2_TAX * settings.MCI
        else:
            return settings.GRNZ_TAX * settings.MCI
