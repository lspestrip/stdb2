from datetime import date, datetime
import os.path
from tempfile import TemporaryDirectory

from django.test import TestCase
import h5py

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
    StabilityAnalysis,
)


class TestFileConversion(TestCase):
    def setUp(self):
        self.test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testdata'))
        self.temporary_dir = TemporaryDirectory()

    def tearDown(self):
        self.temporary_dir.cleanup()

    def _file_conversion(self, base_input_file_name, base_output_file_name):
        input_file_name = os.path.join(self.test_file_path, base_input_file_name)
        output_file_name = os.path.join(self.temporary_dir.name, base_output_file_name)

        with open(input_file_name, 'rb') as input_file:
            convert_data_file_to_h5(input_file_name, input_file, output_file_name)

        return input_file_name, output_file_name
        

    def test_text_conversion(self):
        'Determine if the code converts a text file into HDF5 correctly'

        input_name, output_name = self._file_conversion(
            base_input_file_name='datafile.txt',
            base_output_file_name='datafile_from_txt.h5'
        )
        
        with h5py.File(output_name) as h5_file:
            self.assertEqual(len(h5_file.items()), 1)
            self.assertTrue('time_series' in h5_file)

    def test_excel_conversion(self):
        '''Determine if the code converts a bunch of Excel files zipped together
        into one HDF5 file correctly'''
        
        input_name, output_name = self._file_conversion(
            base_input_file_name='datafile.zip',
            base_output_file_name='datafile_from_zip.h5'
        )

        with h5py.File(output_name) as h5_file:
            self.assertEqual(len(h5_file.items()), 14)
            for group in (
                'HA1', 'HB1',
                'HA2', 'HB2',
                'HA3', 'HB3',
                'PSA1', 'PSB1',
                'PSA2', 'PSB2',
                'Q1', 'U1',
                'Q2', 'U2',
            ):
                self.assertTrue(group in h5_file)

class TestBasicFunctionality(TestCase):
    def test_if_you_can_create_objects(self):
        'Check that all the basic objects can be created seamlessy'

        test_type_1 = TestType(description='1/f')
        test_type_1.save()

        test = PolarimeterTest(
            polarimeter_number=1,
            cryogenic=True,
            acquisition_date=date(year=2017, month=10, day=1),
            notes='',
            data_file=None,
            test_type=test_type_1
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
            pwr0_adu=1.0,
            pwr1_adu=2.0,
            pwr2_adu=3.0,
            pwr3_adu=4.0
        )
        adc_ofs.save()

        det_output = DetectorOutput(
            test=test,
            pwr0_adu=10.0,
            pwr1_adu=20.0,
            pwr2_adu=20.0,
            pwr3_adu=30.0
        )
        det_output.save()

        biases = Biases(
            test=test,
            h0_vdrain=1.0,
            h0_idrain=2.0,
            h0_vgate=3.0,
            h1_vdrain=4.0,
            h1_idrain=5.0,
            h1_vgate=6.0,
            h2_vdrain=7.0,
            h2_idrain=8.0,
            h2_vgate=9.0,
            h3_vdrain=10.0,
            h3_idrain=11.0,
            h3_vgate=12.0,
            h4_vdrain=13.0,
            h4_idrain=14.0,
            h4_vgate=15.0,
            h5_vdrain=16.0,
            h5_idrain=17.0,
            h5_vgate=18.0,
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
            polarimeter_gain=1.0,
            polarimeter_gain_err=2.0,
            gain_product=1000.0,
            gain_product_err=1000.0,
            noise_temperature=30.0,
            noise_temperature_err=10.0,
            estimation_method='nonlinear',
            code_version='0.1',
            code_commit='0123456789abcdef',
            analysis_date=datetime(year=2017, month=10, day=1, hour=1, minute=2, second=3),
        )
        tnoise.save()

        stability = StabilityAnalysis(
            test=test,
            oof_alpha=1.0,
            oof_knee_frequency_hz=0.010,
            wn_level_adu2_rhz=0.3,
            sampling_frequency_hz=25.0,
            code_version='0.2',
            code_commit='fedcba9876543210',
            analysis_date=datetime(year=2016, month=9, day=2, hour=2, minute=4, second=5),
        )
        stability.save()


