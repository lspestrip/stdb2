# -*- encoding: utf-8 -*-

from django import forms
from .models import PolarimeterTest, AdcOffset, DetectorOutput


class AddTestForm(forms.ModelForm):
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


class AddAdcOffset(forms.ModelForm):
    class Meta:
        model = AdcOffset
        fields = [
            'pwr0_adu',
            'pwr1_adu',
            'pwr2_adu',
            'pwr3_adu',
        ]


class AddDetectorOutputs(forms.ModelForm):
    class Meta:
        model = DetectorOutput
        fields = [
            'pwr0_adu',
            'pwr1_adu',
            'pwr2_adu',
            'pwr3_adu',
        ]


class CreateFromJSON(forms.Form):
    json_text = forms.CharField(
        label='JSON record', widget=forms.Textarea, max_length=4096)
