from django.db import models
from django.contrib.auth.models import User
from cars.models import Reregistration


class Center(models.Model):
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=128)


class Inspector(models.Model):
    user = models.OneToOneField(User)
    center = models.ForeignKey(Center)


class Inspection(models.Model):
    center = models.ForeignKey(Center, null=True)
    date = models.DateField(null=True)
    time_range = models.CharField(max_length=11, null=True)
    is_success = models.BooleanField(default=False)
    inspector = models.ForeignKey(Inspector, null=True)
    reregistration = models.OneToOneField(Reregistration, null=True)