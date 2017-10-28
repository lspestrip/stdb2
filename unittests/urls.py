# -*- encoding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_of_tests, name='listoftests'),
    url(r'^tests/add$', views.addtest, name='addtest'),
    url(r'^tests/(?P<test_id>\d+)/newadcoffset$',
        views.add_adc_offsets, name='addAdcOffset'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutput$',
        views.add_detector_outputs, name='adddetoutputs'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutputjson$',
        views.add_detector_outputs_from_json, name='adddetoutputsjson'),

    url(r'^tests/(?P<test_id>\d+)/delete$',
        views.delete_test, name='deletetest'),
    url(r'^tests/(?P<test_id>\d+)/AdcOffset/(?P<ofs_id>\d+)/delete$',
        views.delete_adc_offsets, name='deleteAdcOffset'),
    url(r'^tests/(?P<test_id>\d+)/detoutput/(?P<output_id>\d+)/delete$',
        views.delete_detector_outputs, name='deletedetoutputs'),

    url(r'^details/(?P<test_id>\d+)/$', views.details, name='details'),
    url(r'^details/(?P<test_id>\d+)/json/$',
        views.details_json, name='detailsjson'),
    url(r'^details/(?P<test_id>\d+)/download/$',
        views.download_test, name='downloadtest'),

    url(r'^tnoise/$', views.list_of_noise_temperatures, name='listofnoisetemps'),
    url(r'^tnoise/add/(?P<test_id>\d+)$',
        views.add_noise_temperature, name='addtnoise'),
    url(r'^tnoise/add/(?P<test_id>\d+)/json$',
        views.add_noise_temperature_from_json, name='addtnoisejson'),
]
