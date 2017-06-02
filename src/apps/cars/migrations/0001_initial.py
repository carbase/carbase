# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-02 04:20
from __future__ import unicode_literals

import cars.api
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('amount_text', models.CharField(max_length=256)),
                ('seller_sign', models.TextField()),
                ('buyer_sign', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_tax_paid', models.BooleanField(default=False)),
                ('inspection_time', models.CharField(default='', max_length=20)),
                ('is_inspection_success', models.BooleanField(default=False)),
                ('is_number_received', models.BooleanField(default=False)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_agreements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=cars.api.car_image_dir_path)),
                ('manufacturer', models.CharField(default='', max_length=256)),
                ('model', models.CharField(default='', max_length=256)),
                ('number', models.CharField(default='', max_length=16)),
                ('vin_code', models.CharField(default='', max_length=20)),
                ('color_text', models.CharField(default='', max_length=64)),
                ('color_code', models.CharField(blank=True, default='', max_length=16)),
                ('year', models.CharField(default='', max_length=5)),
                ('passport_number', models.CharField(default='', max_length=64)),
                ('engine_capacity', models.IntegerField(default=0)),
                ('user', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('info', models.TextField()),
                ('is_paid', models.BooleanField()),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.Car')),
            ],
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('info', models.TextField()),
                ('is_paid', models.BooleanField()),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.Car')),
            ],
            options={
                'verbose_name_plural': 'taxes',
            },
        ),
        migrations.AddField(
            model_name='agreement',
            name='car',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.Car'),
        ),
        migrations.AddField(
            model_name='agreement',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_agreements', to=settings.AUTH_USER_MODEL),
        ),
    ]
