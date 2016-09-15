# -*- coding: utf-8 -*-
'''
This class provides functions to easily build SQL-Strings as well as SQL-Statements
for db2 and sqlite3.

@author: Moritz Kurt Heilemann
'''
from enum import Enum

class DatabaseType(Enum):
    db2 = 'db2'
    sqlite = 'sqlite'
    
# collection of reusable sql statement templates
class Statement(Enum):
    _insert_replace = 'INSERT OR REPLACE INTO {} {} VALUES {}'
    _insert_db2 = 'INSERT INTO {} {} VALUES {}'
    
    _select = 'SELECT {}'
    _from = ' FROM {}'
    _where = ' WHERE'
    _condition_equality = ' {} = ?'
    _condition_dif = ' {} != ?'
    _condition_like = ' {} like ?'
    _condition_greater_equal = ' {} >= ?'
    _condition_less_equal = ' {} <= ?'
    _and = ' AND'
    _order_by = ' ORDER BY {}'
    _maximum_rows_db2 = ' FETCH FIRST {} ROWS ONLY'
    _maximum_rows_sqlite = ' LIMIT {}'
    _uncommitted_read = ' WITH UR'
    
class SQLBuilder():
    
    def __init__(self, database_type):
        for db_type in DatabaseType:
            if database_type == db_type or database_type == db_type.value:
                # db type for used statements    
                self.db_type = db_type
        pass

    # sql builder is initialized if the type is set and valid
    def __is_initialized(self):
        return self.db_type != None
        
    def build_select_statement_dao(self, sql_dao):
        return self.build_select_statement(sql_dao.get_table(), sql_dao.get_columns_select(), sql_dao.get_columns_where(), sql_dao.get_where_condition_types(), sql_dao.get_max_rows(), sql_dao.get_columns_order())
    
    def build_insert_statement_with_info(self, stmt_info):
        return self.build_insert_statement(stmt_info.get_table(), stmt_info.get_columns_select(), stmt_info.set_where_condition_values())
    
    # mask some parameters for easier use
    def build_simple_select_statement(self, table, columns, condition_columns, condition_types):
        return self.build_select_statement(table, columns, condition_columns, condition_types, None, None)
    
    # builds a sql statement for db2 or sqlite
    # like 'SELECT * FROM VSTB0041 WHERE cond1 = ? AND cond2 = ? FETCH FIRST 100 ROWS ONLY'
    def build_select_statement(self, table, columns, conditions_columns, condition_types, maximum_rows, order_by_columns):
        # check if class is
        if not self.__is_initialized():
            raise Exception('Keinen Datenbanktyp zum SQL-Builder zugewiesen oder Typ nicht erkannt!')
        
        string = ''        
        # if there are columns, add them
        if columns and len(columns) > 0:
            string += Statement._select.value.format(', '.join(columns))
        # if not, use SELECT *
        else:
            string+= Statement._select.value.format('*')
            
        string += Statement._from.value.format(table)
        # if there is at least one condition
        if conditions_columns and len(conditions_columns) > 0:
            string += Statement._where.value
            # add the conditions
            for i in range(0, len(conditions_columns)):
                string += condition_types[i].format(conditions_columns[i])
                # if its not the last condition, add an "and" to the statement
                if i < (len(conditions_columns) - 1):
                    string += Statement._and.value

        # if there is at least one order by condition
        if order_by_columns and len(order_by_columns) > 0:
            string += Statement._order_by.value.format(', '.join(order_by_columns))
            
        # limit the output rows
        if maximum_rows:
            if self.db_type == DatabaseType.db2:
                string += Statement._maximum_rows_db2.value.format(maximum_rows)
            if self.db_type == DatabaseType.sqlite:
                string += Statement._maximum_rows_sqlite.value.format(maximum_rows)

        # add UNCOMMITTED READ: always!
        if self.db_type == DatabaseType.db2:
            string += Statement._uncommitted_read.value
            
        return string
            
    # builds an sql string for inserting or replacing (SQLITE ONLY!)
    def build_insert_statement(self, table, update_columns):
        # if self.db_type == DatabaseType.db2
        if not self.__is_initialized():
            raise Exception('Keinen Datenbanktyp zum SQL-Builder zugewiesen oder Typ nicht erkannt!')
        if self.db_type == DatabaseType.sqlite:
            string = Statement._insert_replace.value.format(table,'(' + ', '.join(update_columns) + ')', '(' + ', '.join(['?' for column in update_columns]) + ')')
        elif self.db_type == DatabaseType.db2:
            string = Statement._insert_db2.value.format(table,'(' + ', '.join(update_columns) + ')', '(' + ', '.join(['%s' for column in update_columns]) + ')')
        return string
    