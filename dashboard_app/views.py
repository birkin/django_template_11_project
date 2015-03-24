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
chart_maker = models.ChartMaker()
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
    ( chart_values, chart_percentages, chart_range, chart_keys ) = chart_maker.prep_data( widget.data_points )
    gchart_detail_url = chart_maker.prep_gchart_detail_url()
    jdict = widget.get_jdict( request.build_absolute_uri() )
    if request.GET.get( u'format', None ) == u'json':
        output = json.dumps( jdict, sort_keys=True, indent=2 )
        if request.GET.get( u'callback', None ):
            output = u'%s(%s)' % ( request.GET.get(u'callback'), output )
        return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
    else:
        # return HttpResponse( jdict[u'data_main'][u'title'] )
        context = {
            u'widget': widget,
            u'detailchart_percentages': chart_percentages,
            u'detailchart_range': chart_range,
            u'detailchart_keys': chart_keys,
            u'data_index': 0  # so url can look 1-based, whereas google chart-api is zero-based
            }
        return render( request, u'dashboard_app_templates/widget_detail.html', context )


    # widget_instance = Widget.objects.get( slug=identifier )

    # detailchart_tuples = eval( widget_instance.data_points )

    # detailchart_values = []
    # for element in detailchart_tuples:
    #     detailchart_values.append( element[1] )

    # detailchart_percentages = utility_code.makeChartPercentages( detailchart_values )

    # detailchart_range = utility_code.makeChartRanges( detailchart_percentages )

    # detailchart_keys = []
    # for element in detailchart_tuples:
    #     detailchart_keys.append( element[0] )

    # page_dict = {
    #     'host':settings_app.HOST_URL_BASE,
    #     'widget':widget_instance,
    #     'detailchart_percentages':detailchart_percentages,
    #     'detailchart_range':detailchart_range,
    #     'detailchart_keys':detailchart_keys,
    #     'detailchart_values':detailchart_values,
    #     'data_index':int(data_index)
    #     # 'data_index':int(data_index) - 1 # so url can look 1-based, whereas google chart-api is zero-based
    #     }
    # return render_to_response( 'dashboard/info.html', page_dict )


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
