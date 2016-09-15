# -*- coding: utf-8 -*-
'''
This class provides functions to easily build SQL-Strings as well as SQL-Statements
for db2 and sqlite3.

@author: Moritz Kurt Heilemann
'''
import copy
from enum import Enum    

class SQLStmtInfo(): 
    class TYPE(Enum):
        SELECT = 1
        INSERT = 2
        INSERT_UPDATE = 3
        UPDATE = 4
        DELETE = 5
    
    def __init__(self, stmttype=TYPE.SELECT, table=None, columns_select=[], **kwargs):
        # statement type of this sql object
        # only SELECT statements are possible (now)        
        self.stmt_type = stmttype
        # like DB2.VSTB0041
        self.table = table
        # EINST_ZP
        self.columns_select = columns_select
        # EINST_ZP
        self.columns_where = []
        # {column} >= ? {value}
        self.where_condition_types = []
        # value of thing above
        self.where_condition_values = []
        # EINST_ZP ASC
        self.columns_order = []
        # LIMIT to 10 rows
        self.max_rows = 0
        
        # INSERT / UPDATE
        self.insert_columns = []
        self.insert_values = []
        
        # if data is given within the constructor
        if 'conditions' in kwargs:
            tuples = kwargs['conditions']
            for tup in tuples:
                self.add_where_condition(*tup)
            
        
    # GET/SET-methods
    def get_table(self):
        return self.table
    def get_columns_select(self):
        return self.columns_select
    def get_columns_where(self):
        return self.columns_where
    def get_where_condition_types(self):
        return self.where_condition_types
    def get_where_condition_values(self):
        return self.where_condition_values
    def get_columns_order(self):
        return self.columns_order
    def get_max_rows(self):
        return self.max_rows
    def get_insert_columns(self):
        return self.insert_columns
    def get_insert_values(self):
        return self.insert_values
    def set_table(self, table):
        self.table = table
    def set_columns_select(self, columns_select):
        self.columns_select = self.convert_enum(list(columns_select))
    def set_columns_where(self, columns_where):
        self.columns_where = self.convert_enum(list(columns_where))
    def set_where_condition_types(self, where_condition_types):
        self.where_condition_types = self.convert_enum(list(where_condition_types))
    def set_where_condition_values(self, where_condition_values):
        self.where_condition_values = self.convert_enum(list(where_condition_values))
    def set_columns_order(self, columns_order):
        self.columns_order = self.convert_enum(list(columns_order))
    def set_max_rows(self, max_rows):
        self.max_rows = max_rows
    def set_insert_columns(self, insert_cols):
        self.insert_columns = self.convert_enum(list(insert_cols))
    def set_insert_values(self, insert_vals):
        self.insert_values = self.convert_enum(list(insert_vals))
        
        
    def __format_slash(self, string):
        return self.parenthesis + string + self.parenthesis
        
    def __replace(self, string):
        return string.replace('-', '_')
        
    # comfort functions
    # EINST_ZP >= ? (value)
    def add_where_condition(self, column_name, condition_type, condition_value):
        self.columns_where.append(column_name)
        self.where_condition_types.append(condition_type)
        self.where_condition_values.append(condition_value)
        
    def format_select_where_columns(self, parenthesis):
        self.parenthesis = parenthesis
        for i in range(0, len(self.columns_select)):
            self.columns_select[i] = self.__format_slash(self.columns_select[i])
        for i in range(0, len(self.columns_where)):
            self.columns_where[i] = self.__format_slash(self.columns_where[i])

    def format_order_by_columns(self, parenthesis):
        self.parenthesis = parenthesis
        for i in range(0, len(self.columns_order)):
            self.columns_order[i] = self.__format_slash(self.columns_order[i])
            
    def format_insert_columns(self, parenthesis):
        self.parenthesis = parenthesis
        for i in range(0, len(self.insert_columns)):
            self.insert_columns[i] = self.__format_slash(self.insert_columns[i])
            
    def minus_to_underline_select_where(self):
        for i in range(0, len(self.columns_select)):
            self.columns_select[i] = self.__replace(self.columns_select[i])
        for i in range(0, len(self.columns_where)):
            self.columns_where[i] = self.__replace(self.columns_where[i])
            
    def minus_to_underline_order_by_columns(self):
        for i in range(0, len(self.columns_order)):
            self.columns_order[i] = self.__replace(self.columns_order[i])
            
    def set_where_column(self, column, value, nr):
        count = 0
        for i in range(0, len(self.columns_where)):
            if self.columns_where[i] == column:
                count += 1
                # if the column is found and it the correct count
                if count == nr:
                    self.where_condition_values[i] = value
                    return True
        # if the column is not found
        return False
    def get_value_of_column(self, column, nr):
        count = 0
        for i in range(0, len(self.columns_where)):
            if self.columns_where[i] == column:
                count += 1
                # if the column is found and it the correct count
                if count == nr:
                    return self.where_condition_values[i]
        # if the column is not found
        return False
        
    def get_value_of_column_with_type(self, column, _type, nr):
        count = 0
        for i in range(0, len(self.columns_where)):
            if self.columns_where[i] == column and _type == self.where_condition_types[i]:
                count += 1
                # if the column is found and it the correct count
                if count == nr:
                    return self.where_condition_values[i]
        # if the column is not found
        return False
        
    def get_values_of_column(self, column, max_columns):
        index = 0
        columns = []
        while True:
            index += 1
            tmp = self.get_value_of_column(column, index)
            if tmp:
                columns.append(tmp)
            else:
                return columns
                
    def convert_enum(self, _list):
        """Wenn die angegebene Liste Enum-Variablen enthält, 
        werden die Inhalte dieser ausgelesen und gespeichert"""
        for i in range(0, len(_list)):
            # var.value ist der Zugriff auf den Inhalt eines Enum-Feldes
            if hasattr(_list[i], 'value'):
                _list[i] = _list[i].value
        return _list
                
    def create_copy(self):
        return copy.deepcopy(self)
        
    # checks if the statement uses the * operator to select all rows
    def is_select_all(self):
        return self.columns_select == None or len(self.columns_select) < 1 or self.columns_select[0] == '*' 
        
    def is_select(self):
        return self.stmt_type == self.TYPE.SELECT