# -*- encoding: utf-8 -*-

'''Views of the "unittest" application
'''

from collections import OrderedDict
from datetime import timedelta
import mimetypes
import os.path

import simplejson as json

from django.contrib.auth import get_user
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,
    UpdateView,
)

from rest_framework.views import APIView
from rest_framework.response import Response as RESTResponse

from .models import (
    get_polarimeter_name,
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

        # Get a list of the polarimeters which have at least one test
        pol_nums = [x[0] for x in PolarimeterTest.objects.order_by()
                    .values_list('polarimeter_number').distinct()]
        if pol_nums:
            tests = OrderedDict()
            pol_nums.sort()
            for cur_pol_num in pol_nums:
                pol_name = get_polarimeter_name(cur_pol_num)
                tests[pol_name] = \
                    PolarimeterTest.objects.filter(
                        polarimeter_number=cur_pol_num)

            context = {
                'polarimeter_tests': tests,
            }
        else:
            context = {}

        return render(request, self.template, context)


@method_decorator(login_required, name='dispatch')
class TestCreate(CreateView):
    'Create a new PolarimeterTest object'

    form_class = TestForm
    model = PolarimeterTest
    template_name = 'unittests/polarimetertest_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super(TestCreate, self).get_form(form_class)
        form.fields['acquisition_date'].widget.attrs.update(
            {'class': 'datepicker'})
        form.fields['acquisition_date'].widget.format = '%Y-%m-%d'
        form.fields['acquisition_date'].input_formats = ['%Y-%m-%d']
        return form


@method_decorator(login_required, name='dispatch')
class TestUpdate(UpdateView):
    'Update an existing PolarimeterTest object'
    form_class = TestForm
    model = PolarimeterTest
    template_name = 'unittests/polarimetertest_create.html'


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


@method_decorator(login_required, name='dispatch')
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


class PolarimeterDetails(TemplateView):
    template_name = 'unittests/polarimeter_details.html'

    def get_context_data(self, **kwargs):
        'Details about a polarimeter'

        context = super().get_context_data(**kwargs)
        polarimeter_name = context['pol_name']
        polarimeter_number = int(polarimeter_name[5:7])
        context['polarimeter_name'] = polarimeter_name
        context['polarimeter_number'] = polarimeter_number

        context['tests'] = \
            PolarimeterTest.objects.filter(
                polarimeter_number=polarimeter_number).all()

        context['bandpasses'] = \
            BandpassAnalysis.objects.filter(
                test__polarimeter_number=polarimeter_number).all()

        context['noise_temperatures'] = \
            NoiseTemperatureAnalysis.objects.filter(
                test__polarimeter_number=polarimeter_number).all()

        context['spectrums'] = \
            SpectralAnalysis.objects.filter(
                test__polarimeter_number=polarimeter_number).all()

        return context


@method_decorator(login_required, name='dispatch')
class CreateMixin(CreateView):
    form_class = None
    model = None
    template_name = ''
    load_files = False

    def post(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        if self.load_files:
            form = self.form_class(request.POST, request.FILES)
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            new_obj = form.save(commit=False)
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs


class CreateMixinWithRequest(CreateMixin):
    load_files = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['analysis_date'].widget.attrs.update(
            {'class': 'datepicker'})
        form.fields['analysis_date'].widget.format = '%Y-%m-%d'
        form.fields['analysis_date'].input_formats = ['%Y-%m-%d']
        return form


@method_decorator(login_required, name='dispatch')
class DeleteMixin(DeleteView):
    model = None

    def get(self, request, test_id, obj_id):
        cur_ofs = get_object_or_404(self.model, pk=obj_id)
        cur_ofs.delete()

        cur_obj = get_object_or_404(PolarimeterTest, pk=test_id)
        return redirect(cur_obj)


@method_decorator(login_required, name='dispatch')
class AdcOffsetAddView(CreateView):
    form_class = AdcOffsetCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = AdcOffset

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.test = PolarimeterTest.objects.get(pk=self.kwargs['test_id'])
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AdcOffsetUpdateView(UpdateView):
    form_class = AdcOffsetCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = AdcOffset


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class DetOutputAddView(CreateView):
    form_class = DetOutputCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = DetectorOutput

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.test = PolarimeterTest.objects.get(pk=self.kwargs['test_id'])
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class DetOutputUpdateView(UpdateView):
    form_class = DetOutputCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = DetectorOutput


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class BiasesAddView(CreateView):
    form_class = BiasesCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = Biases

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.test = PolarimeterTest.objects.get(pk=self.kwargs['test_id'])
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BiasesUpdateView(UpdateView):
    form_class = BiasesCreate
    template_name = 'unittests/test_hk_entry_create.html'
    model = Biases


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class TemperatureAddView(CreateView):
    form_class = TemperatureCreate
    template_name = 'unittests/temperature_create.html'
    model = Temperatures

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.test = PolarimeterTest.objects.get(pk=self.kwargs['test_id'])
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TemperatureUpdateView(UpdateView):
    form_class = TemperatureCreate
    template_name = 'unittests/temperature_create.html'
    model = Temperatures


@method_decorator(login_required, name='dispatch')
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


class ReportCreateMixin:
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.test = PolarimeterTest.objects.get(pk=self.kwargs['test_id'])
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TnoiseAddView(ReportCreateMixin, CreateView):
    form_class = NoiseTemperatureAnalysisCreate
    model = NoiseTemperatureAnalysis
    template_name = 'unittests/tnoise_create.html'


@method_decorator(login_required, name='dispatch')
class TnoiseUpdateView(UpdateView):
    form_class = NoiseTemperatureAnalysisCreate
    model = NoiseTemperatureAnalysis
    template_name = 'unittests/tnoise_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class TnoiseDeleteView(DeleteMixin):
    model = NoiseTemperatureAnalysis


class DownloadReportMixin(View):
    model_class = None

    def get(self, request, pk):
        'Send the report as an attachment'

        cur_analysis = get_object_or_404(self.model_class, pk=pk)
        data_file = cur_analysis.report_file
        if data_file.name == '':
            # No file to download
            raise Http404

        data_file.open()
        data = data_file.read()
        resp = HttpResponse(
            data, content_type=mimetypes.guess_type(data_file.name))
        resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            os.path.basename(data_file.name))
        return resp


class TnoiseReport(DownloadReportMixin, View):
    model_class = NoiseTemperatureAnalysis


class SpectralAnalysisListView(View):
    template = 'unittests/spectral_analysis_list.html'

    def get(self, request):
        'Show a list of the results of a spectral analysis'

        context = {
            'spectral_analysis_tests': SpectralAnalysis.objects.all(),
        }
        return render(request, self.template, context)


@method_decorator(login_required, name='dispatch')
class SpectralAnalysisAddView(ReportCreateMixin, CreateView):
    form_class = SpectralAnalysisCreate
    model = SpectralAnalysis
    template_name = 'unittests/spectral_analysis_create.html'


@method_decorator(login_required, name='dispatch')
class SpectralAnalysisUpdateView(UpdateView):
    form_class = SpectralAnalysisCreate
    model = SpectralAnalysis
    template_name = 'unittests/spectral_analysis_create.html'


@method_decorator(login_required, name='dispatch')
class SpectralAnalysisDeleteView(DeleteMixin):
    model = SpectralAnalysis


class SpectralAnalysisReport(DownloadReportMixin, View):
    model_class = SpectralAnalysis


class BandpassAnalysisListView(View):
    template = 'unittests/bandpass_analysis_list.html'

    def get(self, request):
        'Show a list of the results of a bandpass analysis'

        context = {
            'bandpass_analysis_tests': BandpassAnalysis.objects.all(),
        }
        return render(request, self.template, context)


@method_decorator(login_required, name='dispatch')
class BandpassAnalysisAddView(ReportCreateMixin, CreateView):
    form_class = BandpassAnalysisCreate
    model = BandpassAnalysis
    template_name = 'unittests/bandpass_analysis_create.html'


@method_decorator(login_required, name='dispatch')
class BandpassAnalysisUpdateView(UpdateView):
    form_class = BandpassAnalysisCreate
    model = BandpassAnalysis
    template_name = 'unittests/bandpass_analysis_create.html'


@method_decorator(login_required, name='dispatch')
class BandpassAnalysisDeleteView(DeleteMixin):
    model = BandpassAnalysis


class BandpassAnalysisReport(DownloadReportMixin, View):
    model_class = BandpassAnalysis


# REST classes (used for plots)

class TnoiseData(APIView):
    def get(self, request, format=None):
        pol_nums = [x[0] for x in NoiseTemperatureAnalysis.objects.order_by('test__polarimeter_number')
                    .values_list('test__polarimeter_number').distinct()]

        tnoise = []
        tnoise_err = []
        for cur_pol_num in pol_nums:
            data = NoiseTemperatureAnalysis.objects.filter(
                test__polarimeter_number=cur_pol_num).all()
            cur_tnoise = []
            cur_tnoise_err = []
            for cur_val in data:
                cur_tnoise.append(cur_val.noise_temperature)
                cur_tnoise_err.append(cur_val.noise_temperature_err)

            tnoise.append(cur_tnoise)
            tnoise_err.append(cur_tnoise_err)

        return RESTResponse({
            'polarimeters': [get_polarimeter_name(x) for x in pol_nums],
            'tnoise': tnoise,
            'error': tnoise_err,
        })


class UsersData(APIView):
    def get(self, request, format=None):
        users = []

        for cur_user in get_user_model().objects.all():
            users.append({
                'id': cur_user.pk,
                'name': cur_user.username,
                'num_of_tests': PolarimeterTest.objects.filter(author=cur_user).count(),
            })

        return RESTResponse({
            'users': users,
        })


class TestTimeTableData(APIView):
    def get(self, request, format=None):
        date_values = []
        num_of_tests = []

        today = timezone.now().date()
        for days_ago in range(30):
            start = today - timedelta(days=days_ago)
            date_values.append(start)
            num_of_tests.append(PolarimeterTest.objects.filter(
                creation_date=start).count())

        data = {
            'date': date_values,
            'num_of_tests': num_of_tests,
        }

        return RESTResponse(data)
