from django.db import models
from django.contrib.auth.models import User
from cars.models import Reregistration, Deregistration


class Center(models.Model):
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    def __str__(self):
        return '{} {}'.format(self.city, self.address)


class Inspector(models.Model):
    user = models.OneToOneField(User)
    center = models.ForeignKey(Center)

    def __str__(self):
        return self.user.username


class Inspection(models.Model):
    center = models.ForeignKey(Center, null=True)
    date = models.DateField(null=True)
    time_range = models.CharField(max_length=11, null=True)
    is_success = models.BooleanField(default=False)
    inspector = models.ForeignKey(Inspector, null=True)
    reregistration = models.OneToOneField(Reregistration, null=True)
    deregistration = models.OneToOneField(Deregistration, null=True)
