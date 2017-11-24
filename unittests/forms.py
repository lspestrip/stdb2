# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user
from .models import (
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    Biases,
    Temperatures,
    BandpassAnalysis,
    SpectralAnalysis,
    NoiseTemperatureAnalysis,
)


class TestForm(forms.ModelForm):
    class Meta:
        model = PolarimeterTest
        fields = [
            'data_file',
            'polarimeter_number',
            'band',
            'acquisition_date',
            'cryogenic',
            'phsw_state',
            'test_type',
            'operators',
            'notes',
        ]
        labels = {
            'data_file': 'Data file (either .txt, .zip, .h5 or .hdf5)',
        }

    def save(self, request, commit=True):
        obj = super().save(commit=False)
        if not obj.pk:
            obj.author = get_user(request)

        if commit:
            obj.save()
            self.save_m2m()

        return obj


class AdcOffsetCreate(forms.ModelForm):
    class Meta:
        model = AdcOffset
        exclude = ('test',)


class DetOutputCreate(forms.ModelForm):
    class Meta:
        model = DetectorOutput
        exclude = ('test',)


class BiasesCreate(forms.ModelForm):
    class Meta:
        model = Biases
        exclude = ('test',)


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


class BandpassAnalysisCreate(forms.ModelForm):
    class Meta:
        model = BandpassAnalysis
        # These fields will be filled automatically
        exclude = ('test', 'author')


class SpectralAnalysisCreate(forms.ModelForm):
    class Meta:
        model = SpectralAnalysis
        # These fields will be filled automatically
        exclude = ('test', 'author')


class NoiseTemperatureAnalysisCreate(forms.ModelForm):
    class Meta:
        model = NoiseTemperatureAnalysis
        # These fields will be filled automatically
        exclude = ('test', 'author')
