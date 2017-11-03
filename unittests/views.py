# -*- encoding: utf-8 -*-

'''Views of the "unittest" application
'''

import os.path

import simplejson as json

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
)

from .models import (
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    NoiseTemperatureAnalysis,
    dict_to_tnoise_analysis,
    dict_to_detector_output,
)

from .forms import (
    TestForm,
    AdcOffsetCreate,
    DetOutputCreate,
    CreateFromJSON,
)


class TestListView(View):
    template = 'unittests/polarimetertest_list.html'

    def get(self, request):
        'Produce a list of the tests in the database'

        context = {
            'tests': PolarimeterTest.objects.all()
        }
        return render(request, self.template, context)


class TestCreate(CreateView):
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


class TestDetails(View):
    template_name = 'unittests/polarimetertest_details.html'

    def get(self, request, test_id):
        'Show details about a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        return render(request, self.template_name, {
            'test': cur_test,
            'adc_offsets': AdcOffset.objects.filter(test=cur_test),
            'det_outputs': DetectorOutput.objects.filter(test=cur_test),
            'tnoise_analyses': NoiseTemperatureAnalysis.objects.filter(test=cur_test),
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
            'operators': [x.name for x in cur_test.operators.all()],
        }
        return HttpResponse(json.dumps(result, indent=4), content_type='application/json')


class TestDeleteView(DeleteView):
    model = PolarimeterTest
    success_url = reverse_lazy('unittests:test_list')


class TestDownload(View):
    def get(self, request, test_id):
        'Allow the user to download the data file for a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        data_file = cur_test.data_file
        data_file.open()
        data = data_file.read()
        resp = HttpResponse(data, content_type='application/fits')
        resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            os.path.basename(data_file.name))
        return resp


class AdcOffsetAddView(View):
    def post(self, request, test_id):
        'Set the value of the four ADC offsets for a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = AdcOffsetCreate(request.POST)
        if form.is_valid():
            new_offsets = form.save(commit=False)
            new_offsets.test = cur_test
            new_offsets.save()

            return redirect(cur_test)

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = AdcOffsetCreate()

        return render(request, 'unittests/adc_create.html', {
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class AdcOffsetDeleteView(View):
    def get(self, request, test_id, ofs_id):
        'Remove a set of ADC offsets'

        cur_ofs = get_object_or_404(AdcOffset, pk=ofs_id)
        cur_ofs.delete()
        return redirect('unittests:test_details', kwargs={'test_id': test_id})


class DetOutputAddView(View):
    def post(self, request, test_id):
        'Set the level of the detector outputs for a test'

        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = DetOutputCreate(request.POST)
        if form.is_valid():
            new_output = form.save(commit=False)
            new_output.test = cur_test
            new_output.save()

            return redirect('unittests:test_details', kwargs={'test_id': test_id})

    def get(self, request, test_id):
        cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
        form = DetOutputCreate()

        return render(request, 'unittests/detoutput_create.html', {
            'test_id': test_id,
            'polarimeter_number': cur_test.polarimeter_number,
            'form': form,
        })


class DetOutputDeleteView(View):
    def get(self, request, test_id, output_id):
        'Remove a set of detector_outputs'

        cur_output = get_object_or_404(DetectorOutput, pk=output_id)
        cur_output.delete()
        return redirect('unittests:test_details', kwargs={'test_id': test_id})


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

            return redirect('unittests:test_details', kwargs={'test_id': test_id})

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
                })
        })

        return render(request, 'unittests/detoutput.html', {
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


class TnoiseAddView(View):
    template = 'unittests/tnoise_create.html'

    def get(self, request, test_id):
        'Add a new estimate for the noise temperature of a polarimeter'

        context = {
            'test_id': test_id,
        }
        return render(request, self.template, context)


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

            return redirect('unittests:test_details', kwargs={'test_id': test_id})

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
                })
        })

        return render(request, 'unittests/tnoise_create.html', {
            'test_id': test_id,
            'form': form,
        })
