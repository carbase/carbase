from django.db import models


def get_cars_by_iin(iin):
    return Car.objects.filter(user=iin)


def get_cars_by_bin(bin):
    return Car.objects.filter(user=bin)


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
        reg = Reregistration.objects.get(id=product_id[3:])
        reg.is_paid = True
        reg.save()


def get_email_by_iin(iin):
    try:
        email_obj = Email.objects.get(iin=iin)
        return email_obj.email
    except Email.ObjectDoesNotExist:
        pass


class Car(models.Model):
    manufacturer = models.CharField(max_length=256, default='')
    model = models.CharField(max_length=256, default='')
    user = models.CharField(max_length=20, default='')
    number = models.CharField(max_length=16, default='', blank=True)
    vin_code = models.CharField(max_length=20, default='')
    color_text = models.CharField(max_length=64, default='', blank=True)
    color_code = models.CharField(max_length=16, default='', blank=True)
    year = models.CharField(max_length=5, default='', blank=True)
    passport_number = models.CharField(max_length=64, default='', blank=True)
    engine_capacity = models.IntegerField(default=0, blank=True)
    is_registred = models.BooleanField(default=True)

    def __str__(self):
        return self.manufacturer + ' ' + self.model

    def reregistration(self):
        reregistrations = self.reregistration_set.exclude(is_number_received=True)
        return (reregistrations[0] if len(reregistrations) else None)

    def deregistration(self):
        deregistrations = self.deregistration_set.exclude(is_success=True)
        return (deregistrations[0] if len(deregistrations) else None)


class Deregistration(models.Model):
    is_paid = models.BooleanField()
    is_transit_number = models.BooleanField()
    car = models.ForeignKey(Car)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_success = models.BooleanField()


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


class Reregistration(models.Model):
    seller = models.CharField(max_length=20, default='', blank=True)
    buyer = models.CharField(max_length=20, default='', blank=True)
    car = models.ForeignKey(Car)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    amount_text = models.CharField(max_length=256, blank=True)
    number = models.CharField(max_length=8, blank=True, default='')
    seller_sign = models.TextField(blank=True)
    buyer_sign = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_tax_paid = models.BooleanField(default=False)
    is_number_received = models.BooleanField(default=False)


class Email(models.Model):
    iin = models.CharField(max_length=12)
    email = models.CharField(max_length=256)
