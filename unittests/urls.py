# -*- encoding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^dashboard/$', TemplateView.as_view(template_name='unittests/dashboard.html'),
        name='dashboard'),

    url(r'^$', views.TestListView.as_view(), name='test_list'),
    url(r'^tests/(?P<test_id>\d+)/$',
        views.TestDetails.as_view(), name='test_details'),
    url(r'^tests/(?P<pk>\d+)/update$',
        views.TestUpdate.as_view(), name='test_update'),
    url(r'^tests/(?P<test_id>\d+)/json/$',
        views.TestDetailsJson.as_view(), name='test_details_json'),
    url(r'^tests/(?P<test_id>\d+)/plot/$',
        views.TestPwrPlot.as_view(), name='test_pwr_plot'),
    url(r'^tests/(?P<test_id>\d+)/download/$',
        views.TestDownload.as_view(), name='test_download'),
    url(r'^tests/create$', views.TestCreate.as_view(), name='test_create'),
    url(r'^tests/(?P<pk>\d+)/delete$',
        views.TestDeleteView.as_view(), name='test_delete'),

    url(r'^(?P<pol_name>STRIP\d+)/$',
        views.PolarimeterDetails.as_view(), name='polarimeter_details'),

    url(r'^tests/(?P<test_id>\d+)/newadcoffset$',
        views.AdcOffsetAddView.as_view(), name='adc_create'),
    url(r'^tests/(?P<test_id>\d+)/newadcoffset/json$',
        views.AdcOffsetJsonView.as_view(), name='adc_create_json'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutput$',
        views.DetOutputAddView.as_view(), name='detoutput_create'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutput/json$',
        views.DetOutputJsonView.as_view(), name='detoutput_create_json'),
    url(r'^tests/(?P<test_id>\d+)/newbiases$',
        views.BiasesAddView.as_view(), name='biases_create'),
    url(r'^tests/(?P<test_id>\d+)/newbiases/json$',
        views.BiasesJsonView.as_view(), name='biases_create_json'),
    url(r'^tests/(?P<test_id>\d+)/newtemperature$',
        views.TemperatureAddView.as_view(), name='temperature_create'),
    url(r'^tests/(?P<test_id>\d+)/temperature/json$',
        views.TemperatureJsonView.as_view(), name='temperature_create_json'),
    url(r'^tests/(?P<test_id>\d+)/newtemperature/duplicatelast$',
        views.duplicate_last_temperature, name='temperature_duplicate_last'),

    url(r'^adcoffset/(?P<pk>\d+)/update$',
        views.AdcOffsetUpdateView.as_view(), name='adc_update'),
    url(r'^detoutput/(?P<pk>\d+)/update$',
        views.DetOutputUpdateView.as_view(), name='detoutput_update'),
    url(r'^biases/(?P<pk>\d+)/update$',
        views.BiasesUpdateView.as_view(), name='biases_update'),
    url(r'^temperature/(?P<pk>\d+)/update$',
        views.TemperatureUpdateView.as_view(), name='temperature_update'),

    url(r'^adcoffset/(?P<pk>\d+)/delete$',
        views.AdcOffsetDeleteView.as_view(), name='adc_delete'),
    url(r'^detoutput/(?P<pk>\d+)/delete$',
        views.DetOutputDeleteView.as_view(), name='detoutput_delete'),
    url(r'^biases/(?P<pk>\d+)/delete$',
        views.BiasesDeleteView.as_view(), name='biases_delete'),
    url(r'^temperature/(?P<pk>\d+)/delete$',
        views.TemperatureDeleteView.as_view(), name='temperature_delete'),

    url(r'^tnoise/$', views.TnoiseListView.as_view(), name='tnoise_list'),
    url(r'^tnoise/(?P<pk>\d+)$', views.TnoiseReport.as_view(), name='tnoise_report'),
    url(r'^tnoise/add/(?P<test_id>\d+)$',
        views.TnoiseAddView.as_view(), name='tnoise_create'),
    url(r'^tnoise/(?P<pk>\d+)/update$',
        views.TnoiseUpdateView.as_view(), name='tnoise_update'),
    url(r'^tnoise/(?P<pk>\d+)/delete$',
        views.TnoiseDeleteView.as_view(), name='tnoise_delete'),

    url(r'^bandpass/$', views.BandpassAnalysisListView.as_view(),
        name='bandpass_list'),
    url(r'^bandpass/(?P<pk>\d+)$',
        views.BandpassAnalysisReport.as_view(), name='bandpass_report'),
    url(r'^bandpass/add/(?P<test_id>\d+)$',
        views.BandpassAnalysisAddView.as_view(), name='bandpass_create'),
    url(r'^bandpass/(?P<pk>\d+)/update$',
        views.BandpassAnalysisUpdateView.as_view(), name='bandpass_update'),
    url(r'^bandpass/(?P<pk>\d+)/delete$',
        views.BandpassAnalysisDeleteView.as_view(), name='bandpass_delete'),

    url(r'^spectrum/$', views.SpectralAnalysisListView.as_view(), name='spectrum_list'),
    url(r'^spectrum/(?P<pk>\d+)$',
        views.SpectralAnalysisReport.as_view(), name='spectrum_report'),
    url(r'^spectrum/add/(?P<test_id>\d+)$',
        views.SpectralAnalysisAddView.as_view(), name='spectrum_create'),
    url(r'^spectrum/(?P<pk>\d+)/update$',
        views.SpectralAnalysisUpdateView.as_view(), name='spectrum_update'),
    url(r'^spectrum/(?P<pk>\d+)/delete$',
        views.SpectralAnalysisDeleteView.as_view(), name='spectrum_delete'),

    # REST API

    url(r'^api/tnoise/$', views.TnoiseAllData.as_view(), name='api-tnoise-all-data'),
    url(r'^api/tnoise/(?P<pk>\d+)$',
        views.TnoiseData.as_view(), name='api-tnoise-data'),

    url(r'^api/bandpass/$', views.BandpassAllData.as_view(),
        name='api-bandpass-all-data'),
    url(r'^api/bandpass/(?P<pk>\d+)$',
        views.BandpassData.as_view(), name='api-bandpass-data'),

    url(r'^api/spectrum/$', views.SpectrumAllData.as_view(),
        name='api-spectrum-all-data'),
    url(r'^api/spectrum/(?P<pk>\d+)$',
        views.SpectrumData.as_view(), name='api-spectrum-data'),

    url(r'^api/tests/STRIP(?P<num>\d+)/$', views.TestsByPolarimeter.as_view(),
        name='api-tests-polarimeter'),

    url(r'^api/tests/types/$', views.TestTypes.as_view(),
        name='api-tests-types'),
    url(r'^api/tests/types/(?P<pk>\d+)$', views.TestsByType.as_view(),
        name='api-tests-types'),

    url(r'^api/tests/users/$', views.UsersData.as_view(),
        name='api-tests-users'),
    url(r'^api/tests/countbydate/$', views.TestTimeTableData.as_view(),
        name='api-tests-countbydate'),
]
