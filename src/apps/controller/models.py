from django.db import models
from django.contrib.auth.models import User
from cars.models import Reregistration, Deregistration


class Center(models.Model):
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    def __str__(self):
        return '{} {}'.format(self.city, self.address)


INSPECTOR_ROLE_CHOISES = (
    ('rev', 'revisor'),
    ('all', 'allower'),
    ('adm', 'administrator')
)


class Inspector(models.Model):
    user = models.OneToOneField(User)
    center = models.ForeignKey(Center)
    role = models.CharField(max_length=3, choices=INSPECTOR_ROLE_CHOISES, default='rev')

    def __str__(self):
        return self.user.username


class Inspection(models.Model):
    reregistration = models.OneToOneField(Reregistration, null=True)
    deregistration = models.OneToOneField(Deregistration, null=True)
    center = models.ForeignKey(Center, null=True)
    date = models.DateField(null=True)
    time_range = models.CharField(max_length=11, null=True)
    allower = models.ForeignKey(Inspector, null=True, related_name='allower')
    is_prelimenary_success = models.NullBooleanField(null=True)
    prelimenary_result = models.TextField(null=True, blank=True)
    prelimenary_sign = models.TextField(null=True, blank=True)
    revisor = models.ForeignKey(Inspector, null=True, related_name='revisor')
    is_revision_success = models.NullBooleanField(null=True)
    revision_result = models.TextField(null=True, blank=True)
    revision_sign = models.TextField(null=True, blank=True)
    is_success = models.BooleanField(default=False)
    result = models.TextField(null=True, blank=True)
    sign = models.TextField(null=True, blank=True)
