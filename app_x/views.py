# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def info( request ):
    """ Returns basic info.
        Getting this running shows that logging is working, and that the settings_app file is properly reading env-vars. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    start = datetime.datetime.now()
    rtrn_dct = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=request.scheme, hst=request.META['HTTP_HOST'], uri=request.META.get('REQUEST_URI', request.META['PATH_INFO']) ) },  # REQUEST_URI not available via run-server
        'response': {
            'documentation': settings_app.README_URL,
            'elapsed_time': str( datetime.datetime.now() - start ),
            'message': 'ok' } }
    return HttpResponse( json.dumps(rtrn_dct, sort_keys=True, indent=2), content_type='application/javascript; charset=utf-8' )
