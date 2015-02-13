# -*- coding: utf-8 -*-

from django.contrib import admin
from dashboard_app.models import Widget


class WidgetAdmin( admin.ModelAdmin ):
    prepopulated_fields = {"slug": ("title",)}
    # date_hierarchy = u'create_datetime'
    ordering = [ u'id' ]
    list_display = [ u'id', u'title', u'data_contact_email_address'  ]
    # list_filter = [ u'title' ]
    search_fields = [ u'id', u'title', u'data_contact_email_address'  ]
    readonly_fields = [ u'id', u'data_contact_email_address'  ]
    radio_fields = {"best_goal": admin.HORIZONTAL}


admin.site.register( Widget, WidgetAdmin )
