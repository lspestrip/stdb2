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

from io import BytesIO
import logging
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files import File
from django.core.files.base import ContentFile
import h5py
import matplotlib as mpl

from jsonfield import JSONField

from .file_conversions import convert_data_file_to_h5
from .validators import validate_report_file_ext

mpl.use('Agg')
import matplotlib.pylab as plt

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


def create_pwr_plot(hdf5_file_name, dpi=80):
    'Plot PWR data from an HDF5 file into an image'

    plt.figure(figsize=(512 / dpi, 384 / dpi), dpi=dpi)
    with h5py.File(hdf5_file_name, 'r') as h5_file:
        if not 'time_series' in h5_file:
            # Do not attempt to make plots from a file containing Keithley data
            return None

        dataset = h5_file['time_series']
        time = dataset['time_s']

        for idx, detector in enumerate(['Q1', 'U1', 'U2', 'Q2']):
            column = 'pwr_{0}_ADU'.format(detector)
            pwr_name = 'PWR{0}'.format(idx)
            plt.plot(
                time, dataset[column], label='{0} ({1})'.format(pwr_name, detector))

    plt.xlabel('Time [s]')
    plt.ylabel('Output [ADU]')
    plt.legend()

    # Save the image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=dpi)

    return ContentFile(buffer.getvalue())


def update_hdf5_test_file_attrs(file_name, poltest):
    'Update HDF5 file attributes with information from a PolarimeterTest obj'

    if settings.HTTP_HOST and settings.HTTP_HOST != '':
        abs_url = ''.join([settings.HTTP_HOST,
                           poltest.get_absolute_url()])
    else:
        abs_url = poltest.get_absolute_url()

    with h5py.File(file_name, 'r+') as h5_file:
        for key, value in [('url', abs_url),
                           ('polarimeter', poltest.polarimeter_name),
                           ('cryogenic', poltest.cryogenic),
                           ('acquisition_date',
                            poltest.acquisition_date.strftime('%Y-%m-%d')),
                           ('band', poltest.band),
                           ('test_type', str(poltest.test_type))]:
            h5_file.attrs[key] = value


def get_polarimeter_name(num):
    return 'STRIP{0:02d}'.format(num)


class PolarimeterTest(models.Model):
    'A dedicated test done on one polarimeter'

    polarimeter_number = models.IntegerField(
        verbose_name='Number of the polarimeter')
    cryogenic = models.BooleanField(verbose_name='Cryogenic test')
    acquisition_date = models.DateField(
        verbose_name='Date of acquisition (YYYY-MM-DD)')
    data_file = models.FileField(max_length=1024, upload_to='unit_test_data/')
    short_description = models.CharField(max_length=140, blank=True,
                                         verbose_name='Short description (optional)')
    notes = models.TextField(verbose_name='Notes', blank=True)
    phsw_state = models.CharField(
        max_length=12, default='N/A', choices=PHSW_STATES)
    band = models.CharField(max_length=1, choices=BAND_CHOICES)

    pwr_plot = models.ImageField(
        max_length=1024, upload_to='plots/', blank=True)

    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    operators = models.ManyToManyField(Operator, related_name='tests')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tests_owned', on_delete=models.PROTECT)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{0} {1} ({2})'.format(
            self.polarimeter_name,
            self.test_type,
            self.acquisition_date,
        )

    @property
    def polarimeter_name(self):
        return get_polarimeter_name(self.polarimeter_number)

    @property
    def test_description(self):
        if self.short_description:
            return self.short_description
        else:
            return self.test_type.description

    def get_absolute_url(self):
        return reverse('unittests:test_details', kwargs={'test_id': self.pk})

    def get_download_url(self):
        return reverse('unittests:test_download', kwargs={'test_id': self.pk})

    def get_json_url(self):
        return reverse('unittests:test_details_json', kwargs={'test_id': self.pk})

    def get_delete_url(self):
        return reverse('unittests:test_delete', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.data_file:
            # Remove weird characters from the description of the test type
            test_type = ''.join(filter(str.isalpha,
                                       self.test_type.description))
            base_file_name = ('{polname}_{date}_{testtype}'
                              .format(polname=self.polarimeter_name,
                                      date=self.acquisition_date.strftime(
                                          '%Y-%m-%d'),
                                      testtype=test_type))
            hdf5_file_name = base_file_name + '.h5'
            LOGGER.debug('going to create a temporary HDF5 file in "%s"',
                         hdf5_file_name)
            with NamedTemporaryFile(suffix='.h5', delete=False) as temporary_file:
                tmp_file_name = temporary_file.name
                convert_data_file_to_h5(
                    self.data_file.name, self.data_file, temporary_file.name)
                image_file = create_pwr_plot(temporary_file.name)

            LOGGER.debug('importing HDF5 file "%s" into the database',
                         hdf5_file_name)
            with open(tmp_file_name, 'rb') as temporary_file:
                self.data_file = File(temporary_file, hdf5_file_name)

                if image_file:
                    self.pwr_plot.save(base_file_name + '.png',
                                       image_file, save=False)

                super(PolarimeterTest, self).save(*args, **kwargs)

            os.remove(tmp_file_name)
            LOGGER.debug(
                'HDF5 file "%s" imported in the database and removed, new file is "%s"',
                hdf5_file_name, self.data_file.name)

            update_hdf5_test_file_attrs(os.path.join(
                settings.MEDIA_ROOT, self.data_file.name), self)
            LOGGER.debug('metadata for file "%s" have been updated',
                         self.data_file.name)
        else:
            super(PolarimeterTest, self).save(*args, **kwargs)

    def to_dict(self):
        'Create a dictionary containing a summary of the test (useful for the REST API)'

        return {
            'id': self.pk,
            'polarimeter_number': self.polarimeter_number,
            'test_type': self.test_type.pk,
            'description': self.test_description,
            'absolute_url': self.get_absolute_url(),
            'download_url': self.get_download_url(),
            'json_url': self.get_json_url(),
        }

    class Meta:
        verbose_name = 'test of a polarimetric unit'
        ordering = ['polarimeter_number', 'acquisition_date']
        get_latest_by = 'acquisition_date'


class AdcOffset(models.Model):
    'Offset configuration used for the four ADCs'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)
    q1_adu = models.IntegerField(verbose_name='PWR0 (Q1) offset [ADU]')
    u1_adu = models.IntegerField(verbose_name='PWR1 (U1) offset [ADU]')
    u2_adu = models.IntegerField(verbose_name='PWR2 (U2) offset [ADU]')
    q2_adu = models.IntegerField(verbose_name='PWR3 (Q2) offset [ADU]')

    def __str__(self):
        return 'PWR0={0} ADU, PWR1={1} ADU, PWR2={2} ADU, PWR3={3} ADU'.format(
            self.q1_adu,
            self.u1_adu,
            self.u2_adu,
            self.q2_adu
        )

    def get_absolute_url(self):
        return self.test.get_absolute_url()

    class Meta:
        verbose_name = 'values of the four ADC offsets'


def dict_to_adc_offset_list(data):
    offsets = data['adc_offsets']
    if type(offsets) is dict:
        # We have just one set of outputs, so let's build a list with one element
        offsets = [offsets]

    return [AdcOffset(
        q1_adu=x['q1_adu'],
        u1_adu=x['u1_adu'],
        u2_adu=x['u2_adu'],
        q2_adu=x['q2_adu'],
    ) for x in offsets]


class DetectorOutput(models.Model):
    'Average output of the four detectors'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)
    q1_adu = models.IntegerField(verbose_name='PW0 (Q1)')
    u1_adu = models.IntegerField(verbose_name='PW1 (U1)')
    u2_adu = models.IntegerField(verbose_name='PW2 (U2)')
    q2_adu = models.IntegerField(verbose_name='PW3 (Q2)')

    def __str__(self):
        return 'PWR0={0} ADU, PWR1={1} ADU, PWR2={2} ADU, PWR3={3} ADU'.format(
            self.q1_adu,
            self.u1_adu,
            self.u2_adu,
            self.q2_adu
        )

    def get_absolute_url(self):
        return self.test.get_absolute_url()

    class Meta:
        verbose_name = 'average output of the four detectors'


def dict_to_detector_output_list(data):
    outputs = data['detector_outputs']
    if type(outputs) is dict:
        # We have just one set of outputs, so let's build a list with one element
        outputs = [outputs]

    return [DetectorOutput(
        q1_adu=x['q1_adu'],
        u1_adu=x['u1_adu'],
        u2_adu=x['u2_adu'],
        q2_adu=x['q2_adu'],
    ) for x in outputs]


class Biases(models.Model):
    'Biases used to polarize the HEMTs'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    drain_voltage_ha1_V = models.FloatField(
        verbose_name='H0 drain voltage [V]')
    drain_current_ha1_mA = models.FloatField(
        verbose_name='H0 drain current [mA]')
    gate_voltage_ha1_mV = models.FloatField(
        verbose_name='H0 gate voltage [mV]')

    drain_voltage_hb1_V = models.FloatField(
        verbose_name='H1 drain voltage [V]')
    drain_current_hb1_mA = models.FloatField(
        verbose_name='H1 drain current [mA]')
    gate_voltage_hb1_mV = models.FloatField(
        verbose_name='H1 gate voltage [mV]')

    drain_voltage_ha2_V = models.FloatField(
        verbose_name='H2 drain voltage [V]')
    drain_current_ha2_mA = models.FloatField(
        verbose_name='H2 drain current [mA]')
    gate_voltage_ha2_mV = models.FloatField(
        verbose_name='H2 gate voltage [mV]')

    drain_voltage_hb2_V = models.FloatField(
        verbose_name='H3 drain voltage [V]')
    drain_current_hb2_mA = models.FloatField(
        verbose_name='H3 drain current [mA]')
    gate_voltage_hb2_mV = models.FloatField(
        verbose_name='H3 gate voltage [mV]')

    drain_voltage_ha3_V = models.FloatField(
        verbose_name='H4 drain voltage [V]')
    drain_current_ha3_mA = models.FloatField(
        verbose_name='H4 drain current [mA]')
    gate_voltage_ha3_mV = models.FloatField(
        verbose_name='H4 gate voltage [mV]')

    drain_voltage_hb3_V = models.FloatField(
        verbose_name='H5 drain voltage [V]')
    drain_current_hb3_mA = models.FloatField(
        verbose_name='H5 drain current [mA]')
    gate_voltage_hb3_mV = models.FloatField(
        verbose_name='H5 gate voltage [mV]')

    def get_absolute_url(self):
        return self.test.get_absolute_url()

    class Meta:
        verbose_name = 'HEMT polarization biases'


def dict_to_biases(data):
    biases = data['hemt_biases']
    return Biases(
        drain_voltage_ha1_V=biases['drain_voltage_ha1_V'],
        drain_current_ha1_mA=biases['drain_current_ha1_mA'],
        gate_voltage_ha1_mV=biases['gate_voltage_ha1_mV'],
        drain_voltage_hb1_V=biases['drain_voltage_hb1_V'],
        drain_current_hb1_mA=biases['drain_current_hb1_mA'],
        gate_voltage_hb1_mV=biases['gate_voltage_hb1_mV'],
        drain_voltage_ha2_V=biases['drain_voltage_ha2_V'],
        drain_current_ha2_mA=biases['drain_current_ha2_mA'],
        gate_voltage_ha2_mV=biases['gate_voltage_ha2_mV'],
        drain_voltage_hb2_V=biases['drain_voltage_hb2_V'],
        drain_current_hb2_mA=biases['drain_current_hb2_mA'],
        gate_voltage_hb2_mV=biases['gate_voltage_hb2_mV'],
        drain_voltage_ha3_V=biases['drain_voltage_ha3_V'],
        drain_current_ha3_mA=biases['drain_current_ha3_mA'],
        gate_voltage_ha3_mV=biases['gate_voltage_ha3_mV'],
        drain_voltage_hb3_V=biases['drain_voltage_hb3_V'],
        drain_current_hb3_mA=biases['drain_current_hb3_mA'],
        gate_voltage_hb3_mV=biases['gate_voltage_hb3_mV'],
    )


class Temperatures(models.Model):
    'Temperatures of the cryochamber'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    t_load_a_1 = models.FloatField(verbose_name='Tload_A1 [K]')
    t_load_a_2 = models.FloatField(verbose_name='Tload_A2 [K]')

    t_load_b_1 = models.FloatField(verbose_name='Tload_B1 [K]')
    t_load_b_2 = models.FloatField(verbose_name='Tload_B2 [K]')

    t_cross_guide_1 = models.FloatField(verbose_name='T_Cross1 [K]')
    t_cross_guide_2 = models.FloatField(verbose_name='T_Cross2 [K]')

    t_polarimeter_1 = models.FloatField(verbose_name='T_Pol1 [K]')
    t_polarimeter_2 = models.FloatField(verbose_name='T_Pol2 [K]')

    def __str__(self):
        return (
            'TloadA = {0:.1f} K, TloadB = {1:.1f} K, Tcross = {2:.1f} K, Tpol = {3:.1f}'
            .format(self.t_load_a_1, self.t_load_b_1, self.t_cross_guide_1, self.t_polarimeter_1)
        )

    def get_absolute_url(self):
        return self.test.get_absolute_url()

    class Meta:
        verbose_name = 'temperatures of the cryochamber'


def dict_to_temperature_set_list(data):
    temperatures = data['temperatures']
    if isinstance(temperatures, dict):
        # We have just one set of outputs, so let's build a list with one element
        temperatures = [temperatures]

    return [Temperatures(
        t_load_a_1=x['t_load_a_1_K'],
        t_load_a_2=x['t_load_a_2_K'],
        t_load_b_1=x['t_load_b_1_K'],
        t_load_b_2=x['t_load_b_2_K'],
        t_polarimeter_1=x['t_polarimeter_1_K'],
        t_polarimeter_2=x['t_polarimeter_2_K'],
        t_cross_guide_1=x['t_cross_guide_1_K'],
        t_cross_guide_2=x['t_cross_guide_2_K'],
    ) for x in temperatures]


class NoiseTemperatureAnalysis(models.Model):
    'Result of a noise temperature analysis'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)
    analysis_results = JSONField(blank=True)
    report_file = models.FileField(
        verbose_name='Report', upload_to='reports/',
        validators=[validate_report_file_ext], blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tnoise_owned', on_delete=models.PROTECT)

    def __str__(self):
        return ('noise temperature analysis for {0}'.format(self.test))

    def get_absolute_url(self):
        return reverse('unittests:tnoise_list')

    class Meta:
        verbose_name = 'noise temperature and gain estimates'


class SpectralAnalysis(models.Model):
    'Results of the analysis of a long-acquisition test'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    analysis_results = JSONField(blank=True)
    report_file = models.FileField(
        verbose_name='Report', upload_to='reports/',
        validators=[validate_report_file_ext], blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='spectral_owned', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('unittests:spectrum_list')

    def __str__(self):
        return self.test.polarimeter_name

    class Meta:
        verbose_name = 'noise analysis for tests done in stable conditions'


class BandpassAnalysis(models.Model):
    'Results of the analysis of a bandpass test'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    analysis_results = JSONField(blank=True)
    report_file = models.FileField(
        verbose_name='Report', upload_to='reports/',
        validators=[validate_report_file_ext], blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='bandpass_owned', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('unittests:bandpass_list')

    def __str__(self):
        return self.test.polarimeter_name

    class Meta:
        verbose_name = 'noise analysis for tests done in stable conditions'
