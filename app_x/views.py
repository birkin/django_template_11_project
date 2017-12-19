# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def info( request ):
    """ Returns basic info. """
    start = datetime.datetime.now()
    rtrn_dct = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=request.scheme, hst=request.META['HTTP_HOST'], uri=request.META['REQUEST_URI'] )
        },
        'response': {
            'documentation': settings_app.README_URL,
            'elapsed_time': str( datetime.datetime.now() - start ),
            'message': 'ok'
        }
    }
    jsn = json.dumps( rtrn_dct, sort_keys=True, indent=2 )
    return HttpResponse( jsn, content_type='application/javascript; charset=utf-8' )
