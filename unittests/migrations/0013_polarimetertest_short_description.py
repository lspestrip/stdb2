# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-01 11:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unittests', '0012_auto_20171128_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='polarimetertest',
            name='short_description',
            field=models.CharField(blank=True, max_length=140, verbose_name='Short description (optional)'),
        ),
    ]
