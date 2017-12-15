# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-15 10:30
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('unittests', '0014_auto_20171215_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='bandpassanalysis',
            name='analysis_results',
            field=jsonfield.fields.JSONField(blank=True),
        ),
        migrations.AddField(
            model_name='noisetemperatureanalysis',
            name='analysis_results',
            field=jsonfield.fields.JSONField(blank=True),
        ),
        migrations.AddField(
            model_name='spectralanalysis',
            name='analysis_results',
            field=jsonfield.fields.JSONField(blank=True),
        ),
    ]