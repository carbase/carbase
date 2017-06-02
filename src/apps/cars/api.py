from django.db import models
from django.conf import settings


def get_cars_by_iin(iin):
    return Car.objects.filter(user=iin)


def get_fines_by_iin(iin):
    return Fine.objects.filter(car__user=iin)


def get_taxes_by_iin(iin):
    return Tax.objects.filter(car__user=iin)


def pay_by_id(product_id):
    if product_id.startswith('tax'):
        tax = Tax.objects.get(id=product_id[3:])
        tax.is_paid = True
        tax.save()
    elif product_id.startswith('fine'):
        fine = Fine.objects.get(id=product_id[4:])
        fine.is_paid = True
        fine.save()
    elif product_id.startswith('reg'):
        reg = Reregestration.objects.get(id=product_id[3:])
        reg.is_paid = True
        reg.save()


class Car(models.Model):
    manufacturer = models.CharField(max_length=256, default='')
    model = models.CharField(max_length=256, default='')
    user = models.CharField(max_length=20, default='')
    number = models.CharField(max_length=16, default='')
    vin_code = models.CharField(max_length=20, default='')
    color_text = models.CharField(max_length=64, default='', blank=True)
    color_code = models.CharField(max_length=16, default='', blank=True)
    year = models.CharField(max_length=5, default='', blank=True)
    passport_number = models.CharField(max_length=64, default='', blank=True)
    engine_capacity = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.manufacturer + ' ' + self.model


class Tax(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    info = models.TextField()
    is_paid = models.BooleanField()
    car = models.ForeignKey(Car)

    class Meta:
        verbose_name_plural = "taxes"


class Fine(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    info = models.TextField()
    is_paid = models.BooleanField()
    car = models.ForeignKey(Car)


class Reregestration(models.Model):
    seller = models.CharField(max_length=20, default='', blank=True)
    buyer = models.CharField(max_length=20, default='', blank=True)
    car = models.ForeignKey(Car)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    amount_text = models.CharField(max_length=256, blank=True)
    seller_sign = models.TextField(blank=True)
    buyer_sign = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_tax_paid = models.BooleanField(default=False)
    inspection_time = models.CharField(max_length=20, default='', blank=True)
    is_inspection_success = models.BooleanField(default=False)
    is_number_received = models.BooleanField(default=False)
