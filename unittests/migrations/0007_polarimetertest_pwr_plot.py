# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-25 04:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unittests', '0006_auto_20171124_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='polarimetertest',
            name='pwr_plot',
            field=models.ImageField(blank=True, max_length=1024, upload_to='plots/'),
        ),
    ]