# -*- coding: utf-8 -*-

from dashboard_app.models import Widget, WidgetHelper, MinichartMaker
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


class MinichartMakerTest(TestCase):
    """ Tests for non-django models.MinichartMaker() """

    def test_extract_minichart_data(self):
        """ Tests the four expected datapoints. """
        minichart_maker = MinichartMaker()
        data_points = '[ {"97/98": 183179}, {"98/99": 178095}, {"99/00": 172425}, {"00/01": 159397}, {"01/02": 168697}, {"02/03": 191740}, {"03/04": 188981}, {"04/05": 188298}, {"05/06": 198735}, {"06/07": 183533} ]'
        self.assertEqual(
            u'foo', minichart_maker.extract_minichart_data( json.loads(data_points) )
            )
