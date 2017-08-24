from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template import Context, Template


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


class AgreementTemplate(models.Model):
    ''' Шаблон договора '''
    template = models.TextField()
    owner = models.CharField(max_length=22, null=True, blank=True)
    is_selected = models.BooleanField()
    is_active = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    display_name = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.display_name if self.display_name else ''


class Agreement(models.Model):
    ''' Каждый конкретный экземпляр договора '''
    template = models.ForeignKey(AgreementTemplate)
    context = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def render(self, content_type='html'):
        template = Template(self.template.template)
        context = Context(self.context)
        context['reregistration'] = Reregistration.objects.get(agreement=self)
        return template.render(context)


class Sign(models.Model):
    ''' Подписи договора. '''
    key_info = models.TextField()
    signed_info = models.TextField()
    signature_value = models.TextField()
    agreement = models.ForeignKey(Agreement)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Car(models.Model):
    ''' ТС. Временная модель для хранения авто (в будущем возможно использования его как временного кэша) '''
    manufacturer = models.CharField(max_length=256, default='')
    model = models.CharField(max_length=256, default='')
    user = models.CharField(max_length=20, default='')
    number = models.CharField(max_length=16, default='', blank=True)
    vin_code = models.CharField(max_length=20, default='')
    color_text = models.CharField(max_length=64, default='', blank=True)
    color_code = models.CharField(max_length=16, default='', blank=True)
    year = models.CharField(max_length=5, default='', blank=True)
    passport_number = models.CharField(max_length=64, default='', blank=True)
    engine_capacity = models.DecimalField(default=0, max_digits=5, decimal_places=3, blank=True)
    is_registred = models.BooleanField(default=True)

    def __str__(self):
        return self.manufacturer + ' ' + self.model

    def reregistration(self):
        ''' Получение текущего процесса перерегистрации ТС '''
        reregistrations = self.reregistration_set.exclude(is_number_received=True)
        return (reregistrations[0] if len(reregistrations) else None)

    def deregistration(self):
        ''' Получение текущего процесса снятия с учета ТС '''
        deregistrations = self.deregistration_set.exclude(is_success=True)
        return (deregistrations[0] if len(deregistrations) else None)


class Deregistration(models.Model):
    ''' Снятие с учета '''
    is_paid = models.BooleanField()
    is_transit_number = models.BooleanField()
    car = models.ForeignKey(Car)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_success = models.BooleanField()


class Tax(models.Model):
    ''' Налоги '''
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    info = models.TextField()
    is_paid = models.BooleanField()
    car = models.ForeignKey(Car)

    class Meta:
        verbose_name_plural = "taxes"


class Fine(models.Model):
    ''' Штрафы '''
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    info = models.TextField()
    is_paid = models.BooleanField()
    car = models.ForeignKey(Car)


class Reregistration(models.Model):
    ''' Перерегистрация '''
    seller = models.CharField(max_length=20, default='', blank=True)
    buyer = models.CharField(max_length=20, default='', blank=True)
    car = models.ForeignKey(Car)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    amount_text = models.CharField(max_length=256, blank=True)
    number = models.CharField(max_length=8, blank=True, default='')
    agreement = models.ForeignKey(Agreement, null=True, blank=True)
    seller_sign = models.TextField(blank=True)  # Что бы не делать лишние joinы подписи дублируются
    buyer_sign = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_tax_paid = models.BooleanField(default=False)
    is_number_received = models.BooleanField(default=False)


class Email(models.Model):
    iin = models.CharField(max_length=12)
    email = models.CharField(max_length=256)
