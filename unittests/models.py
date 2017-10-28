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

from django.db import models


class TestType(models.Model):
    'Kind of test (e.g., Y-factor)'
    description = models.CharField(max_length=80)

    def __str__(self):
        return self.description


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
    ('0000', '0000'),
    ('0101', '0101'),
    ('1010', '1010'),
    ('switching', 'switching'),
)


class PolarimeterTest(models.Model):
    'A dedicated test done on one polarimeter'

    polarimeter_number = models.IntegerField(
        verbose_name='Number of the polarimeter')
    cryogenic = models.BooleanField(verbose_name='Cryogenic test')
    acquisition_date = models.DateField(verbose_name='Date of acquisition')
    data_file = models.FileField(max_length=1024, upload_to='test_data/')
    notes = models.TextField(verbose_name='Notes', blank=True)
    phsw_state = models.CharField(
        max_length=12, default='0000', choices=PHSW_STATES)
    band = models.CharField(max_length=1, choices=BAND_CHOICES)

    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    operators = models.ManyToManyField(Operator)

    def __str__(self):
        return 'STRIP{0}, {1}'.format(
            self.polarimeter_number,
            self.acquisition_date.strftime('%Y-%M-%D')
        )

    def polarimeter_name(self):
        return 'STRIP{0:02d}'.format(self.polarimeter_number)


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


class Biases(models.Model):
    'Biases used in the six HEMTs of a polarimeter'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    h0_vdrain = models.FloatField(verbose_name='H0 Vdrain [V]')
    h0_idrain = models.FloatField(verbose_name='H0 Idrain [mA]')
    h0_vgate = models.FloatField(verbose_name='H0 Vgate [mV]')

    h1_vdrain = models.FloatField(verbose_name='H1 Vdrain [V]')
    h1_idrain = models.FloatField(verbose_name='H1 Idrain [mA]')
    h1_vgate = models.FloatField(verbose_name='H1 Vgate [mV]')

    h2_vdrain = models.FloatField(verbose_name='H2 Vdrain [V]')
    h2_idrain = models.FloatField(verbose_name='H2 Idrain [mA]')
    h2_vgate = models.FloatField(verbose_name='H2 Vgate [mV]')

    h3_vdrain = models.FloatField(verbose_name='H3 Vdrain [V]')
    h3_idrain = models.FloatField(verbose_name='H3 Idrain [mA]')
    h3_vgate = models.FloatField(verbose_name='H3 Vgate [mV]')

    h4_vdrain = models.FloatField(verbose_name='H4 Vdrain [V]')
    h4_idrain = models.FloatField(verbose_name='H4 Idrain [mA]')
    h4_vgate = models.FloatField(verbose_name='H4 Vgate [mV]')

    h5_vdrain = models.FloatField(verbose_name='H5 Vdrain [V]')
    h5_idrain = models.FloatField(verbose_name='H5 Idrain [mA]')
    h5_vgate = models.FloatField(verbose_name='H5 Vgate [mV]')


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

    def __str__(self):
        return ('Tnoise={0} for {1} ({2})'
                .format(self.noise_temperature,
                        self.test.polarimeter_name()))


class StabilityAnalysis(models.Model):
    'Results of the analysis of a long-acquisition test'

    test = models.ForeignKey(to=PolarimeterTest, on_delete=models.CASCADE)

    oof_alpha = models.FloatField(verbose_name='1/f noise slope')
    oof_knee_frequency = models.FloatField(
        verbose_name='1/f knee frequency [Hz]')
    wn_level = models.FloatField(verbose_name='white noise level [ADU^2]')
    sampling_frequency = models.FloatField(
        verbose_name='sampling frequency [Hz]', default=25.0)

    code_version = models.CharField(max_length=12,
                                    verbose_name='version number of the analysis code')
    code_commit = models.CharField(max_length=40,
                                   verbose_name='last commit hash of the analysis code')
    analysis_date = models.DateTimeField('date when the analysis was done')

    def __str__(self):
        return self.test.polarimeter_name()
