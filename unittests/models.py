# -*- encoding: utf-8 -*-

'''Database model for the "unittest" application

This module provides the definition of the database tables and fields used by
"unittest", the application which keeps track of the raw data and the analysis
results of the polarimetric unit tests done in Bicocca.

The core of the module is the "PolarimeterTest" class, which is typically
associated to one datafile acquired using the electronic board or to one set of
Excel files acquired using the Keithley apparatus. All the other classes provide
additional (and often optional) information about the test.abs

The main reason why the structure of tables seems so complicated stems from the
need of great versatility. Since no housekeeping information was recorded during
the tests, the code cannot assume that information such as amplifier biases,
housekeeping temperatures, and so on is available and ready to be put in the
database.
'''

import logging
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files import File
from .file_conversions import convert_data_file_to_h5

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


class TestType(models.Model):
    'Kind of test (e.g., Y-factor)'
    description = models.CharField(max_length=80)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'type of test'
        ordering = ['description']


class Operator(models.Model):
    'Person who has run a test'

    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


BAND_CHOICES = (
    ('Q', 'Q'),
    ('W', 'W'),
)

PHSW_STATES = (
    ('N/A', 'N/A'),
    ('0101', '0101'),
    ('0110', '0110'),
    ('switching', 'switching'),
    ('1010', '1010'),
    ('1001', '1001'),
)


class PolarimeterTest(models.Model):
    'A dedicated test done on one polarimeter'

    polarimeter_number = models.IntegerField(
        verbose_name='Number of the polarimeter')
    cryogenic = models.BooleanField(verbose_name='Cryogenic test')
    acquisition_date = models.DateField(
        verbose_name='Date of acquisition (YYYY-MM-DD)')
    data_file = models.FileField(max_length=1024, upload_to='unit_test_data/')
    notes = models.TextField(verbose_name='Notes', blank=True)
    phsw_state = models.CharField(
        max_length=12, default='N/A', choices=PHSW_STATES)
    band = models.CharField(max_length=1, choices=BAND_CHOICES)

    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    operators = models.ManyToManyField(Operator, related_name='tests')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tests_owned')
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{0} {1} ({2})'.format(
            self.polarimeter_name,
            self.test_type,
            self.acquisition_date,
        )

    @property
    def polarimeter_name(self):
        return 'STRIP{0:02d}'.format(self.polarimeter_number)

    def get_absolute_url(self):
        return reverse('unittests:test_details', kwargs={'test_id': self.pk})

    def get_download_url(self):
        return reverse('unittests:test_download', kwargs={'test_id': self.pk})

    def get_json_url(self):
        return reverse('unittests:test_details_json', kwargs={'test_id': self.pk})

    def get_delete_url(self):
        return reverse('unittests:test_delete', kwargs={'pk': self.pk})

    @property
    def get_file_size_in_kb(self):
        return int(self.data_file.size / 1024)

    def save(self, *args, **kwargs):
        if self.data_file:
            # Remove weird characters from the description of the test type
            test_type = ''.join(filter(str.isalpha,
                                       self.test_type.description))
            hdf5_file_name = ('{polname}_{date}_{testtype}.h5'
                              .format(polname=self.polarimeter_name,
                                      date=self.acquisition_date.strftime(
                                          '%Y-%m-%d'),
                                      testtype=test_type))
            LOGGER.debug('going to create a temporary HDF5 file in "%s"',
                         hdf5_file_name)
            with NamedTemporaryFile(suffix='.h5', delete=False) as temporary_file:
                tmp_file_name = temporary_file.name
                convert_data_file_to_h5(
                    self.data_file.name, self.data_file, temporary_file.name)

            LOGGER.debug('importing HDF5 file "%s" into the database',
                         hdf5_file_name)
            with open(tmp_file_name, 'rb') as temporary_file:
                self.data_file = File(temporary_file, hdf5_file_name)

                super(PolarimeterTest, self).save(*args, **kwargs)

            os.remove(tmp_file_name)
            LOGGER.debug(
                'HDF5 file "%s" imported in the database and removed', hdf5_file_name)
        else:
            super(PolarimeterTest, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'test of a polarimetric unit'
        ordering = ['polarimeter_number', 'acquisition_date']
        get_latest_by = 'acquisition_date'


class AdcOffset(models.Model):
    'Offset configuration used for the four ADCs'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)
    pwr0_adu = models.IntegerField()
    pwr1_adu = models.IntegerField()
    pwr2_adu = models.IntegerField()
    pwr3_adu = models.IntegerField()

    def __str__(self):
        return 'PWR0={0} ADU, PWR1={1} ADU, PWR2={2} ADU, PWR3={3} ADU'.format(
            self.pwr0_adu,
            self.pwr1_adu,
            self.pwr2_adu,
            self.pwr3_adu
        )

    class Meta:
        verbose_name = 'values of the four ADC offsets'


class DetectorOutput(models.Model):
    'Average output of the four detectors'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)
    pwr0_adu = models.IntegerField()
    pwr1_adu = models.IntegerField()
    pwr2_adu = models.IntegerField()
    pwr3_adu = models.IntegerField()

    def __str__(self):
        return 'PWR0={0} ADU, PWR1={1} ADU, PWR2={2} ADU, PWR3={3} ADU'.format(
            self.pwr0_adu,
            self.pwr1_adu,
            self.pwr2_adu,
            self.pwr3_adu
        )

    class Meta:
        verbose_name = 'average output of the four detectors'


def dict_to_detector_output(data):
    return DetectorOutput(
        pwr0_adu=data['detector_offsets']['PWR0_adu'],
        pwr1_adu=data['detector_offsets']['PWR1_adu'],
        pwr2_adu=data['detector_offsets']['PWR2_adu'],
        pwr3_adu=data['detector_offsets']['PWR3_adu'],
    )


class Biases(models.Model):
    'Biases used to polarize the HEMTs'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    drain_voltage_ha1_V = models.FloatField(verbose_name='H0 drain voltage [V]')
    drain_current_ha1_mA = models.FloatField(verbose_name='H0 drain current [mA]')
    gate_voltage_ha1_mV = models.FloatField(verbose_name='H0 gate voltage [mV]')

    drain_voltage_hb1_V = models.FloatField(verbose_name='H1 drain voltage [V]')
    drain_current_hb1_mA = models.FloatField(verbose_name='H1 drain current [mA]')
    gate_voltage_hb1_mV = models.FloatField(verbose_name='H1 gate voltage [mV]')

    drain_voltage_ha2_V = models.FloatField(verbose_name='H2 drain voltage [V]')
    drain_current_ha2_mA = models.FloatField(verbose_name='H2 drain current [mA]')
    gate_voltage_ha2_mV = models.FloatField(verbose_name='H2 gate voltage [mV]')

    drain_voltage_hb2_V = models.FloatField(verbose_name='H3 drain voltage [V]')
    drain_current_hb2_mA = models.FloatField(verbose_name='H3 drain current [mA]')
    gate_voltage_hb2_mV = models.FloatField(verbose_name='H3 gate voltage [mV]')

    drain_voltage_ha3_V = models.FloatField(verbose_name='H4 drain voltage [V]')
    drain_current_ha3_mA = models.FloatField(verbose_name='H4 drain current [mA]')
    gate_voltage_ha3_mV = models.FloatField(verbose_name='H4 gate voltage [mV]')

    drain_voltage_hb3_V = models.FloatField(verbose_name='H5 drain voltage [V]')
    drain_current_hb3_mA = models.FloatField(verbose_name='H5 drain current [mA]')
    gate_voltage_hb3_mV = models.FloatField(verbose_name='H5 gate voltage [mV]')

    class Meta:
        verbose_name = 'HEMT polarization biases'


class Temperatures(models.Model):
    'Temperatures of the cryochamber'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    t_load_a_1 = models.FloatField(verbose_name='Tload_A1 [K]')
    t_load_a_2 = models.FloatField(verbose_name='Tload_A2 [K]')

    t_load_b_1 = models.FloatField(verbose_name='Tload_B1 [K]')
    t_load_b_2 = models.FloatField(verbose_name='Tload_B2 [K]')

    t_cross_guide_1 = models.FloatField(verbose_name='Tcross1 [K]')
    t_cross_guide_2 = models.FloatField(verbose_name='Tcross2 [K]')

    t_polarimeter_1 = models.FloatField(verbose_name='Tpolarimeter1 [K]')
    t_polarimeter_2 = models.FloatField(verbose_name='Tpolarimeter2 [K]')

    def __str__(self):
        return (
            'TloadA = {0:.1f} K, TloadB = {1:.1f} K, Tcross = {2:.1f} K, Tpol = {3:.1f}'
            .format(self.t_load_a_1, self.t_load_b_1, self.t_cross_guide_1, self.t_polarimeter_1)
        )

    class Meta:
        verbose_name = 'temperatures of the cryochamber'


class NoiseTemperatureAnalysis(models.Model):
    'Result of a noise temperature analysis'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    polarimeter_gain = models.FloatField()
    polarimeter_gain_err = models.FloatField()

    gain_product = models.FloatField()
    gain_product_err = models.FloatField()

    noise_temperature = models.FloatField()
    noise_temperature_err = models.FloatField()

    estimation_method = models.CharField(max_length=24, blank=True)

    code_version = models.CharField(max_length=12,
                                    verbose_name='version number of the analysis code')
    code_commit = models.CharField(max_length=40,
                                   verbose_name='last commit hash of the analysis code')
    analysis_date = models.DateTimeField('date when the analysis was done')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tnoise_owned')

    def __str__(self):
        return ('Tnoise={0} for {1}'
                .format(self.noise_temperature,
                        self.test.polarimeter_name))

    class Meta:
        verbose_name = 'noise temperature and gain estimates'


def dict_to_tnoise_analysis(data):
    return NoiseTemperatureAnalysis(
        polarimeter_gain=data['average_gain']['mean'],
        polarimeter_gain_err=data['average_gain']['std'],
        gain_product=data['gain_prod']['mean'],
        gain_product_err=data['gain_prod']['std'],
        noise_temperature=data['tnoise']['mean'],
        noise_temperature_err=data['tnoise']['std'],
        estimation_method=data['estimation_method'],
        code_version=data['striptun_version'],
        code_commit=data['latest_git_commit'],
        analysis_date=data['date']
    )


class SpectralAnalysis(models.Model):
    'Results of the analysis of a long-acquisition test'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    oof_alpha = models.FloatField(verbose_name='1/f noise slope')
    oof_alpha_err = models.FloatField(verbose_name='error on 1/f noise slope')
    oof_knee_frequency_hz = models.FloatField(
        verbose_name='1/f knee frequency [Hz]')
    oof_knee_frequency_err = models.FloatField(
        verbose_name='error on 1/f knee frequency')
    wn_level_adu2_rhz = models.FloatField(
        verbose_name='white noise level [ADU^2]')
    wn_level_err = models.FloatField(verbose_name='error on white noise level')
    sampling_frequency_hz = models.FloatField(
        verbose_name='sampling frequency [Hz]', default=25.0)

    code_version = models.CharField(max_length=12,
                                    verbose_name='version number of the analysis code')
    code_commit = models.CharField(max_length=40,
                                   verbose_name='last commit hash of the analysis code')
    analysis_date = models.DateTimeField('date when the analysis was done')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='spectral_owned')

    def __str__(self):
        return self.test.polarimeter_name

    class Meta:
        verbose_name = 'noise analysis for tests done in stable conditions'


class BandpassAnalysis(models.Model):
    'Results of the analysis of a bandpass test'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    central_frequency_ghz = models.FloatField(
        verbose_name='central frequency [GHz]')
    central_frequency_err = models.FloatField(
        verbose_name='error on central frequency')
    bandwidth_ghz = models.FloatField(verbose_name='bandwidth [GHz]')
    bandwidth_err = models.FloatField(verbose_name='error on bandwidth')

    code_version = models.CharField(max_length=12,
                                    verbose_name='version number of the analysis code')
    code_commit = models.CharField(max_length=40,
                                   verbose_name='last commit hash of the analysis code')
    analysis_date = models.DateTimeField('date when the analysis was done')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='bandpass_owned')

    def __str__(self):
        return self.test.polarimeter_name

    class Meta:
        verbose_name = 'noise analysis for tests done in stable conditions'
