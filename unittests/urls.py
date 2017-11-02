# -*- encoding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.TestListView.as_view(), name='listoftests'),
    url(r'^tests/add$', views.AddTestView.as_view(), name='addtest'),
    url(r'^tests/(?P<test_id>\d+)/newadcoffset$',
        views.AdcOffsetAddView.as_view(), name='addAdcOffset'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutput$',
        views.DetOutputAddView.as_view(), name='adddetoutputs'),
    url(r'^tests/(?P<test_id>\d+)/newdetoutputjson$',
        views.DetOutputJsonView.as_view(), name='adddetoutputsjson'),

    url(r'^tests/(?P<test_id>\d+)/delete$',
        views.TestDeleteView.as_view(), name='deletetest'),
    url(r'^tests/(?P<test_id>\d+)/AdcOffset/(?P<ofs_id>\d+)/delete$',
        views.AdcOffsetDeleteView.as_view(), name='deleteAdcOffset'),
    url(r'^tests/(?P<test_id>\d+)/detoutput/(?P<output_id>\d+)/delete$',
        views.DetOutputDeleteView.as_view(), name='deletedetoutputs'),

    url(r'^details/(?P<test_id>\d+)/$',
        views.TestDetails.as_view(), name='details'),
    url(r'^details/(?P<test_id>\d+)/json/$',
        views.TestDetailsJson.as_view(), name='detailsjson'),
    url(r'^details/(?P<test_id>\d+)/download/$',
        views.TestDownload.as_view(), name='downloadtest'),

    url(r'^tnoise/$', views.TnoiseListView.as_view(), name='listofnoisetemps'),
    url(r'^tnoise/add/(?P<test_id>\d+)$',
        views.TnoiseAddView.as_view(), name='addtnoise'),
    url(r'^tnoise/add/(?P<test_id>\d+)/json$',
        views.TnoiseAddFromJsonView.as_view(), name='addtnoisejson'),
]
