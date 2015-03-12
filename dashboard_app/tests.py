# -*- coding: utf-8 -*-

from dashboard_app.models import Widget, WidgetHelper, ChartMaker, MinichartMaker
from django.test import TestCase

widget_helper = WidgetHelper()


class WidgetHelperTest(TestCase):
    """ Tests for non-django models.WidgetHelper() """

    def test_process_data(self):
        """ Tests process_data(). """
        w = Widget()
        w.best_goal = 1  # best is higher -- think higher circulation being good
        w.data_points = '[ {"97/98": 183179}, {"98/99": 178095}, {"99/00": 172425}, {"00/01": 159397}, {"01/02": 168697}, {"02/03": 191740}, {"03/04": 188981}, {"04/05": 188298}, {"05/06": 198735}, {"06/07": 183533} ]'
        processed_w = widget_helper.process_data( w )
        ## baseline
        self.assertEqual( 183179, processed_w.baseline_value )
        ## best
        self.assertEqual( 198735, processed_w.best_value )
        ## current
        self.assertEqual( 183533, processed_w.current_value )
        ## trend direction
        self.assertEqual( -1, processed_w.trend_direction )
        ## trend color
        self.assertEqual( -1, processed_w.trend_color )
        ## tests 'best' when best is 'lower', think missing books
        w2 = Widget()
        w2.best_goal = -1
        w2.data_points = '[ {"97/98": 183179}, {"98/99": 178095}, {"99/00": 172425}, {"00/01": 159397}, {"01/02": 168697}, {"02/03": 191740}, {"03/04": 188981}, {"04/05": 188298}, {"05/06": 198735}, {"06/07": 183533} ]'
        processed_w2 = widget_helper.process_data( w2 )
        ## best
        self.assertEqual( 159397, processed_w2.best_value )

    # end class WidgetHelperTest


class ChartMakerTest(TestCase):
    """ Tests for non-django models.ChartMaker() """

    def test_make_percentages(self):
        """ Tests example lists. """
        cm = ChartMaker()
        lst = [ 1, 2, 3, 4, 5, 6, 7 ]
        self.assertEqual(
            [ 14.0, 29.0, 43.0, 57.0, 71.0, 86.0, 100.0 ], cm.make_percentages(lst) )

    # end class ChartMakerTest


class MinichartMakerTest(TestCase):
    """ Tests for non-django models.MinichartMaker() """

    def test_extract_minichart_data(self):
        """ Tests the four expected datapoints. """
        minichart_maker = MinichartMaker()
        lst = [ 1, 2, 3, 4, 5, 6, 7 ]
        self.assertEqual(
            [ 1, 3, 5, 7 ], minichart_maker.extract_data_elements(lst) )
        lst = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]
        self.assertEqual(
            [ 1, 4, 7, 10 ], minichart_maker.extract_data_elements(lst) )
        lst = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ]
        self.assertEqual(
            [ 1, 4, 8, 11 ], minichart_maker.extract_data_elements(lst) )
        lst = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ]
        self.assertEqual(
            [ 1, 5, 9, 12 ], minichart_maker.extract_data_elements(lst) )

    # end class MinichartMakerTest
