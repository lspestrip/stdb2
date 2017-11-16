# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-16 05:11
from __future__ import unicode_literals

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
            name='AdcOffset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pwr0_adu', models.IntegerField()),
                ('pwr1_adu', models.IntegerField()),
                ('pwr2_adu', models.IntegerField()),
                ('pwr3_adu', models.IntegerField()),
            ],
            options={
                'verbose_name': 'values of the four ADC offsets',
            },
        ),
        migrations.CreateModel(
            name='BandpassAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('central_frequency_ghz', models.FloatField(verbose_name='central frequency [GHz]')),
                ('central_frequency_err', models.FloatField(verbose_name='error on central frequency')),
                ('bandwidth_ghz', models.FloatField(verbose_name='bandwidth [GHz]')),
                ('bandwidth_err', models.FloatField(verbose_name='error on bandwidth')),
                ('code_version', models.CharField(max_length=12, verbose_name='version number of the analysis code')),
                ('code_commit', models.CharField(max_length=40, verbose_name='last commit hash of the analysis code')),
                ('analysis_date', models.DateTimeField(verbose_name='date when the analysis was done')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spectrum_owned', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'noise analysis for tests done in stable conditions',
            },
        ),
        migrations.CreateModel(
            name='Biases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('h0_vdrain', models.FloatField(verbose_name='H0 Vdrain [V]')),
                ('h0_idrain', models.FloatField(verbose_name='H0 Idrain [mA]')),
                ('h0_vgate', models.FloatField(verbose_name='H0 Vgate [mV]')),
                ('h1_vdrain', models.FloatField(verbose_name='H1 Vdrain [V]')),
                ('h1_idrain', models.FloatField(verbose_name='H1 Idrain [mA]')),
                ('h1_vgate', models.FloatField(verbose_name='H1 Vgate [mV]')),
                ('h2_vdrain', models.FloatField(verbose_name='H2 Vdrain [V]')),
                ('h2_idrain', models.FloatField(verbose_name='H2 Idrain [mA]')),
                ('h2_vgate', models.FloatField(verbose_name='H2 Vgate [mV]')),
                ('h3_vdrain', models.FloatField(verbose_name='H3 Vdrain [V]')),
                ('h3_idrain', models.FloatField(verbose_name='H3 Idrain [mA]')),
                ('h3_vgate', models.FloatField(verbose_name='H3 Vgate [mV]')),
                ('h4_vdrain', models.FloatField(verbose_name='H4 Vdrain [V]')),
                ('h4_idrain', models.FloatField(verbose_name='H4 Idrain [mA]')),
                ('h4_vgate', models.FloatField(verbose_name='H4 Vgate [mV]')),
                ('h5_vdrain', models.FloatField(verbose_name='H5 Vdrain [V]')),
                ('h5_idrain', models.FloatField(verbose_name='H5 Idrain [mA]')),
                ('h5_vgate', models.FloatField(verbose_name='H5 Vgate [mV]')),
            ],
            options={
                'verbose_name': 'biases used in the six HEMTs',
            },
        ),
        migrations.CreateModel(
            name='DetectorOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pwr0_adu', models.IntegerField()),
                ('pwr1_adu', models.IntegerField()),
                ('pwr2_adu', models.IntegerField()),
                ('pwr3_adu', models.IntegerField()),
            ],
            options={
                'verbose_name': 'average output of the four detectors',
            },
        ),
        migrations.CreateModel(
            name='NoiseTemperatureAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polarimeter_gain', models.FloatField()),
                ('polarimeter_gain_err', models.FloatField()),
                ('gain_product', models.FloatField()),
                ('gain_product_err', models.FloatField()),
                ('noise_temperature', models.FloatField()),
                ('noise_temperature_err', models.FloatField()),
                ('estimation_method', models.CharField(blank=True, max_length=24)),
                ('code_version', models.CharField(max_length=12, verbose_name='version number of the analysis code')),
                ('code_commit', models.CharField(max_length=40, verbose_name='last commit hash of the analysis code')),
                ('analysis_date', models.DateTimeField(verbose_name='date when the analysis was done')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tnoise_owned', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'noise temperature and gain estimates',
            },
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='PolarimeterTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polarimeter_number', models.IntegerField(verbose_name='Number of the polarimeter')),
                ('cryogenic', models.BooleanField(verbose_name='Cryogenic test')),
                ('acquisition_date', models.DateField(verbose_name='Date of acquisition (YY-MM-DD)')),
                ('data_file', models.FileField(max_length=1024, upload_to='unit_test_data/')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('phsw_state', models.CharField(choices=[('0000', '0000'), ('0101', '0101'), ('1010', '1010'), ('switching', 'switching')], default='0000', max_length=12)),
                ('band', models.CharField(choices=[('Q', 'Q'), ('W', 'W')], max_length=1)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests_owned', to=settings.AUTH_USER_MODEL)),
                ('operators', models.ManyToManyField(related_name='tests', to='unittests.Operator')),
            ],
            options={
                'verbose_name': 'test of a polarimetric unit',
                'ordering': ['polarimeter_number', 'acquisition_date'],
                'get_latest_by': 'acquisition_date',
            },
        ),
        migrations.CreateModel(
            name='SpectralAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oof_alpha', models.FloatField(verbose_name='1/f noise slope')),
                ('oof_alpha_err', models.FloatField(verbose_name='error on 1/f noise slope')),
                ('oof_knee_frequency_hz', models.FloatField(verbose_name='1/f knee frequency [Hz]')),
                ('oof_knee_frequency_err', models.FloatField(verbose_name='error on 1/f knee frequency')),
                ('wn_level_adu2_rhz', models.FloatField(verbose_name='white noise level [ADU^2]')),
                ('wn_level_err', models.FloatField(verbose_name='error on white noise level')),
                ('sampling_frequency_hz', models.FloatField(default=25.0, verbose_name='sampling frequency [Hz]')),
                ('code_version', models.CharField(max_length=12, verbose_name='version number of the analysis code')),
                ('code_commit', models.CharField(max_length=40, verbose_name='last commit hash of the analysis code')),
                ('analysis_date', models.DateTimeField(verbose_name='date when the analysis was done')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bandpass_owned', to=settings.AUTH_USER_MODEL)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest')),
            ],
            options={
                'verbose_name': 'noise analysis for tests done in stable conditions',
            },
        ),
        migrations.CreateModel(
            name='Temperatures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('t_load_a_1', models.FloatField(verbose_name='Tload_A1 [K]')),
                ('t_load_a_2', models.FloatField(verbose_name='Tload_A2 [K]')),
                ('t_load_b_1', models.FloatField(verbose_name='Tload_B1 [K]')),
                ('t_load_b_2', models.FloatField(verbose_name='Tload_B2 [K]')),
                ('t_cross_guide_1', models.FloatField(verbose_name='Tcross1 [K]')),
                ('t_cross_guide_2', models.FloatField(verbose_name='Tcross2 [K]')),
                ('t_polarimeter_1', models.FloatField(verbose_name='Tpolarimeter1 [K]')),
                ('t_polarimeter_2', models.FloatField(verbose_name='Tpolarimeter2 [K]')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest')),
            ],
            options={
                'verbose_name': 'temperatures of the cryochamber',
            },
        ),
        migrations.CreateModel(
            name='TestType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'type of test',
                'ordering': ['description'],
            },
        ),
        migrations.AddField(
            model_name='polarimetertest',
            name='test_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.TestType'),
        ),
        migrations.AddField(
            model_name='noisetemperatureanalysis',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest'),
        ),
        migrations.AddField(
            model_name='detectoroutput',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest'),
        ),
        migrations.AddField(
            model_name='biases',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest'),
        ),
        migrations.AddField(
            model_name='bandpassanalysis',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest'),
        ),
        migrations.AddField(
            model_name='adcoffset',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unittests.PolarimeterTest'),
        ),
    ]
