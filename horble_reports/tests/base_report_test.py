import calendar
from horble_reports import horble_report as hr

class BaseReportTest(TestCase):
    def report_for(self, data_set):
        return report_builder(data_set=data_set, 
                              row_header_label=("Marketing",), 
                              row_key=lambda x: (x[0],), 
                              column_key=lambda x:x[1], 
                              value_key=lambda x:x[2],
                              header_converter=lambda i: calendar.month_abbr[i])