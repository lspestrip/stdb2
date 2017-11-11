# -*- encoding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.TestListView.as_view(), name='test_list'),
    url(r'^tests/(?P<test_id>\d+)/$',
        views.TestDetails.as_view(), name='test_details'),
    url(r'^tests/(?P<test_id>\d+)/json/$',
        views.TestDetailsJson.as_view(), name='test_details_json'),
    url(r'^tests/(?P<test_id>\d+)/download/$',
        views.TestDownload.as_view(), name='test_download'),
    url(r'^tests/create$', views.TestCreate.as_view(), name='test_create'),
    url(r'^tests/(?P<test_id>\d+)/delete$',
        views.TestDeleteView.as_view(), name='test_delete'),

    url(r'^tests/(?P<test_id>\d+)/newadcoffset$',
        views.AdcOffsetAddView.as_view(), name='adc_create'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutput$',
        views.DetOutputAddView.as_view(), name='detoutput_create'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutputjson$',
        views.DetOutputJsonView.as_view(), name='detoutput_create_json'),
    url(r'^tests/(?P<test_id>\d+)/newtemperature$',
        views.TemperatureAddView.as_view(), name='temperature_create'),

    url(r'^tests/(?P<test_id>\d+)/AdcOffset/(?P<obj_id>\d+)/delete$',
        views.AdcOffsetDeleteView.as_view(), name='adc_delete'),
    url(r'^tests/(?P<test_id>\d+)/detoutput/(?P<obj_id>\d+)/delete$',
        views.DetOutputDeleteView.as_view(), name='detoutput_delete'),
    url(r'^tests/(?P<test_id>\d+)/temperature/(?P<obj_id>\d+)/delete$',
        views.TemperatureDeleteView.as_view(), name='temperature_delete'),

    url(r'^tnoise/$', views.TnoiseListView.as_view(), name='tnoise_list'),
    url(r'^tnoise/add/(?P<test_id>\d+)$',
        views.TnoiseAddView.as_view(), name='tnoise_create'),
    url(r'^tnoise/add/(?P<test_id>\d+)/json$',
        views.TnoiseAddFromJsonView.as_view(), name='tnoise_create_json'),
]
