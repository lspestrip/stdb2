# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-28 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unittests', '0010_auto_20171127_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adcoffset',
            name='q1_adu',
            field=models.IntegerField(verbose_name='PWR0 (Q1) offset [ADU]'),
        ),
        migrations.AlterField(
            model_name='adcoffset',
            name='q2_adu',
            field=models.IntegerField(verbose_name='PWR3 (Q2) offset [ADU]'),
        ),
        migrations.AlterField(
            model_name='adcoffset',
            name='u1_adu',
            field=models.IntegerField(verbose_name='PWR1 (U1) offset [ADU]'),
        ),
        migrations.AlterField(
            model_name='adcoffset',
            name='u2_adu',
            field=models.IntegerField(verbose_name='PWR2 (U2) offset [ADU]'),
        ),
        migrations.AlterField(
            model_name='detectoroutput',
            name='q1_adu',
            field=models.IntegerField(verbose_name='PW0 (Q1)'),
        ),
        migrations.AlterField(
            model_name='detectoroutput',
            name='q2_adu',
            field=models.IntegerField(verbose_name='PW3 (Q2)'),
        ),
        migrations.AlterField(
            model_name='detectoroutput',
            name='u1_adu',
            field=models.IntegerField(verbose_name='PW1 (U1)'),
        ),
        migrations.AlterField(
            model_name='detectoroutput',
            name='u2_adu',
            field=models.IntegerField(verbose_name='PW2 (U2)'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_cross_guide_1',
            field=models.FloatField(verbose_name='T<sub>Cross1</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_cross_guide_2',
            field=models.FloatField(verbose_name='T<sub>Cross2</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_load_a_1',
            field=models.FloatField(verbose_name='Tload<sub>A1</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_load_a_2',
            field=models.FloatField(verbose_name='Tload<sub>A2</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_load_b_1',
            field=models.FloatField(verbose_name='Tload<sub>B1</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_load_b_2',
            field=models.FloatField(verbose_name='Tload<sub>B2</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_polarimeter_1',
            field=models.FloatField(verbose_name='T<sub>Pol1</sub> [K]'),
        ),
        migrations.AlterField(
            model_name='temperatures',
            name='t_polarimeter_2',
            field=models.FloatField(verbose_name='T<sub>Pol2</sub> [K]'),
        ),
    ]
