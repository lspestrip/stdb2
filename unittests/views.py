# -*- encoding: utf-8 -*-

'''Views of the "unittest" application
'''

import os.path

import simplejson as json

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
    dict_to_tnoise_analysis,
    dict_to_detector_output,
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
                'pwr0_adu': ofs.pwr0_adu,
                'pwr1_adu': ofs.pwr1_adu,
                'pwr2_adu': ofs.pwr2_adu,
                'pwr3_adu': ofs.pwr3_adu,
            })

        det_outputs = []
        for out in DetectorOutput.objects.filter(test=cur_test):
            det_outputs.append({
                'pwr0_adu': out.pwr0_adu,
                'pwr1_adu': out.pwr1_adu,
                'pwr2_adu': out.pwr2_adu,
                'pwr3_adu': out.pwr3_adu,
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
                't_load_a_1': temp.t_load_a_1,
                't_load_a_2': temp.t_load_a_2,
                't_load_b_1': temp.t_load_b_1,
                't_load_b_2': temp.t_load_b_2,
                't_cross_guide_1': temp.t_cross_guide_1,
                't_cross_guide_2': temp.t_cross_guide_2,
                't_polarimeter_1': temp.t_polarimeter_1,
                't_polarimeter_2': temp.t_polarimeter_2,
            })

        tnoise_analyses = []
        for analysis in NoiseTemperatureAnalysis.objects.filter(test=cur_test):
            tnoise_analyses.append({
                'polarimeter_gain': analysis.polarimeter_gain,
                'polarimeter_gain_err': analysis.polarimeter_gain_err,

                'gain_product': analysis.gain_product,
                'gain_product_err': analysis.gain_product_err,

                'noise_temperature': analysis.noise_temperature,
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


class AddMixin(View):
    form_class = None
    template_name = ''

    def post(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            new_offsets = form.save(commit=False)
            new_offsets.test = cur_test
            new_offsets.save()

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
    template_name = 'unittests/adc_create.html'


class AdcOffsetDeleteView(DeleteMixin):
    model = AdcOffset


class DetOutputAddView(AddMixin):
    form_class = DetOutputCreate
    template_name = 'unittests/detoutput_create.html'


class DetOutputDeleteView(DeleteMixin):
    model = DetectorOutput


class DetOutputJsonView(View):
    def post(self, request, test_id):
        'Import the level of the detector outputs for a test from a JSON record'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_output = dict_to_detector_output(data)
            new_output.test = cur_test
            new_output.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = CreateFromJSON(initial={
            'json_text': json.dumps(
                {
                    "detector_offsets": {
                        "PWR0_adu": 1.0,
                        "PWR1_adu": 2.0,
                        "PWR2_adu": 3.0,
                        "PWR3_adu": 4.0
                    }
                }, indent=4)
        })

        return render(request, 'unittests/detoutput_create.html', {
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class BiasesAddView(AddMixin):
    form_class = BiasesCreate
    template_name = 'unittests/adc_create.html'


class BiasesDeleteView(DeleteMixin):
    model = Biases


class TemperatureAddView(AddMixin):
    form_class = TemperatureCreate
    template_name = 'unittests/temperature_create.html'


class TemperatureDeleteView(DeleteMixin):
    model = Temperatures


class TnoiseListView(View):
    template_name = 'unittests/tnoise_list.html'

    def get(self, request):
        'Show a list of the results of Tnoise tests'

        context = {
            'tnoise_tests': NoiseTemperatureAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class TnoiseAddView(AddMixin):
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
            'spectral_analysis_tests': NoiseTemperatureAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class SpectralAnalysisAddView(AddMixin):
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
            'bandpass_analysis_tests': NoiseTemperatureAnalysis.objects.all(),
        }
        return render(request, self.template, context)


class BandpassAnalysisAddView(AddMixin):
    form_class = BandpassAnalysisCreate
    template_name = 'unittests/bandpass_analysis_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BandpassAnalysisDeleteView(DeleteMixin):
    model = BandpassAnalysis
