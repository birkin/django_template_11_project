# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView


urlpatterns = patterns('',

    url( r'^info/$',  'dashboard_app.views.info', name=u'info_url' ),

    url( r'^request_widget/$',  'dashboard_app.views.request_widget', name=u'request_widget_url' ),

    url( r'^widget/(?P<identifier>[^/]+)/$',  'dashboard_app.views.widget', name=u'widget_url' ),

    url( r'^tag/(?P<tag>[^/]+)/$',  'dashboard_app.views.tag', name=u'tag_url' ),

    url( r'^shib_login/$',  'dashboard_app.views.shib_login', name=u'shib_login_url' ),
    url( r'^logout/$',  'dashboard_app.views.shib_logout', name=u'logout_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name=u'info_url') ),

    )
