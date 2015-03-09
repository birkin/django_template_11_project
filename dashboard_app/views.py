# -*- coding: utf-8 -*-

import json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from dashboard_app import models
from dashboard_app.models import Widget

log = logging.getLogger(__name__)
shib_view_helper = models.ShibViewHelper()
widget_helper = models.WidgetHelper()
chart_helper = models.ChartMaker()
minichart_maker = models.MinichartMaker()


def info( request ):
    """ Returns info page. """
    first_widget = Widget.objects.all()[0]
    context = {
        u'email_general_help': os.environ[u'DSHBRD__EMAIL_GENERAL_HELP'],
        u'first_widget_url': reverse( u'widget_url', kwargs={u'identifier': first_widget.slug} )
        }
    return render( request, u'dashboard_app_templates/info.html', context )


def widget( request, identifier ):
    """ Displays requested widget. """
    # from django.shortcuts import get_object_or_404
    widget = get_object_or_404( Widget, slug=identifier )
    ( chart_values, chart_percentages, chart_range, chart_keys ) = chart_helper.prep_data( widget.data_points )
    jdict = widget.get_jdict( request.build_absolute_uri() )
    if request.GET.get( u'format', None ) == u'json':
        output = json.dumps( jdict, sort_keys=True, indent=2 )
        if request.GET.get( u'callback', None ):
            output = u'%s(%s)' % ( request.GET.get(u'callback'), output )
        return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
    else:
        return HttpResponse( jdict[u'data_main'][u'title'] )

    # widget_instance = Widget.objects.get( slug=identifier )
    # trend_direction_dict = { 1:'up', -1:'down', 0:'flat' }
    # trend_color_dict = { 1:'blue', -1:'red', 0:'blank' }
    # minichart_tuples = utility_code.extractMinichartData( eval(widget_instance.data_points) )
    # minichart_values = [ minichart_tuples[0][1], minichart_tuples[1][1], minichart_tuples[2][1], minichart_tuples[3][1]  ]
    # minichart_percentages = utility_code.makeChartPercentages( minichart_values )
    # minichart_range = utility_code.makeChartRanges( minichart_percentages )
    # page_dict = {
    #     'media_directory':project_settings.MEDIA_URL,
    #     'widget':widget_instance,
    #     'trend_direction':trend_direction_dict[ widget_instance.trend_direction ],
    #     'trend_color':trend_color_dict[ widget_instance.trend_color ],
    #     'minichart_percentages':minichart_percentages,
    #     'minichart_range':minichart_range,
    #     }
    # return render_to_response( 'dashboard/widget.html', page_dict )
    # return HttpResponse( u'coming' )


def request_widget( request ):
    """ STUB
        Displays/handles form for requesting a widget. """
    return HttpResponse( u'request-widget url' )


def tag( request, tag ):
    """ STUB
        Displays set of widgets for given tag. """
    # minichart_data = minichart_maker.prep_data( json.loads(widget.data_points) )  # will be used here, not in widget view
    return HttpResponse( u'tag url' )


def shib_login( request ):
    """ Examines shib headers, sets session-auth, & returns user to request page. """
    log.debug( u'in views.shib_login(); starting' )
    if request.method == u'POST':  # from request_login.html
        log.debug( u'in views.shib_login(); post detected' )
        return HttpResponseRedirect( os.environ[u'DSHBRD__SHIB_LOGIN_URL'] )  # forces reauth if user clicked logout link
    request.session[u'shib_login_error'] = u''  # initialization; updated when response is built
    ( validity, shib_dict ) = shib_view_helper.check_shib_headers( request )
    return_url = request.GET.get(u'return_url', reverse(u'info_url') )
    return_response = shib_view_helper.build_response( request, validity, shib_dict, return_url )
    log.debug( u'in views.shib_login(); about to return response' )
    return return_response


def shib_logout( request ):
    """ Clears session, hits shib logout, and redirects user to landing page. """
    request.session[u'authz_info'][u'authorized'] = False
    logout( request )
    scheme = u'https' if request.is_secure() else u'http'
    redirect_url = u'%s://%s%s' % ( scheme, request.get_host(), reverse(u'request_url') )
    if request.get_host() == u'127.0.0.1' and project_settings.DEBUG == True:
        pass
    else:
        encoded_redirect_url =  urlquote( redirect_url )  # django's urlquote()
        redirect_url = u'%s?return=%s' % ( os.environ[u'DSHBRD__SHIB_LOGOUT_URL_ROOT'], encoded_redirect_url )
    log.debug( u'in vierws.shib_logout(); redirect_url, `%s`' % redirect_url )
    return HttpResponseRedirect( redirect_url )
