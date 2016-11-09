# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import include, url
from django.views.generic import RedirectView
from app_x import views

urlpatterns = [

    url( r'^info/$',  views.hi, name='info_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='foo:info_url') ),

    ]
