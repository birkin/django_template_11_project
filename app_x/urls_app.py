# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView


urlpatterns = patterns('',

    url( r'^hi/$',  'app_x.views.hi', name=u'hi_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name=u'info_url') ),

    )
