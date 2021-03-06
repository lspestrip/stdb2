# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-27 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import unittests.validators


class Migration(migrations.Migration):

    dependencies = [
        ('unittests', '0007_polarimetertest_pwr_plot'),
    ]

    operations = [
        migrations.AddField(
            model_name='bandpassanalysis',
            name='report_file',
            field=models.FileField(blank=True, upload_to='reports/', validators=[unittests.validators.validate_report_file_ext], verbose_name='Report'),
        ),
        migrations.AddField(
            model_name='noisetemperatureanalysis',
            name='report_file',
            field=models.FileField(blank=True, upload_to='reports/', validators=[unittests.validators.validate_report_file_ext], verbose_name='Report'),
        ),
        migrations.AddField(
            model_name='spectralanalysis',
            name='report_file',
            field=models.FileField(blank=True, upload_to='reports/', validators=[unittests.validators.validate_report_file_ext], verbose_name='Report'),
        ),
    ]
