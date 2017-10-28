# -*- encoding: utf-8 -*-

'''Views of the "unittest" application
'''

import os.path

import simplejson as json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader

from .models import (
    PolarimeterTest,
    AdcOffset,
    DetectorOutput,
    Operator,
    NoiseTemperatureAnalysis
)

from .forms import (
    AddTestForm,
    AddAdcOffset,
    AddDetectorOutputs,
    CreateFromJSON,
)


def list_of_tests(request):
    'Produce a list of the tests in the database'

    context = {
        'tests': PolarimeterTest.objects.all()
    }
    return render(request, 'unittests/testlist.html', context)


def addtest(request):
    'Prompt the user to insert information about a new test, and save it'

    if request.method == 'POST':
        form = AddTestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/unittests/')
    else:
        form = AddTestForm()

    return render(request, 'unittests/addtest.html',
                  {
                      'form': form
                  })


def details(request, test_id):
    'Show details about a test'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    return render(request, 'unittests/details.html', {
        'test': cur_test,
        'adc_offsets': AdcOffset.objects.filter(test=cur_test),
        'det_outputs': DetectorOutput.objects.filter(test=cur_test),
        'tnoise_analyses': NoiseTemperatureAnalysis.objects.filter(test=cur_test),
        'operators': cur_test.operators.all(),
    })


def details_json(request, test_id):
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
        'url': 'details/{0}'.format(test_id),
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


def delete_test(request, test_id):
    'Remove a test from the database'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    cur_test.delete()
    return HttpResponseRedirect('/unittests/')


def download_test(request, test_id):
    'Allow the user to download the data file for a test'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    data_file = cur_test.data_file
    data_file.open()
    data = '\n'.join([x.decode('utf-8') for x in data_file.readlines()])
    resp = HttpResponse(data, content_type='text/plain')
    resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
        os.path.basename(data_file.name))
    return resp


def add_adc_offsets(request, test_id):
    'Set the value of the four ADC offsets for a test'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    if request.method == 'POST':
        form = AddAdcOffset(request.POST)
        if form.is_valid():
            new_offsets = form.save(commit=False)
            new_offsets.test = cur_test
            new_offsets.save()

            return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))
    else:
        form = AddAdcOffset()

    return render(request, 'unittests/addadcofs.html', {
        'test_id': test_id,
        'polarimeter_number': cur_test.polarimeter_number,
        'form': form,
    })


def delete_adc_offsets(request, test_id, ofs_id):
    'Remove a set of ADC offsets'

    cur_ofs = get_object_or_404(AdcOffset, pk=ofs_id)
    cur_ofs.delete()
    return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))


def add_detector_outputs(request, test_id):
    'Set the level of the detector outputs for a test'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    if request.method == 'POST':
        form = AddDetectorOutputs(request.POST)
        if form.is_valid():
            new_output = form.save(commit=False)
            new_output.test = cur_test
            new_output.save()

            return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))
    else:
        form = AddDetectorOutputs()

    return render(request, 'unittests/adddetoutput.html', {
        'test_id': test_id,
        'polarimeter_number': cur_test.polarimeter_number,
        'form': form,
    })


def delete_detector_outputs(request, test_id, output_id):
    'Remove a set of detector_outputs'

    cur_output = get_object_or_404(DetectorOutput, pk=output_id)
    cur_output.delete()
    return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))


def add_detector_outputs_from_json(request, test_id):
    'Import the level of the detector outputs for a test from a JSON record'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    if request.method == 'POST':
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_output = DetectorOutput(
                pwr0_adu=data['detector_offsets']['PWR0_adu'],
                pwr1_adu=data['detector_offsets']['PWR1_adu'],
                pwr2_adu=data['detector_offsets']['PWR2_adu'],
                pwr3_adu=data['detector_offsets']['PWR3_adu'],
            )
            new_output.test = cur_test
            new_output.save()

            return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))
    else:
        form = CreateFromJSON(initial={'json_text': '''{                           
    "detector_offsets": {   
        "PWR0_adu": 1.0,
        "PWR1_adu": 2.0,
        "PWR2_adu": 3.0,
        "PWR3_adu": 4.0 
    }                       
}'''})

    return render(request, 'unittests/adddetoutput.html', {
        'test_id': test_id,
        'polarimeter_number': cur_test.polarimeter_number,
        'form': form,
    })


def list_of_noise_temperatures(request):
    'Show a list of the results of Tnoise tests'

    context = {
        'tnoise_tests': NoiseTemperatureAnalysis.objects.all(),
    }
    return render(request, 'unittests/tnoiselist.html', context)


def add_noise_temperature(request, test_id):
    'Add a new estimate for the noise temperature of a polarimeter'

    context = {
        'test_id': test_id,
    }
    return render(request, 'unittests/addtnoise.html', context)


def add_noise_temperature_from_json(request, test_id):
    'Import a JSON file containing the estimates of Tnoise for a polarimeter'

    'Import the level of the detector outputs for a test from a JSON record'

    cur_test = get_object_or_404(PolarimeterTest, pk=test_id)
    if request.method == 'POST':
        form = CreateFromJSON(request.POST)
        if form.is_valid():
            data = json.loads(form.cleaned_data['json_text'])
            new_analysis = NoiseTemperatureAnalysis(
                polarimeter_gain=data['average_gain']['mean'],
                polarimeter_gain_err=data['average_gain']['std'],
                gain_product=data['gain_prod']['mean'],
                gain_product_err=data['gain_prod']['std'],
                noise_temperature=data['tnoise']['mean'],
                noise_temperature_err=data['tnoise']['std'],
                estimation_method=data['estimation_method'],
                code_version=data['striptun_version'],
                code_commit=data['latest_git_commit'],
                analysis_date=data['date']
            )
            new_analysis.test = cur_test
            new_analysis.save()

            return HttpResponseRedirect('/unittests/details/{0}'.format(test_id))
    else:
        form = CreateFromJSON(initial={'json_text': '''{
    "average_gain": {
        "mean": 3045.8428562313666,
        "std": 562.5624766927529
    },
    "gain_prod": {
        "mean": 2918.8247765887895,
        "std": 741.1967061432678
    },
    "tnoise": {
        "mean": 18.516167480747846,
        "std": 7.8330311448372605
    },
    "estimation_method": "nonlinear fit",
    "striptun_version": "1.0",
    "latest_git_commit": "a26d6b81ca46f3e33361a4bef3a58b884b6175bb",
    "date": "2017-10-01"
}'''})

    return render(request, 'unittests/addtnoise.html', {
        'test_id': test_id,
        'form': form,
    })
