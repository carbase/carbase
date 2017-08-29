import datetime

from django.db import models
from django.contrib.auth.models import User
from cars.models import Reregistration, Deregistration, Registration


class Center(models.Model):
    ''' Спеццоны '''
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
    ''' Инспектора '''
    user = models.OneToOneField(User)
    center = models.ForeignKey(Center)
    role = models.CharField(max_length=3, choices=INSPECTOR_ROLE_CHOISES, default='rev')

    def __str__(self):
        return self.user.username


class Inspection(models.Model):
    ''' Проверки.
        Инстанс модели создается пользователем во время бронирования на последнем шаге
        перерегистрации или снятия учета
        Затем в три этапа (предварительная проверка, сверка и заключение) заполняется сотрудниками спецЦона
        Каждый этап содержит три поля
            is_..._success - успешность проверки
            ..._result - результат проверки (время проверки, причины отказа и тд)
            ..._sign - подписанный ЭЦП xml-результат проверки
    '''
    reregistration = models.OneToOneField(Reregistration, null=True)  # Либо это перерегистрация
    deregistration = models.OneToOneField(Deregistration, null=True)  # Либо снятие с учета
    registration = models.OneToOneField(Registration, null=True)      # Либо постановка на учет
    center = models.ForeignKey(Center, null=True)
    date = models.DateField(null=True)
    time_range = models.CharField(max_length=11, null=True)
    time = models.CharField(max_length=6, null=True)
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

    def get_process(self):
        if self.reregistration:
            return self.reregistration
        elif self.registration:
            return self.reregistration
        elif self.deregistration:
            return self.reregistration

    def save(self, *args, **kwargs):
        if self.time_range:
            times_by_range = {
                '9:00-12:00': ['9:00', '9:20', '9:40', '10:00', '10:20', '10:40', '11:00', '11:20', '11:40'],
                '12:00-15:00': ['12:00', '12:20', '12:40', '13:00', '13:20', '13:40', '14:00', '14:20', '14:40'],
                '15:00-18:00': ['15:00', '15:20', '15:40', '16:00', '16:20', '16:40', '17:00', '17:20', '17:40'],
            }
            ins_date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            other_inspections = Inspection.objects.filter(center=self.center).exclude(pk=self.pk)
            other_inspections.filter(date__year=ins_date.year, date__month=ins_date.month, date__day=ins_date.day)
            for other_ins in other_inspections:
                times_by_range[other_ins.time_range].remove(other_ins.time)
            if len(times_by_range[self.time_range]):
                self.time = times_by_range[self.time_range][0]
            else:
                raise ValueError('Нет свободного времени')
        super(Inspection, self).save(*args, **kwargs)
