# -*- coding: utf-8 -*-

from dashboard_app.models import Widget, WidgetHelper
from django.test import TestCase

widget_helper = WidgetHelper()


class WidgetHelperTest(TestCase):
    """ Tests for models.WidgetHelper() """

    def test_process_data(self):
        """ Tests function that processes Widget() instance data. """
        ## init
        w = Widget()
        w.best_goal = 1
        w.data_points = "[ ('97/98', 183179), ('98/99', 178095), ('99/00', 172425), ('00/01', 159397), ('01/02', 168697), ('02/03', 191740), ('03/04', 188981), ('04/05', 188298), ('05/06', 198735), ('06/07', 183533) ]"
        processed_w = widget_helper.processData( w )
        ## baseline
        self.assertEqual(
            183179, processed_w.baseline_value )


        # expected = 183179
        # result = processed_w.baseline_value
        # self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        # best
        expected = 198735
        result = processed_w.best_value
        self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        # current
        expected = 183533
        result = processed_w.current_value
        self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        # trend value
        expected = -1
        result = processed_w.trend_direction
        self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        # trend color
        expected =  -1
        result = processed_w.trend_color
        self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        ## handling bug in 'best' when best is 'lower'...

        w2 = Widget()
        w2.best_goal = -1
        w2.data_points = "[ ('97/98', 183179), ('98/99', 178095), ('99/00', 172425), ('00/01', 159397), ('01/02', 168697), ('02/03', 191740), ('03/04', 188981), ('04/05', 188298), ('05/06', 198735), ('06/07', 183533) ]"
        processed_w2 = widget_helper.processData( w2 )

        # best
        expected = 159397
        result = processed_w2.best_value
        self.assertTrue( expected == result, '\n Expected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

        # end def test_processData()
