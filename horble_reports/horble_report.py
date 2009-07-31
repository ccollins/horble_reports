from sets import Set
    
def replace_into_tuple(matrix, value, position):
    return matrix[0:position] + (value,) + matrix[(position + 1):len(matrix)]
    
def _build_matrix(ds, row_key, column_key, value_key, default_value=0):
    row_headers = Set()
    column_headers = Set()
    value_dict = {}

    for row in ds:
        rk = row_key(row)
        row_headers.add(rk)
        ck = column_key(row)
        column_headers.add(ck)
        value_dict[(rk, ck)] = value_key(row)

    sorted_row_headers = tuple(sorted(row_headers))
    sorted_column_headers = tuple(sorted(column_headers))

    values = ()
    for srh in sorted_row_headers:
        row = ()
        for sch in sorted_column_headers:
            v = value_dict.get((srh,sch), default_value)
            row += (v,)
        values += (row,)

    return (sorted_row_headers, sorted_column_headers, values)

def merge_matrices((rh1, ch1, m1), (rh2, ch2, m2)):
    merged_rows = merge_rows(rh1, rh2)
    merged_data = merge_data(m1, m2, merged_rows, rh1, rh2)
    return merged_rows, ch1 + ch2, merged_data
    
def merge_data(m1, m2, mrh, rh1, rh2):
    lrh1 = list(rh1)
    lrh2 = list(rh2)
    data = []
    
    for rh in mrh:
        if lrh1.count(rh) > 0:
            m1d = m1[lrh1.index(rh)]
        else:
            m1d = tuple(map(lambda x:0, range(0, len(m1[0]))))
            
        if lrh2.count(rh) > 0:
            m2d = m2[lrh2.index(rh)]
        else:
            m2d = tuple(map(lambda x:0, range(0, len(m2[0]))))
      
        data.append(m1d + m2d)

    return tuple(data)
    
def merge_rows(rh1, rh2):
    return tuple(sorted(set(rh1 + rh2)))
        
def transpose_column(matrix, key):    
    return tuple([row[key] for row in matrix])

def reduce_rows(matrix, transform):
    return tuple([transform(row) for row in matrix])

def reduce_columns(matrix, transform):
    return tuple([transform(transpose_column(matrix, key)) for key in range(len(matrix[0]))])

def append_row(matrix, row):
    return matrix + (row,)
    
def append_column(matrix, column):
    for i in range(len(matrix)):
        matrix = replace_into_tuple(matrix, matrix[i] + (column[i],), i)
    return matrix

def prepend_row(matrix, row):
    return (row,) + matrix
    
def prepend_column(matrix, column):
    for i in range(len(matrix)):
        matrix = replace_into_tuple(matrix, (column[i],) + matrix[i], i)
    return matrix
    
# assumes the matrix is already sorted in an order that the key func will follow
def split_matrix(key, row_headers, data_matrix):    
    split_data = ()
    current_key = None
    
    for i, row in enumerate(row_headers):
        row_key = key(row)
        if row_key == current_key:
            matrix_tuple = replace_into_tuple(matrix_tuple, matrix_tuple[0] + (row,), 0)
            matrix_tuple = replace_into_tuple(matrix_tuple, matrix_tuple[1] + (data_matrix[i],), 1)
            if i == len(row_headers) - 1:
                split_data = split_data + (matrix_tuple,)            
        else:
            if current_key is not None:
                split_data = split_data + (matrix_tuple,)            
            matrix_tuple = ((row,), (data_matrix[i],))
        current_key = row_key
        
    return split_data
    
def join_matrices(*tuples):
    row_headers = ()
    data_matrix = ()
    for (rh, m) in tuples:
        row_headers = row_headers + rh
        data_matrix = data_matrix + m
    return row_headers, data_matrix

def append_report(r1, r2):
    rhs, m = join_matrices((r1.row_headers, r1.data_matrix), (r2.row_headers, r2.data_matrix))
    return Report(r1.row_header_label, rhs, r1.column_headers, m)
        
def report_builder(data_set, row_header_label, row_key, column_key, value_key, header_converter=str):
    row_headers, column_headers, data_matrix = _build_matrix(data_set, row_key, column_key, value_key)
    column_headers = tuple(map(header_converter, column_headers))
    
    return Report(row_header_label, row_headers, column_headers, data_matrix)
    
class Report(object):
    def __init__(self, row_header_label, row_headers, column_headers, data_matrix):
        self.row_header_label = row_header_label
        self.row_headers = row_headers
        self.column_headers = column_headers
        self.data_matrix = data_matrix
        self.calculations = ()
      
    def sum_groups(self, group, sum_label):
        reports = self.split_report(group)        
        for report in reports:
            report.add_total_row(sum_label)
            report.run_calculations()
        
        return reduce(append_report, reports)
        
    def split_report(self, group):
        split_matrices = split_matrix(key=group, row_headers=self.row_headers, data_matrix=self.data_matrix)
        reports = []
        for (rh, data) in split_matrices:
            reports.append(Report(self.row_header_label, rh, self.column_headers, data))
        return reports
            
    def add_total_row(self, header=("Total",)):
        self.add_row(header, sum)

    def add_average_row(self, header=("Average",)):
        self.add_row(header, lambda x: sum(x)*1.0/len(x))

    def add_row(self, label, func):
        new_row = reduce_columns(self.data_matrix, func)
        def calc():
            self.row_headers = append_row(self.row_headers, label)
            self.data_matrix = append_row(self.data_matrix, new_row)
        self.calculations += (calc,)

    def add_total_column(self, header="Total"):
        self.add_column(header, sum)

    def add_average_column(self):
        self.add_column("Average", lambda x: sum(x)*1.0/len(x))

    def add_column(self, label, func):
        new_column = reduce_rows(self.data_matrix, func)
        def calc():
            self.column_headers = append_row(self.column_headers, label)
            self.data_matrix = append_column(self.data_matrix, new_column)
        self.calculations += (calc,)

    def run_calculations(self):
        for c in self.calculations: c()
        self.calculations = []

    def format(self):
        self.column_headers = self.row_header_label + self.column_headers
        self.run_calculations()
        self.prepend_row_headers()
        self.data_matrix = prepend_row(self.data_matrix, self.column_headers)
        return self.data_matrix
        
    def prepend_row_headers(self):
        row_headers = [[] for i in range(len(self.row_header_label))]
        for row in self.row_headers:
            for key, header in enumerate(row):
                row_headers[key].append(header)

        row_headers.reverse()
        for row in row_headers:
            self.data_matrix = prepend_column(self.data_matrix, tuple(row))
        
    def __add__(self, other):
        return Report(self.row_header_label, *merge_matrices((self.row_headers, self.column_headers, self.data_matrix), 
                                                             (other.row_headers, other.column_headers, other.data_matrix)))
                                                             
    def __repr__(self):
        return "Data: %s, Columns: %s, Row: %s" % (repr(self.data_matrix), repr(self.column_headers), repr(self.row_headers))