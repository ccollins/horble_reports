import calendar
from datetime import *
from horble_reports import horble_report as hr
from horble_reports.tests.base_report_test import BaseReportTest
 
class ReportTest(BaseReportTest):     
    def test_split(self):
        data_set = [
                ['internet', 'apple'  , 1, 4],
                ['internet', 'ms'     , 1, 5],
                ['internet', 'apple'  , 2, 7],
                ['internet', 'linux'  , 2, 1],
                ['internet', 'ms'     , 2, 3],
                ['tv'      , 'sony'   , 1, 2],
                ['tv'      , 'toshiba', 1, 7],
                ['tv'      , 'jvc'    , 1, 4],
                ['tv'      , 'sony'   , 2, 8],
                ['tv'      , 'toshiba', 2, 3],
        ]

        (row_headers, column_headers, data_matrix) = hr._build_matrix(data_set, row_key=lambda x: (x[0], x[1]), column_key=lambda x:x[2], value_key=lambda x:x[3])

        (rh1, m1), (rh2, m2) = hr.split_matrix(key=lambda x: x[0], row_headers=row_headers, data_matrix=data_matrix)
        expected_rh1 = (('internet', 'apple'), ('internet', 'linux'), ('internet', 'ms'))
        expected_rh2 = (('tv', 'jvc'), ('tv', 'sony'), ('tv', 'toshiba'))
        expected_m1 = ((4,   7),
                       (0,   1),
                       (5,   3))
        expected_m2 = ((4,   0),
                       (2,   8),
                       (7,   3))
        
        self.assertEquals(expected_rh1, rh1)
        self.assertEquals(expected_rh2, rh2)
        self.assertEquals(expected_m1, m1)
        self.assertEquals(expected_m2, m2)     
        
    def test_join(self):
        rh1 = (('internet', 'apple'), ('internet', 'linux'), ('internet', 'ms'))
        rh2 = (('tv', 'jvc'), ('tv', 'sony'), ('tv', 'toshiba'))
        m1 = ((4,   7),
              (0,   1),
              (5,   3))
        m2 = ((4,   0),
              (2,   8),
              (7,   3))
              
        (row_headers, data_matrix) = hr.join_matrices((rh1, m1), (rh2, m2))
        expected_row_headers = (('internet', 'apple'), ('internet', 'linux'), ('internet', 'ms'), ('tv', 'jvc'), ('tv', 'sony'), ('tv', 'toshiba'))
        expected_data_matrix = ((4, 7),
                                (0, 1),
                                (5, 3),
                                (4, 0),
                                (2, 8),
                                (7, 3))
        self.assertEquals(row_headers, expected_row_headers)
        self.assertEquals(data_matrix, expected_data_matrix)
        
    def test_sum_groups(self):
        data_set = [
                ['internet', 'apple'  , 1, 4],
                ['internet', 'ms'     , 1, 5],
                ['internet', 'apple'  , 2, 7],
                ['internet', 'linux'  , 2, 1],
                ['internet', 'ms'     , 2, 3],
                ['tv'      , 'sony'   , 1, 2],
                ['tv'      , 'toshiba', 1, 7],
                ['tv'      , 'jvc'    , 1, 4],
                ['tv'      , 'sony'   , 2, 8],
                ['tv'      , 'toshiba', 2, 3],
        ]

        report = hr.report_builder(data_set=data_set, 
                              row_header_label=("Marketing", "Specialty"), 
                              row_key=lambda x:(x[0], x[1]), 
                              column_key=lambda x:x[2], 
                              value_key=lambda x:x[3],
                              header_converter=lambda i: calendar.month_abbr[i])
    
        report = report.sum_groups(group=lambda x: x[0], sum_label=('','Total'))

        expected_report = (
                ('Marketing', "Specialty", "Jan", "Feb"),
                ('internet' , 'apple'    ,  4   ,  7   ),
                ('internet' , 'linux'    ,  0   ,  1   ),
                ('internet' , 'ms'       ,  5   ,  3   ),
                (''         , 'Total'    ,  9   , 11   ),
                ('tv'       , 'jvc'      ,  4   ,  0   ),
                ('tv'       , 'sony'     ,  2   ,  8   ),
                ('tv'       , 'toshiba'  ,  7   ,  3   ),
                (''         , 'Total'    , 13   , 11   ),
        )
        
        self.assertEquals(expected_report, report.format())
        
    def test_merge_matrices(self):
        ch1 = ('marketing', 'jan', 'feb')
        rh1 = ('internet', 'tv')
        m1 = ((1, 2), (3, 4))
        
        ch2 = ('year to date',)
        rh2 = ('internet', 'tv')
        m2 = ((100,), (200,))
        
        expected_ch = ('marketing', 'jan', 'feb', 'year to date')
        expected_rh = ('internet', 'tv')
        expected_m = ((1, 2, 100), (3, 4, 200))
        (result_rh, result_ch, result_m) = hr.merge_matrices((rh1, ch1, m1), (rh2, ch2, m2))
        
        self.assertEquals(expected_ch, result_ch)
        self.assertEquals(expected_rh, result_rh)
        self.assertEquals(expected_m, result_m)

    def test_replace_into_tuple(self):
        t1 = (0, 1, 2, 3, 4, 5)
        self.assertEquals((0, 1, 2, 9, 4, 5), hr.replace_into_tuple(t1, 9, 3))
        self.assertEquals((9, 1, 2, 3, 4, 5), hr.replace_into_tuple(t1, 9, 0))
        self.assertEquals((0, 1, 2, 3, 4, 9), hr.replace_into_tuple(t1, 9, 5))
        self.assertEquals((0, 1, 2, 3, 4, 5, 9), hr.replace_into_tuple(t1, 9, 6))
            
    def test_prepend_column(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        column = (0, 0, 0)
        expected = ((0, 1, 2, 3), (0, 4, 5, 6), (0, 7, 8, 9))
        
        self.assertEquals(expected, hr.prepend_column(ds, column))
        self.assertEquals(ds, ((1, 2, 3), (4, 5, 6), (7, 8, 9)))
        
    def test_prepend_row(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        column = (0, 0, 0)
        expected = ((0, 0, 0), (1, 2, 3), (4, 5, 6), (7, 8, 9))
        
        self.assertEquals(expected, hr.prepend_row(ds, column))
        
    def test_append_column(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        column = (0, 0, 0)
        expected = ((1, 2, 3, 0), (4, 5, 6, 0), (7, 8, 9, 0))
        
        self.assertEquals(expected, hr.append_column(ds, column))
        
    def test_sum_columns(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        expected = (12, 15, 18)
        
        self.assertEquals(expected, hr.reduce_columns(ds, sum))
        
    def test_average_columns(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        expected = (4, 5, 6)
        
        self.assertEquals(expected, hr.reduce_columns(ds, lambda x: sum(x)/len(x)))
        
    def test_sum_rows(self):
        ds = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        expected = (6, 15, 24)
        
        self.assertEquals(expected, hr.reduce_rows(ds, sum))
        
    def test_build_matrix(self):
        data_set = [
             ['internet', 1, 4],
             ['internet', 2, 5],
             ['tv' , 1, 6],
             ['tv' , 2, 7],
        ]
         
        (row_headers, column_headers, data_matrix) = hr._build_matrix(data_set, row_key=lambda x: (x[0],), column_key=lambda x:x[1], value_key=lambda x:x[2])
        self.assertEquals((('internet',), ('tv',)), row_headers)
        self.assertEquals((1, 2), column_headers)
        expected_values = ((4, 5), (6, 7))
        
        self.assertEquals(expected_values, data_matrix)
        
    def test_build_matrix_tuple(self):
        data_set = [
                ['internet', 'apple'  , 1, 4],
                ['internet', 'ms'     , 1, 5],
                ['internet', 'apple'  , 2, 7],
                ['internet', 'linux'  , 2, 1],
                ['internet', 'ms'     , 2, 3],
                ['tv'      , 'sony'   , 1, 2],
                ['tv'      , 'toshiba', 1, 7],
                ['tv'      , 'jvc'    , 1, 4],
                ['tv'      , 'sony'   , 2, 8],
                ['tv'      , 'toshiba', 2, 3],
        ]

        (row_headers, column_headers, data_matrix) = hr._build_matrix(data_set, row_key=lambda x: (x[0], x[1]), column_key=lambda x:x[2], value_key=lambda x:x[3])
        self.assertEquals((('internet', 'apple'), ('internet', 'linux'), ('internet', 'ms'), ('tv', 'jvc'), ('tv', 'sony'), ('tv', 'toshiba')), row_headers)
        self.assertEquals((1, 2), column_headers)
        expected_values = ((4, 7),
                           (0, 1),
                           (5, 3),
                           (4, 0),
                           (2, 8),
                           (7, 3))

        self.assertEquals(expected_values, data_matrix)
        
    def test_transpose_tuple(self):
        data_set = [
                ['internet', 'apple'  , 1, 4],
                ['internet', 'ms'     , 1, 5],
                ['internet', 'apple'  , 2, 7],
                ['internet', 'linux'  , 2, 1],
                ['internet', 'ms'     , 2, 3],
                ['tv'      , 'sony'   , 1, 2],
                ['tv'      , 'toshiba', 1, 7],
                ['tv'      , 'jvc'    , 1, 4],
                ['tv'      , 'sony'   , 2, 8],
                ['tv'      , 'toshiba', 2, 3],
        ]
            
        expected_report = (
                ('Marketing', "Specialty", "Jan", "Feb"),
                ('internet' , 'apple'    , 4    , 7    ),
                ('internet' , 'linux'    , 0    , 1    ),
                ('internet' , 'ms'       , 5    , 3    ),
                ('tv'       , 'jvc'      , 4    , 0    ),
                ('tv'       , 'sony'     , 2    , 8    ),
                ('tv'       , 'toshiba'  , 7    , 3    ),
        )
            
        report = hr.report_builder(data_set=data_set, 
                              row_header_label=("Marketing", "Specialty"), 
                              row_key=lambda x:(x[0], x[1]), 
                              column_key=lambda x:x[2], 
                              value_key=lambda x:x[3],
                              header_converter=lambda i: calendar.month_abbr[i])
        self.assertEquals(expected_report, report.format())
            
    def test_transpose_missing(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 2, 7],
        ]    
         
        expected_report = (
            ('Marketing', "Jan", "Feb"),
            ('internet' , 4, 5),
            ('tv' , 0, 7),
        )
        
        self.assertEquals(expected_report, self.report_for(data_set).format())
        
    def test_transform_by_row_total(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]
        
        report = self.report_for(data_set)
        report.add_total_column() 
 
        expected_report = (
            ('Marketing', "Jan", "Feb", "Total"),
            ('internet' , 4, 5, 9 ),
            ('tv'       , 6, 7, 13),
        )
        
        self.assertEquals(expected_report, report.format())

    def test_transform_by_row_total_and_avg(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_total_column() 
        report.add_average_column()
        expected_report = (
            ('Marketing', "Jan", "Feb", "Total", "Average"),
            ('internet' , 4, 5, 9,  4.5),
            ('tv'       , 6, 7, 13, 6.5),
        )

        self.assertEquals(expected_report, report.format())

     
    def test_transform_by_row_average(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_average_column() 

        expected_report = (
            ('Marketing', "Jan", "Feb", "Average"),
            ('internet' , 4, 5, 4.5 ),
            ('tv'       , 6, 7, 6.5),
        )

        self.assertEquals(expected_report, report.format())
        
    def test_transform_by_column_total(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]
 
        report = self.report_for(data_set)
        report.add_total_row() 
    
        expected_report = (
            ('Marketing', "Jan",  "Feb" ),
            ('internet' , 4,  5 ),
            ('tv'       , 6,  7 ),
            ('Total'    , 10, 12)
        )
        
        self.assertEquals(expected_report, report.format())

    def test_transform_by_column_average(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_average_row() 

        expected_report = (
            ('Marketing', "Jan",  "Feb" ),
            ('internet' , 4,  5 ),
            ('tv'       , 6,  7 ),
            ('Average'    , 5, 6)
        )

        self.assertEquals(expected_report, report.format())
        
    def test_transform_by_column_total_and_avg(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_total_row() 
        report.add_average_row() 

        expected_report = (
            ('Marketing', "Jan",  "Feb" ),
            ('internet' , 4,  5 ),
            ('tv'       , 6,  7 ),
            ('Total'    , 10, 12),
            ('Average'    , 5, 6)            
        )

        self.assertEquals(expected_report, report.format())

    def test_transform_by_row_total_and_column_avg(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_total_column() 
        report.run_calculations()
        report.add_average_row() 

        expected_report = (
            ('Marketing', "Jan",  "Feb", "Total" ),
            ('internet' , 4,  5, 9  ),
            ('tv'       , 6,  7, 13 ),
            ('Average'    , 5, 6, 11)            
        )

        self.assertEquals(expected_report, report.format())
    
    def test_transform_by_row_total_and_column_total(self):
        data_set = [
            ['internet', 1, 4],
            ['internet', 2, 5],
            ['tv' , 1, 6],
            ['tv' , 2, 7],
        ]

        report = self.report_for(data_set)
        report.add_total_column() 
        report.run_calculations()
        report.add_total_row() 

        expected_report = (
            ('Marketing', "Jan",  "Feb", "Total" ),
            ('internet' , 4,  5, 9  ),
            ('tv'       , 6,  7, 13 ),
            ('Total'    , 10, 12, 22)            
        )

        self.assertEquals(expected_report, report.format())
        
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
             ('tv'       , 6,  7, 600 )          
         )
         
         self.assertEquals(expected_report, report3.format())
         
    def test_transpose_column(self):
        matrix = ((1, 2, 3, 4, 5),
                  (6, 7, 8, 9, 0),
                  (1, 2, 3, 4, 5))
                  
        self.assertEquals((1, 6, 1), hr.transpose_column(matrix, 0))
        self.assertEquals((2, 7, 2), hr.transpose_column(matrix, 1))
        self.assertEquals((3, 8, 3), hr.transpose_column(matrix, 2))
        self.assertEquals((4, 9, 4), hr.transpose_column(matrix, 3))
        self.assertEquals((5, 0, 5), hr.transpose_column(matrix, 4))