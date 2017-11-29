# -*- encoding: utf-8 -*-

'''Views of the "unittest" application
'''

import os.path

import simplejson as json

from django.contrib.auth import get_user
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
)

from .models import (
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    Biases,
    Temperatures,
    dict_to_adc_offset_list,
    dict_to_detector_output_list,
    dict_to_biases,
    dict_to_temperature_set_list,
    dict_to_tnoise_analysis,
    NoiseTemperatureAnalysis,
    BandpassAnalysis,
    SpectralAnalysis,
)

from .forms import (
    TestForm,
    AdcOffsetCreate,
    DetOutputCreate,
    BiasesCreate,
    TemperatureCreate,
    CreateFromJSON,
    BandpassAnalysisCreate,
    SpectralAnalysisCreate,
    NoiseTemperatureAnalysisCreate,
)


class TestListView(View):
    template = 'unittests/polarimetertest_list.html'

    def get(self, request):
        'Produce a list of the tests in the database'

        context = {
            'tests': PolarimeterTest.objects.all()
        }
        return render(request, self.template, context)


class FormValidMixin:
    def form_valid(self, form):
        self.object = form.save(self.request)
        return HttpResponseRedirect(self.get_success_url())


class TestCreate(FormValidMixin, CreateView):
    form_class = TestForm
    model = PolarimeterTest
    template_name = 'unittests/polarimetertest_create.html'

    def get_form(self, form_class=None):
        form = super(TestCreate, self).get_form(form_class)
        form.fields['acquisition_date'].widget.attrs.update(
            {'class': 'datepicker'})
        form.fields['acquisition_date'].widget.format = '%Y-%m-%d'
        form.fields['acquisition_date'].input_formats = ['%Y-%m-%d']
        return form

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TestDetails(View):
    template_name = 'unittests/polarimetertest_details.html'

    def get(self, request, test_id):
        'Show details about a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        return render(request, self.template_name, {
            'test': cur_test,
            'adc_offsets': AdcOffset.objects.filter(test=cur_test),
            'det_outputs': DetectorOutput.objects.filter(test=cur_test),
            'biases': Biases.objects.filter(test=cur_test).last(),
            'temperatures': Temperatures.objects.filter(test=cur_test),
            'tnoise_analyses': NoiseTemperatureAnalysis.objects.filter(test=cur_test),
            'bandpass_analyses': BandpassAnalysis.objects.filter(test=cur_test),
            'spectrum_analyses': SpectralAnalysis.objects.filter(test=cur_test),
            'operators': cur_test.operators.all(),
        })


class TestDetailsJson(View):
    def get(self, request, test_id):
        'Return a JSON object containing the details of the test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        adc_offsets = []
        for ofs in AdcOffset.objects.filter(test=cur_test):
            adc_offsets.append({
                'q1_adu': ofs.q1_adu,
                'u1_adu': ofs.u1_adu,
                'u2_adu': ofs.u2_adu,
                'q2_adu': ofs.q2_adu,
            })

        det_outputs = []
        for out in DetectorOutput.objects.filter(test=cur_test):
            det_outputs.append({
                'q1_adu': out.q1_adu,
                'u1_adu': out.u1_adu,
                'u2_adu': out.u2_adu,
                'q2_adu': out.q2_adu,
            })

        hemt_biases = {}
        for biases in Biases.objects.filter(test=cur_test):
            hemt_biases['drain_voltage_ha1_V'] = biases.drain_voltage_ha1_V
            hemt_biases['drain_current_ha1_mA'] = biases.drain_current_ha1_mA
            hemt_biases['gate_voltage_ha1_mV'] = biases.gate_voltage_ha1_mV
            hemt_biases['drain_voltage_hb1_V'] = biases.drain_voltage_hb1_V
            hemt_biases['drain_current_hb1_mA'] = biases.drain_current_hb1_mA
            hemt_biases['gate_voltage_hb1_mV'] = biases.gate_voltage_hb1_mV
            hemt_biases['drain_voltage_ha2_V'] = biases.drain_voltage_ha2_V
            hemt_biases['drain_current_ha2_mA'] = biases.drain_current_ha2_mA
            hemt_biases['gate_voltage_ha2_mV'] = biases.gate_voltage_ha2_mV
            hemt_biases['drain_voltage_hb2_V'] = biases.drain_voltage_hb2_V
            hemt_biases['drain_current_hb2_mA'] = biases.drain_current_hb2_mA
            hemt_biases['gate_voltage_hb2_mV'] = biases.gate_voltage_hb2_mV
            hemt_biases['drain_voltage_ha3_V'] = biases.drain_voltage_ha3_V
            hemt_biases['drain_current_ha3_mA'] = biases.drain_current_ha3_mA
            hemt_biases['gate_voltage_ha3_mV'] = biases.gate_voltage_ha3_mV
            hemt_biases['drain_voltage_hb3_V'] = biases.drain_voltage_hb3_V
            hemt_biases['drain_current_hb3_mA'] = biases.drain_current_hb3_mA
            hemt_biases['gate_voltage_hb3_mV'] = biases.gate_voltage_hb3_mV

        temperatures = []
        for temp in Temperatures.objects.filter(test=cur_test):
            temperatures.append({
                't_load_a_1_K': temp.t_load_a_1,
                't_load_a_2_K': temp.t_load_a_2,
                't_load_b_1_K': temp.t_load_b_1,
                't_load_b_2_K': temp.t_load_b_2,
                't_cross_guide_1_K': temp.t_cross_guide_1,
                't_cross_guide_2_K': temp.t_cross_guide_2,
                't_polarimeter_1_K': temp.t_polarimeter_1,
                't_polarimeter_2_K': temp.t_polarimeter_2,
            })

        tnoise_analyses = []
        for analysis in NoiseTemperatureAnalysis.objects.filter(test=cur_test):
            tnoise_analyses.append({
                'average_gain_K_over_ADU': analysis.average_gain,
                'average_gain_err': analysis.average_gain_err,

                'cross_gain_K_over_ADU': analysis.cross_gain,
                'cross_gain_err': analysis.cross_gain_err,

                'noise_temperature_K': analysis.noise_temperature,
                'noise_temperature_err': analysis.noise_temperature_err,
            })

        result = {
            'url': cur_test.get_absolute_url(),
            'download_url': cur_test.get_download_url(),
            'polarimeter_number': cur_test.polarimeter_number,
            'cryogenic': cur_test.cryogenic,
            'acquisition_date': cur_test.acquisition_date.strftime('%Y-%m-%d'),
            'phsw_state': cur_test.phsw_state,
            'band': cur_test.band,
            'test_type': str(cur_test.test_type),
            'adc_offsets': adc_offsets,
            'detector_outputs': det_outputs,
            'hemt_biases': hemt_biases,
            'temperatures': temperatures,
            'operators': [x.name for x in cur_test.operators.all()],
        }
        return HttpResponse(json.dumps(result, indent=4), content_type='application/json')


class TestDeleteView(DeleteView):
    model = PolarimeterTest
    success_url = reverse_lazy('unittests:test_list')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TestDeleteView, self).dispatch(request, *args, **kwargs)


class TestDownload(View):
    def get(self, request, test_id):
        'Allow the user to download the data file for a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        data_file = cur_test.data_file
        data_file.open()
        data = data_file.read()
        resp = HttpResponse(data, content_type='application/hdf5')
        resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            os.path.basename(data_file.name))
        return resp


class TestPwrPlot(View):
    def get(self, request, test_id):
        'Send a plot of the data'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        image_file = cur_test.pwr_plot
        image_file.open()
        data = image_file.read()
        resp = HttpResponse(data, content_type='image/png')
        resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            os.path.basename(image_file.name))
        return resp


class AddMixin(View):
    form_class = None
    template_name = ''

    def save_form_without_commit(self, form, request):
        return form.save(commit=False)

    def post(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            new_obj = self.save_form_without_commit(form, request)
            new_obj.test = cur_test
            new_obj.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = self.form_class()

        return render(request, self.template_name, {
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddMixin, self).dispatch(request, *args, **kwargs)


class AddMixinWithRequest(AddMixin):
    def get_form(self, form_class=None):
        form = super(TestCreate, self).get_form(form_class)
        form.fields['analysis_date'].widget.attrs.update(
            {'class': 'datepicker'})
        form.fields['analysis_date'].widget.format = '%Y-%m-%d'
        form.fields['analysis_date'].input_formats = ['%Y-%m-%d']
        return form

    def save_form_without_commit(self, form, request):
        return form.save(request, commit=False)


class DeleteMixin(View):
    model = None

    def get(self, request, test_id, obj_id):
        cur_ofs = get_object_or_404(self.model, pk=obj_id)
        cur_ofs.delete()

        cur_obj = get_object_or_404(PolarimeterTest, pk=test_id)
        return redirect(cur_obj)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteMixin, self).dispatch(request, *args, **kwargs)


class AdcOffsetAddView(AddMixin):
    form_class = AdcOffsetCreate
    template_name = 'unittests/test_hk_entry_create.html'


class AdcOffsetDeleteView(DeleteMixin):
    model = AdcOffset


class AdcOffsetJsonView(View):
    def post(self, request, test_id):
        'Import the level of the ADC offsets for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_offsets = dict_to_adc_offset_list(data)
            for ofs in new_offsets:
                ofs.test = cur_test
                ofs.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "adc_offsets": [{
                        "q1_adu": 1.0,
                        "u1_adu": 2.0,
                        "u2_adu": 3.0,
                        "q2_adu": 4.0
                    }],
                }, indent=4)
        })

        return render(request, 'unittests/test_hk_entry_create.html', {
            'page_title': 'Import ADC offsets',
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class DetOutputAddView(AddMixin):
    form_class = DetOutputCreate
    template_name = 'unittests/test_hk_entry_create.html'


class DetOutputDeleteView(DeleteMixin):
    model = DetectorOutput


class DetOutputJsonView(View):
    def post(self, request, test_id):
        'Import the level of the detector outputs for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_output_list = dict_to_detector_output_list(data)
            for new_output in new_output_list:
                new_output.test = cur_test
                new_output.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "detector_offsets": [{
                        "q1_adu": 1.0,
                        "u1_adu": 2.0,
                        "u2_adu": 3.0,
                        "q2_adu": 4.0
                    }]
                }, indent=4)
        })

        return render(request, 'unittests/test_hk_entry_create.html', {
            'page_title': 'Import detector outputs',
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class BiasesAddView(AddMixin):
    form_class = BiasesCreate
    template_name = 'unittests/test_hk_entry_create.html'


class BiasesDeleteView(DeleteMixin):
    model = Biases


class BiasesJsonView(View):
    def post(self, request, test_id):
        'Import the HEMT biases for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_biases = dict_to_biases(data)
            new_biases.test = cur_test
            new_biases.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "hemt_biases": {
                        "drain_voltage_ha1_V": 1.0,
                        "drain_current_ha1_mA": 2.0,
                        "gate_voltage_ha1_mV": 3.0,
                        "drain_voltage_hb1_V": 4.0,
                        "drain_current_hb1_mA": 5.0,
                        "gate_voltage_hb1_mV": 6.0,
                        "drain_voltage_ha2_V": 7.0,
                        "drain_current_ha2_mA": 8.0,
                        "gate_voltage_ha2_mV": 9.0,
                        "drain_voltage_hb2_V": 10.0,
                        "drain_current_hb2_mA": 11.0,
                        "gate_voltage_hb2_mV": 12.0,
                        "drain_voltage_ha3_V": 13.0,
                        "drain_current_ha3_mA": 14.0,
                        "gate_voltage_ha3_mV": 15.0,
                        "drain_voltage_hb3_V": 16.0,
                        "drain_current_hb3_mA": 17.0,
                        "gate_voltage_hb3_mV": 18.0
                    },
                }, indent=4)
        })

        return render(request, 'unittests/test_hk_entry_create.html', {
            'page_title': 'Import HEMT biases',
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class TemperatureAddView(AddMixin):
    form_class = TemperatureCreate
    template_name = 'unittests/temperature_create.html'


class TemperatureDeleteView(DeleteMixin):
    model = Temperatures


class TemperatureJsonView(View):
    def post(self, request, test_id):
        'Import the set of temperatures for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            temperature_set_list = dict_to_temperature_set_list(data)
            for temperature_set in temperature_set_list:
                temperature_set.test = cur_test
                temperature_set.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "temperatures": [{
                        "t_load_a_1_K": 1.0,
                        "t_load_a_2_K": 2.0,
                        "t_load_b_1_K": 3.0,
                        "t_load_b_2_K": 4.0,
                        "t_polarimeter_1_K": 5.0,
                        "t_polarimeter_2_K": 6.0,
                        "t_cross_guide_1_K": 7.0,
                        "t_cross_guide_2_K": 8.0,
                    }]
                }, indent=4)
        })

        return render(request, 'unittests/test_hk_entry_create.html', {
            'page_title': 'Import detector outputs',
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class TnoiseListView(View):
    template = 'unittests/tnoise_list.html'

    def get(self, request):
        'Show a list of the results of Tnoise tests'

        context = {
            'tnoise_tests': NoiseTemperatureAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class TnoiseAddView(AddMixinWithRequest):
    form_class = NoiseTemperatureAnalysisCreate
    template_name = 'unittests/tnoise_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TnoiseAddFromJsonView(View):
    'Import a JSON file containing the estimates of Tnoise for a polarimeter'

    def post(self, request, test_id):
        'Import the level of the detector outputs for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_analysis = dict_to_tnoise_analysis(data)
            new_analysis.test = cur_test
            new_analysis.author = get_user(request)
            new_analysis.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "average_gain": {
                        "mean": 1.0,
                        "std": 2.0,
                    },
                    "gain_prod": {
                        "mean": 3.0,
                        "std": 4.0,
                    },
                    "tnoise": {
                        "mean": 5.0,
                        "std": 6.0,
                    },
                    "estimation_method": "nonlinear fit",
                    "striptun_version": "1.0",
                    "latest_git_commit": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "date": "2017-01-01"
                }, indent=4)
        })

        return render(request, 'unittests/tnoise_create.html', {
            'test_id': test_id,
            'form': form,
        })


class TnoiseDeleteView(DeleteMixin):
    model = NoiseTemperatureAnalysis


class SpectralAnalysisListView(View):
    template = 'unittests/spectral_analysis_list.html'

    def get(self, request):
        'Show a list of the results of a spectral analysis'

        context = {
            'spectral_analysis_tests': SpectralAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class SpectralAnalysisAddView(AddMixinWithRequest):
    form_class = SpectralAnalysisCreate
    template_name = 'unittests/spectral_analysis_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SpectralAnalysisDeleteView(DeleteMixin):
    model = SpectralAnalysis


class BandpassAnalysisListView(View):
    template = 'unittests/bandpass_analysis_list.html'

    def get(self, request):
        'Show a list of the results of a bandpass analysis'

        context = {
            'bandpass_analysis_tests': BandpassAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class BandpassAnalysisAddView(AddMixinWithRequest):
    form_class = BandpassAnalysisCreate
    template_name = 'unittests/bandpass_analysis_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BandpassAnalysisDeleteView(DeleteMixin):
    model = BandpassAnalysis
