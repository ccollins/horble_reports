import calendar
from datetime import *
from horble_reports import horble_report as hr
from horble_reports.tests.base_report_test import BaseReportTest

class MergeDifferentRowsTest(BaseReportTest):
    def test_merge_rows(self):
        rh1 = ('internet', 'tv')
        rh2 = ('internet', 'test', 'tv')
        
        expected_rows = ('internet', 'test', 'tv')
        result_rows = hr.merge_rows(rh1, rh2)
        self.assertEquals(expected_rows, result_rows)
        
    def test_merge_tuple_rows(self):
        rh1 = (('internet', 'a'), ('tv', 'b'))
        rh2 = (('internet', 'c'), ('test', 'a'), ('tv', 'b'))
        
        expected_rows = (('internet', 'a'), ('internet', 'c'), ('test', 'a'), ('tv', 'b'))
        result_rows = hr.merge_rows(rh1, rh2)
        self.assertEquals(expected_rows, result_rows)
        
    def test_merge_rows_diff(self):
        rh1 = ('internet', 'tv')
        rh2 = ('test', 'tv')

        expected_rows = ('internet', 'test', 'tv')
        result_rows = hr.merge_rows(rh1, rh2)
        self.assertEquals(expected_rows, result_rows)
        
    def test_merge_data(self):
        rh1 = ('internet', 'tv')
        rh2 = ('internet', 'test', 'tv')
        mrh = ('internet', 'test', 'tv')
        m1 = ((1, 2), (3, 4))
        m2 = ((100,), (300,), (200,))
        
        expected_m = ((1, 2, 100), (0, 0, 300), (3, 4, 200))
        result_data = hr.merge_data(m1, m2, mrh, rh1, rh2)
        
        self.assertEquals(expected_m, result_data)
    
    def test_merge_data_diff_rows(self):
        rh1 = ('internet', 'tv')
        rh2 = ('test', 'tv')
        mrh = ('internet', 'test', 'tv')
        m1 = ((1, 2), (3, 4))
        m2 = ((300,), (200,))

        expected_m = ((1, 2, 0), (0, 0, 300), (3, 4, 200))
        result_data = hr.merge_data(m1, m2, mrh, rh1, rh2)

        self.assertEquals(expected_m, result_data)
        
    def test_merge_matrices(self):
        ch1 = ('marketing', 'jan', 'feb')
        rh1 = ('internet', 'tv')
        m1 = ((1, 2), (3, 4))
    
        ch2 = ('year to date',)
        rh2 = ('internet', 'test', 'tv')
        m2 = ((100,), (300,), (200,))
    
        expected_ch = ('marketing', 'jan', 'feb', 'year to date')
        expected_rh = ('internet', 'test', 'tv')
        expected_m = ((1, 2, 100), (0, 0, 300), (3, 4, 200))
        (result_rh, result_ch, result_m) = hr.merge_matrices((rh1, ch1, m1), (rh2, ch2, m2))
    
        self.assertEquals(expected_ch, result_ch)
        self.assertEquals(expected_rh, result_rh)
        self.assertEquals(expected_m, result_m)
        
    def test_merge_matrices_diff_row(self):
        ch1 = ('marketing', 'jan', 'feb')
        rh1 = ('internet', 'tv')
        m1 = ((1, 2), (3, 4))

        ch2 = ('year to date',)
        rh2 = ('test', 'tv')
        m2 = ((300,), (200,))

        expected_ch = ('marketing', 'jan', 'feb', 'year to date')
        expected_rh = ('internet', 'test', 'tv')
        expected_m = ((1, 2, 0), (0, 0, 300), (3, 4, 200))
        (result_rh, result_ch, result_m) = hr.merge_matrices((rh1, ch1, m1), (rh2, ch2, m2))

        self.assertEquals(expected_ch, result_ch)
        self.assertEquals(expected_rh, result_rh)
        self.assertEquals(expected_m, result_m)
    
    def test_merge_reports(self):
           data_set1 = [
                ['internet', 1, 4],
                ['internet', 2, 5],
                ['tv' , 1, 6],
                ['tv' , 2, 7],
           ]
           report1 = self.report_for(data_set1)

           data_set2 = [
                ['internet', 'Year to Date', 500],
                ['test' , 'Year to Date', 550],
                ['tv' , 'Year to Date', 600],
           ]

           report2 = hr.report_builder(data_set=data_set2, 
                                  row_header_label=("Marketing",), 
                                  row_key=lambda x: (x[0],), 
                                  column_key=lambda x:x[1], 
                                  value_key=lambda x:x[2])

           report3 = report1 + report2

           expected_report = (
                ('Marketing', "Jan",  "Feb", "Year to Date" ),
                ('internet' , 4,  5, 500  ),
                ('test'     , 0,  0, 550  ),
                ('tv'       , 6,  7, 600 )          
           )

           self.assertEquals(expected_report, report3.format())