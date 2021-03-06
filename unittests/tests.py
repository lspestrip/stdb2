from datetime import date, datetime
import os.path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import make_aware
from django.test import TestCase
import h5py
import numpy as np

from .file_conversions import convert_data_file_to_h5

from .models import (
    TestType,
    Operator,
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    Biases,
    Temperatures,
    NoiseTemperatureAnalysis,
    SpectralAnalysis,
    BandpassAnalysis,
)


class FileConvMixin(TestCase):
    @classmethod
    def create_files(cls,
                     base_input_file_name: str,
                     base_output_file_name: str):
        cls.test_file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'testdata'))
        cls.temporary_dir = TemporaryDirectory()

        _, output_name = cls.file_conversion(
            base_input_file_name,
            base_output_file_name
        )

        cls.h5_file = h5py.File(output_name)

    @classmethod
    def clear_stuff(cls):
        cls.h5_file.close()
        cls.temporary_dir.cleanup()

    @classmethod
    def file_conversion(cls, base_input_file_name, base_output_file_name):
        input_file_name = os.path.join(
            cls.test_file_path, base_input_file_name)
        output_file_name = os.path.join(
            cls.temporary_dir.name, base_output_file_name)

        with open(input_file_name, 'rb') as input_file:
            convert_data_file_to_h5(
                input_file_name, input_file, output_file_name)

        return input_file_name, output_file_name

    def _check_dataset_existence(self, components, datasets):
        for component in components:
            self.assertTrue(component in self.h5_file,
                            'group {0} does not exist'.format(component))
            h5_group = self.h5_file[component]
            for dataset in datasets:
                self.assertTrue(dataset in h5_group,
                                '{0} not in {1}'.format(dataset, component))


class TestTextFileConversion(FileConvMixin):
    @classmethod
    def setUpClass(cls):
        super(TestTextFileConversion, cls).setUpClass()
        cls.create_files(
            base_input_file_name='datafile.txt',
            base_output_file_name='datafile_from_txt.h5'
        )

    @classmethod
    def tearDownClass(cls):
        cls.clear_stuff()
        super(TestTextFileConversion, cls).tearDownClass()

    def testGroups(self):
        'Check that the number of groups under / is what we expect'
        self.assertEqual(len(self.h5_file.items()), 1)
        self.assertTrue('time_series' in self.h5_file)

    def testDatasets(self):
        'Check the contents of the dataset'

        data = self.h5_file['time_series']
        first_sample = data[0]
        last_sample = data[-1]
        for key, first_val, last_val in [
            ('time_s', 0.0, 1.4),
            ('pctime', 713.0, 1702.0),
            ('phb', 0.0, 0.0),
            ('record', 0.0, 0.0),
            ('dem_Q1_ADU', -1652.0, -1655.0),
            ('dem_Q2_ADU', 1218.0, 1222.0),
            ('dem_U1_ADU', 105.0, 103.0),
            ('dem_U2_ADU', -308.0, -301.0),
            ('pwr_Q1_ADU', -4909.0, -4887.0),
            ('pwr_Q2_ADU', 15633.0, 15618.0),
            ('pwr_U1_ADU', 32092.0, 32109.0),
            ('pwr_U2_ADU', -11823.0, -11773.0),
            ('rfpower_dB', -40.0, -40.0),
            ('freq_Hz', -1.0, -1.0),
        ]:
            self.assertAlmostEqual(first_sample[key], first_val,
                                   msg=('{0} != {1} (column {2}, first sample)'
                                        .format(first_sample[key], last_val, key)))
            self.assertAlmostEqual(last_sample[key], last_val,
                                   msg=('{0} != {1} (column {2}, last sample)'
                                        .format(last_sample[key], last_val, key)))


class TestNewExcelFileConversion(FileConvMixin):
    @classmethod
    def setUpClass(cls):
        super(TestNewExcelFileConversion, cls).setUpClass()
        cls.create_files(
            base_input_file_name='datafile.zip',
            base_output_file_name='datafile_from_zip.h5'
        )

    @classmethod
    def tearDownClass(cls):
        cls.clear_stuff()
        super(TestNewExcelFileConversion, cls).tearDownClass()

    def testGroups(self):
        'Check that the number of groups under / is what we expect'
        self.assertEqual(len(self.h5_file.items()), 14)

    def testPresenceOfDatasets(self):
        'Check that all the datasets are in place'

        self._check_dataset_existence(('HA1', 'HA2', 'HA3',
                                       'HB1', 'HB2', 'HB3'),
                                      ('IDVD', 'IDVG'))

        self._check_dataset_existence(('PSA1', 'PSA2', 'PSB1', 'PSB2'),
                                      ('IFVF', 'IRVR'))

        self._check_dataset_existence(('Q1', 'U1', 'Q2', 'U2'),
                                      ('IFVF',))

    def testDatasets(self):
        'Check the contents of a few of the datasets in the file'

        data = self.h5_file['HA1/IDVD']

        self.assertAlmostEqual(data['DrainI', 0, 0], -2.143613e-7)
        self.assertAlmostEqual(data['DrainI', 1, 0], -7.83601E-8)
        self.assertAlmostEqual(data['DrainI', -1, 0], 5.442244e-4)

        self.assertAlmostEqual(data['DrainI', 0, -1], -4.97475048177876E-6)
        self.assertAlmostEqual(data['DrainI', 1, -1], 0.00025984802050516)
        self.assertAlmostEqual(data['DrainI', -1, -1], 0.00649147015064955)

        self.assertAlmostEqual(data['DrainV', 0, 0], 0.0)
        self.assertAlmostEqual(data['DrainV', 1, 0], 0.02)
        self.assertAlmostEqual(data['DrainV', -1, 0], 0.94)


def populate_database():
    SiteUser = get_user_model()
    user = SiteUser.objects.create_user(
        'johndoe', 'johndoe@myself.com', 'iseedeadpeople')

    test_type_1 = TestType(description='1/f')
    test_type_1.save()

    datafile_path = os.path.join(os.path.dirname(__file__),
                                 '..', 'testdata', 'datafile.txt')
    with open(datafile_path, 'rb') as data_file:
        test = PolarimeterTest(
            polarimeter_number=1,
            cryogenic=True,
            acquisition_date=date(year=2017, month=10, day=1),
            notes='',
            data_file=SimpleUploadedFile('datafile.txt', data_file.read()),
            test_type=test_type_1,
            author=user
        )
        test.save()

    operator_1 = Operator(name='Abraham Lincoln')
    operator_1.save()

    operator_2 = Operator(name='George Washington')
    operator_2.save()

    test.operators.add(operator_1)
    test.operators.add(operator_2)

    test.save()

    adc_ofs = AdcOffset(
        test=test,
        q1_adu=1.0,
        u1_adu=2.0,
        u2_adu=3.0,
        q2_adu=4.0
    )
    adc_ofs.save()

    det_output = DetectorOutput(
        test=test,
        q1_adu=10.0,
        u1_adu=20.0,
        u2_adu=30.0,
        q2_adu=40.0
    )
    det_output.save()

    biases = Biases(
        test=test,
        drain_voltage_ha1_V=1.01,
        drain_current_ha1_mA=1.02,
        gate_voltage_ha1_mV=1.03,
        drain_voltage_hb1_V=1.1,
        drain_current_hb1_mA=1.2,
        gate_voltage_hb1_mV=1.3,
        drain_voltage_ha2_V=2.01,
        drain_current_ha2_mA=2.02,
        gate_voltage_ha2_mV=2.03,
        drain_voltage_hb2_V=2.1,
        drain_current_hb2_mA=2.2,
        gate_voltage_hb2_mV=2.3,
        drain_voltage_ha3_V=3.01,
        drain_current_ha3_mA=3.02,
        gate_voltage_ha3_mV=3.03,
        drain_voltage_hb3_V=3.1,
        drain_current_hb3_mA=3.2,
        gate_voltage_hb3_mV=3.3,
    )
    biases.save()

    temp = Temperatures(
        test=test,
        t_load_a_1=10.0,
        t_load_a_2=20.0,
        t_load_b_1=30.0,
        t_load_b_2=40.0,
        t_cross_guide_1=50.0,
        t_cross_guide_2=60.0,
        t_polarimeter_1=70.0,
        t_polarimeter_2=80.0,
    )
    temp.save()

    tnoise = NoiseTemperatureAnalysis(
        test=test,
        analysis_results=None,
        author=user
    )
    tnoise.save()

    spectrum = SpectralAnalysis(
        test=test,
        analysis_results=None,
        author=user
    )
    spectrum.save()

    bandpass = BandpassAnalysis(
        test=test,
        analysis_results=None,
        author=user
    )
    bandpass.save()


class TestBasicFunctionality(TestCase):
    def test_if_you_can_create_objects(self):
        'Check that all the basic objects can be created seamlessy'
        populate_database()


class TestDatabaseAccess(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestDatabaseAccess, cls).setUpClass()
        populate_database()

    def testPolTestProperties(self):
        test_obj = PolarimeterTest.objects.filter(polarimeter_number=1)
        self.assertTrue(test_obj)
        self.assertTrue(len(test_obj.all()) == 1)
        self.assertTrue(len(test_obj[0].operators.all()) == 2)
        self.assertEqual(test_obj[0].polarimeter_name, 'STRIP01')

    def testUrls(self):
        test_obj = PolarimeterTest.objects.filter(polarimeter_number=1)[0]

        self.assertNotEqual(test_obj.get_absolute_url(), '')
        self.assertNotEqual(test_obj.get_download_url(), '')
        self.assertNotEqual(test_obj.get_delete_url(), '')
        self.assertNotEqual(test_obj.get_json_url(), '')

        response = self.client.get(test_obj.get_absolute_url())
        self.assertTemplateUsed(
            response, 'unittests/polarimetertest_details.html')

    def testPolarimeterTestForms(self):
        response = self.client.get('/unittests/')
        self.assertTemplateUsed(
            response, 'unittests/polarimetertest_list.html')
