# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, itertools
from django.conf import settings as project_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils.text import slugify

log = logging.getLogger(__name__)


class Widget(models.Model):
    """ TODO: old original code; update! """

    BEST_GOAL_CHOICES = (
        (1, 'Higher'),
        (-1, 'Lower'), )

    TREND_COLOR_CHOICES = (
        (1, 'Good'),
        (-1, 'Bad'),
        (0, 'Not Applicable'), )

    TREND_DIRECTION_CHOICES = (
        (1, 'Up'),
        (-1, 'Down'),
        (0, 'Flat'), )

    title = models.CharField( unique=True, max_length=30 )
    slug = models.SlugField( unique=True )
    title_info = models.TextField()
    baseline_value = models.IntegerField( null=True, blank=True, help_text='Filled automatically from data_points.' )
    baseline_info = models.TextField( blank=True )
    best_goal = models.IntegerField( choices=BEST_GOAL_CHOICES, help_text='Required. Note, sometimes the \'best\' number will be the lowest one (example: tracking Missing Books).' )
    best_value = models.IntegerField( null=True, blank=True, help_text='Filled automatically from data_points.' )
    best_value_info = models.TextField( blank=True )
    current_value = models.IntegerField( null=True, blank=True, help_text='Filled automatically from data_points.' )
    current_value_info = models.TextField( blank=True )
    trend_direction = models.IntegerField( null=True, blank=True, choices=TREND_DIRECTION_CHOICES, help_text='Filled automatically from data_points.' )
    trend_color = models.IntegerField( null=True, blank=True, choices=TREND_COLOR_CHOICES, help_text='Filled automatically from data_points and \'best goal\'.')
    trend_info = models.TextField( blank=True )
    data_points = models.TextField( help_text='Data may be filled programatically. If entered manually, it should consist of valid json, formatted like this: [ {"March_2008": 123}, {"April_2008": 456} ]' )
    max_data_points_count = models.IntegerField( null=True, blank=True, help_text='Optional. Maximum number of data_points; i.e. 12 for a yearly month-by-month widget.')
    key_label = models.CharField( max_length=50, help_text='A brief description of the \'key\' in the above \'data points\' key-value pairs.' )
    value_label = models.CharField( max_length=50, help_text='A brief description of the \'value\' in the above \'data points\' key-value pairs.' )
    data_contact_name = models.CharField( max_length=50 )
    data_contact_email_address = models.EmailField()
    more_info_url = models.URLField( blank=True, help_text='Not required, but strongly suggested.' )
    active = models.BooleanField( default=True, help_text='Means data is still being collected for this widget.' )
    # tags = models.ManyToManyField( 'Tag', blank=True, null=True )

    def __unicode__(self):
        return smart_unicode(self.title)

    def save(self):
        wh = WidgetHelper()
        try:
            self = wh.process_data( self )
            super(Widget, self).save() # Call the "real" save() method
        except Exception, e:
            log.debug( u'EXCEPTION, %s' % unicode(repr(e)) )
            self.data_points = 'INVALID_DATA: -->' + self.data_points + '<--'
            super(Widget, self).save() # Call the "real" save() method

    def get_jdict( self, url ):
        """ Returns widget data in json-compatible dict. """
        widget_helper = WidgetHelper()
        jdct = widget_helper.output_jdict( self, url )
        return jdct

    # def _get_trend_direction_text(self):
    #     '''Returns trend-direction text from trend-direction integer'''
    #     trend_direction_dict = { 1:'up', -1:'down', 0:'flat' }
    #     return trend_direction_dict[ self.trend_direction ]
    # trend_direction_text = property(_get_trend_direction_text)

    # def _get_trend_color_text(self):
    #     '''Returns trend-color text from trend-color integer'''
    #     trend_color_dict = { 1:'blue', -1:'red', 0:'blank' }
    #     return trend_color_dict[ self.trend_color ]
    # trend_color_text = property(_get_trend_color_text)

    # def _get_minichart_percentages(self):
    #     '''Returns values from minichart-percentage calculations'''
    #     from dashboard_app import utility_code
    #     minichart_tuples = utility_code.extractMinichartData( eval(self.data_points) )
    #     minichart_values = [ minichart_tuples[0][1], minichart_tuples[1][1], minichart_tuples[2][1], minichart_tuples[3][1]  ]
    #     minichart_percentages = utility_code.makeChartPercentages( minichart_values )
    #     return minichart_percentages
    # minichart_percentages = property( _get_minichart_percentages )

    # def _get_minichart_range(self):
    #     '''Returns range-values for minichart'''
    #     from dashboard_app import utility_code
    #     minichart_range = utility_code.makeChartRanges( self.minichart_percentages )
    #     return minichart_range
    # minichart_range = property( _get_minichart_range )

    # class Meta:
    #     ordering = ['title']

    # end class Widget


class WidgetHelper( object ):
    """ Contains helpers for processing Widget() data. """

    def process_data( self, widget ):
        """ Ensures data points are valid, and calculates and sets values for certain fields.
            Called by Widget.save() """
        lst = self.validate_data( widget.data_points )
        widget.baseline_value = lst[0].values()[0]
        widget.best_value = self.get_best_value( widget.best_goal, lst )
        widget.current_value = lst[-1].values()[0]
        widget.trend_direction = self.get_trend_direction( widget.current_value, lst )
        widget.trend_color = self.get_trend_color( widget.trend_direction, widget.best_goal )
        return widget

    def validate_data( self, data ):
        """ Ensures data is a list of dicts.
            Called by process_data() """
        lst = json.loads( data )
        for dct in lst:
            assert type( dct ) == dict
        return lst

    def get_best_value( self, best_goal, lst ):
        """ Grabs best value in list, which will be the highest or lowest, depending on widget.best_goal.
            Called by process_data() """
        initial_value = lst[0].values()[0]
        ( high_value, low_value ) = ( initial_value, initial_value )
        for dct in lst:
            value = dct.values()[0]
            high_value = value if (value > high_value) else high_value
            low_value = value if (value < low_value) else low_value
        if best_goal == 1:  # best is higher
            return_val = high_value
        else:
            return_val = low_value
        return return_val

    def get_trend_direction( self, current_value, lst ):
        """ Grabs trend direction.
            Called by process_data() """
        previous_value = lst[-2].values()[0]
        if current_value > previous_value:
            trend_direction = 1
        elif current_value == previous_value:
            trend_direction = 0
        else:
            trend_direction = -1
        return trend_direction

    def get_trend_color( self, trend_direction, best_goal ):
        """ Sets the trend color based on the trend-direction and best-goal.
            Called by process_data() """
        if trend_direction == 0:
            trend_color = 0
        elif trend_direction == best_goal:
            trend_color = 1
        else:
            trend_color = -1
        return trend_color

    def get_trend_dicts( self ):
        """ Returns static dicts.
            Called by Widget.SOME_PROPERTY? """
        trend_direction_dict = { 1:'up', -1:'down', 0:'flat' }
        trend_color_dict = { 1:'blue', -1:'red', 0:'blank' }
        return ( trend_direction_dict, trend_color_dict )

    def output_jdict( self, widget, url ):
        """ Returns widget data in json-compatible dict format.
            Called by Widget.json_data """
        main_info = {
            u'title': widget.title,
            u'slug': widget.slug,
            u'data_points': widget.data_points,
            u'key_label': widget.key_label,
            u'value_label': widget.value_label,
            u'data_contact_name': widget.data_contact_name,
            u'data_contact_email_address': widget.data_contact_email_address,
            u'more_info_url': widget.more_info_url,
            }
        additional_info = {
            u'title_info': widget.title_info,
            u'baseline_value': widget.baseline_value,
            u'baseline_info': widget.baseline_info,
            u'best_goal': widget.best_goal,
            u'best_value': widget.best_value,
            u'best_value_info': widget.best_value_info,
            u'current_value': widget.current_value,
            u'current_value_info': widget.current_value_info,
            u'trend_direction': widget.trend_direction,
            u'trend_color': widget.trend_color,
            u'max_data_points_count': widget.max_data_points_count,
            }
        dct = {
            u'data_main': main_info,
            u'data_other': additional_info,
            u'request_datetime': unicode( datetime.datetime.now() ),
            u'request_url': url
            }
        return dct

    # end class WidgetHelper


class ChartMaker( object ):
    """ Contains helpers for creating the main chart. """

    def prep_data( self, data_points ):
        """ Calls helper functions for preparing data.
            Called by views.widget() """
        ( keys, values ) = self.extract_values( data_points )
        # values = self.extract_values( data_points )
        percentages = self.make_percentages( values )
        ranges = self.make_ranges( percentages )
        return ( values, percentages, ranges, keys )
        # return ( u'values', 'percentages', u'range', u'keys' )

    def extract_values( self, data_points ):
        """ Returns values from list of dcts.
            Called by prep_data() """
        log.debug( u'in models.ChartMaker.extract_values(); data_points, `%s`; type(data_points), `%s`' % (pprint.pformat(data_points), type(data_points)) )
        ( keys, values ) = ( [], [] )
        for dct in json.loads( data_points ):
            keys.append( dct.items()[0][0] )
            values.append( dct.items()[0][1] )
        log.debug( u'in models.ChartMaker.extract_values(); keys, `%s`; values, `%s`' % (keys, values) )
        return ( keys, values )

    def make_percentages( self, values ):
        """ Returns percentages needed by google-chart api for given list of values.
            Called by prep_data() """
        ( percentages, high_number ) = ( [], max(values) )
        high_number_divisor = high_number * .01
        for number in values:
            if high_number_divisor == 0:
                raw_percentage = 0
            else:
                raw_percentage = number / high_number_divisor
            rounded_raw_percentage = round( raw_percentage )
            percentages.append( rounded_raw_percentage )
        log.debug( u'in models.ChartMaker.make_percentages(); percentages, `%s`' % percentages )
        return percentages

    def make_ranges( self, percentages ):
        """ Returns ranges to be used by google-chart api.
            Called by prep_data() """
        high = max( percentages ) + 5
        low = min( percentages ) - 5
        ranges = [ low, high ]
        log.debug( u'in models.ChartMaker.make_percentages(); ranges, `%s`' % ranges )
        return ranges

    def prep_gchart_detail_url( self ):
        """ Assembles google-chart url for detail chart.
            Called by views.widget() """

        # <img src="http://chart.apis.google.com/chart?cht=lc
        #     &amp;chs=800x375
        #     &amp;chd=t:{% for percentage in detailchart_percentages %}{{percentage}}{% if not forloop.last %},{% endif %}{% endfor %}
        #     &amp;chds={{ detailchart_range.0 }},{{ detailchart_range.1 }}
        #     &amp;chtt={{ widget.title|urlencode }}
        #     &amp;chts=76A4FB,20
        #     &amp;chf=c,lg,0,76A4FB,1,ffffff,0|bg,s,EFEFEF
        #     &amp;chxt=x,x,x
        #     &amp;chxl=0:|{% for key in detailchart_keys %}{{ key }}|{% endfor %}1:|{% for value in detailchart_values %}{{ value|intcomma }}|{% endfor %}2:|{{ widget.key_label }} and {{ widget.value_label }}
        #     &amp;chxp=0|1|2,50
        #     &amp;chxs=2,76A4FB,12,0
        #     {% if data_index %}
        #     &amp;chm=c,FF0000,0,{{ data_index|add:"-1" }}.0,20.0 {% comment %} The 'add' template-filter is used because the url passes a 1-based index-number to the template, but the google-chart-api uses a zero-based index-number here. {% endcomment %}
        #     {% endif %}"
        #     alt="detail line-chart showing {{ widget.key_label }} and {{ widget.value_label }}" />

        pass

    # end class ChartMaker


class MinichartMaker( object ):
    """ Contains helpers for creating the minichart. """

    def extract_data_elements( self, lst ):
        """ Pulls out the middle four elements for crude thumbnail display.
            Called by SOMETHING. """
        one_third = int( round( len(lst)/3 ) )
        two_thirds = int( round( (2*len(lst))/3 ) )
        thumb_lst = [ lst[0], lst[one_third], lst[two_thirds], lst[-1] ]
        log.debug( u'in models.MinichartMaker.extract_data_elements(); list, `%s`; thumb_lst validity `%s`' % (lst, thumb_lst) )
        return thumb_lst

    # end class MinichartMaker


class ShibViewHelper( object ):
    """ Contains helpers for views.shib_login() """

    def check_shib_headers( self, request ):
        """ Grabs and checks shib headers, returns boolean.
            Called by views.shib_login() """
        shib_checker = ShibChecker()
        shib_dict = shib_checker.grab_shib_info( request )
        validity = shib_checker.evaluate_shib_info( shib_dict )
        log.debug( u'in models.ShibViewHelper.check_shib_headers(); returning validity `%s`' % validity )
        return ( validity, shib_dict )

    def build_response( self, request, validity, shib_dict, return_url ):
        """ Sets session vars and redirects to the request page,
              which will show the citation form on login-success, and a helpful error message on login-failure.
            Called by views.shib_login() """
        self.update_session( request, validity, shib_dict )
        return_response = HttpResponseRedirect( return_url )
        log.debug( u'in models.ShibViewHelper.build_response(); returning response' )
        return return_response

    def update_session( self, request, validity, shib_dict ):
        request.session[u'shib_login_error'] = validity  # boolean
        request.session[u'authorized'] = validity
        if validity:
            request.session[u'user_info'] = {
                u'name': u'%s %s' % ( shib_dict[u'firstname'], shib_dict[u'lastname'] ),
                u'email': shib_dict[u'email'],
                u'patron_barcode': shib_dict[u'patron_barcode'] }
            request.session[u'shib_login_error'] = False
        return

    # end class ShibViewHelper


class ShibChecker( object ):
    """ Contains helpers for checking Shib. """

    def __init__( self ):
        self.TEST_SHIB_JSON = os.environ.get( u'DSHBRD__TEST_SHIB_JSON', u'' )
        self.SHIB_REQUIRED_GROUP = os.environ[u'DSHBRD__SHIB_REQUIRED_GROUP']

    def grab_shib_info( self, request ):
        """ Grabs shib values from http-header or dev-settings.
            Called by models.ShibViewHelper.check_shib_headers() """
        shib_dict = {}
        if u'Shibboleth-eppn' in request.META:
            shib_dict = self.grab_shib_from_meta( request )
        else:
            if request.get_host() == u'127.0.0.1' and project_settings.DEBUG == True:
                shib_dict = json.loads( self.TEST_SHIB_JSON )
        log.debug( u'in models.ShibChecker.grab_shib_info(); shib_dict is: %s' % pprint.pformat(shib_dict) )
        return shib_dict

    def grab_shib_from_meta( self, request ):
        """ Extracts shib values from http-header.
            Called by grab_shib_info() """
        shib_dict = {
            u'eppn': request.META.get( u'Shibboleth-eppn', u'' ),
            u'firstname': request.META.get( u'Shibboleth-givenName', u'' ),
            u'lastname': request.META.get( u'Shibboleth-sn', u'' ),
            u'email': request.META.get( u'Shibboleth-mail', u'' ).lower(),
            u'patron_barcode': request.META.get( u'Shibboleth-brownBarCode', u'' ),
            u'member_of': request.META.get( u'Shibboleth-isMemberOf', u'' ) }
        return shib_dict

    def evaluate_shib_info( self, shib_dict ):
        """ Returns boolean.
            Called by models.ShibViewHelper.check_shib_headers() """
        validity = False
        if self.all_values_present(shib_dict) and self.brown_user_confirmed(shib_dict) and self.eresources_allowed(shib_dict):
            validity = True
        log.debug( u'in models.ShibChecker.evaluate_shib_info(); validity, `%s`' % validity )
        return validity

    def all_values_present( self, shib_dict ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        present_check = False
        if sorted( shib_dict.keys() ) == [u'email', u'eppn', u'firstname', u'lastname', u'member_of', u'patron_barcode']:
            value_test = u'init'
            for (key, value) in shib_dict.items():
                if len( value.strip() ) == 0:
                    value_test = u'fail'
            if value_test == u'init':
                present_check = True
        log.debug( u'in models.ShibChecker.all_values_present(); present_check, `%s`' % present_check )
        return present_check

    def brown_user_confirmed( self, shib_dict ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        brown_check = False
        if u'@brown.edu' in shib_dict[u'eppn']:
            brown_check = True
        log.debug( u'in models.ShibChecker.brown_user_confirmed(); brown_check, `%s`' % brown_check )
        return brown_check

    def eresources_allowed( self, shib_dict ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        eresources_check = False
        if self.SHIB_REQUIRED_GROUP in shib_dict[u'member_of']:
            eresources_check = True
        log.debug( u'in models.ShibChecker.eresources_allowed(); eresources_check, `%s`' % eresources_check )
        return eresources_check

    # end class ShibChecker
