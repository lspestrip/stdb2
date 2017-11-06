# -*- encoding: utf-8 -*-

from django import forms
from .models import (
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    Temperatures
)


class TestForm(forms.ModelForm):
    class Meta:
        model = PolarimeterTest
        fields = [
            'polarimeter_number',
            'band',
            'acquisition_date',
            'cryogenic',
            'phsw_state',
            'test_type',
            'data_file',
            'operators',
            'notes',
        ]


class AdcOffsetCreate(forms.ModelForm):
    class Meta:
        model = AdcOffset
        fields = [
            'pwr0_adu',
            'pwr1_adu',
            'pwr2_adu',
            'pwr3_adu',
        ]


class DetOutputCreate(forms.ModelForm):
    class Meta:
        model = DetectorOutput
        fields = [
            'pwr0_adu',
            'pwr1_adu',
            'pwr2_adu',
            'pwr3_adu',
        ]


class TemperatureCreate(forms.ModelForm):
    class Meta:
        model = Temperatures
        fields = [
            't_load_a_1',
            't_load_a_2',
            't_load_b_1',
            't_load_b_2',
            't_polarimeter_1',
            't_polarimeter_2',
            't_cross_guide_1',
            't_cross_guide_2',
        ]


class CreateFromJSON(forms.Form):
    json_text = forms.CharField(
        label='JSON record', widget=forms.Textarea, max_length=4096)
