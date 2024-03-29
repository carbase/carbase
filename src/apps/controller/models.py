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
