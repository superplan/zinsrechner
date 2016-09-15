# -*- coding: utf-8 -*-
'''
Handles the direct access of a .db sql source file.
It provides functions to connect, close and commit to the database.
It handles incoming and outcoming data with view and manipulation Statement.

@author: Moritz Kurt Heilemann
'''
import sqlite3 as sql
import datetime
from enum import Enum
from datasource.sql_builder import SQLBuilder

# collection of reusable sql statement templates
class Statement(Enum):
    # manipulation    
    create_table = 'CREATE TABLE IF NOT EXISTS {} ({})'    
    create_table_config = 'CREATE TABLE IF NOT EXISTS CONFIG(date TIMESTAMP)' 
    insert_into = 'INSERT INTO {} {} VALUES {}'
    delete_all_rows = 'DELETE FROM {}'
    drop_table = 'DROP TABLE IF EXISTS {}'

    # view    
    select_all_rows = 'SELECT * FROM {}'
    select_rows_like = 'SELECT * FROM {} WHERE {} LIKE "%{}%"'
    select_columns_rows = 'SELECT {} FROM {}'
    select_columns_rows_where = 'SELECT {} FROM {} WHERE {} = "{}"'
    select_columns_rows_like = 'SELECT {} FROM {} WHERE {} LIKE "%{}%"'
    
    # check db state
    table_exist = 'SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'
    column_names = 'PRAGMA table_info({})'
    table_names = 'SELECT name FROM sqlite_master'

class DatabaseSQL():
    
    # stores all table names
    table_names = []
    # stores all tables with its column names
    table_columns = {}    
    # first column of tables
    FIRST_COLUMN = 0    
    
    # sqlite date formats
    DATE_FORMAT_1 = '%Y-%m-%d %H:%M:%S' 
    DATE_FORMAT_2 =  '%Y-%m-%d %H:%M:%S.%f'
    
    # Timeout für die Rückmeldezeit auf eine SQL-Anfrage in Sekunden
    TIMEOUT_IN_S = 10
    
    # constructor
    def __init__(self, path):        
        # save path to db
        self.path = path
        self.builder = SQLBuilder('sqlite')
        
    def str_to_date(string):
        
        # if its the first version
        if len(string) == 19:
            return datetime.datetime.strptime(string, DatabaseSQL.DATE_FORMAT_1) 
        elif len(string) == 26:
            return datetime.datetime.strptime(string, DatabaseSQL.DATE_FORMAT_2) 
        
        raise Exception('Datum-String {} kann nicht konvertiert werden!'.format(string))
        
    def date_to_str(date):
        return date.strftime(DatabaseSQL.DATE_FORMAT_2)

    # defined init function to handle other initial processes
    # 1. save columns of tables        
    def init(self):
        # retrieve needed information
        (error, data) = self.__update_table_names()
        if not error:
            (error, data) = self.__update_columns()
            if not error:
                return (False, True)
        return (error, None)
        
    
    # private functions
    def __execute(self, command):
        try:
            print(command)
            return (False, self.connection.execute(command))
        except Exception as e:
            return ('Beim Ausführen des Kommandos "{}" auf der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(command, self.path, repr(e)), None)          
            
    def __select(self, command):
        try:
            cursor = self.connection.cursor()
            cursor.execute(command)
            print(command)
            return (False, cursor.fetchall())
        except Exception as e:
            # if anything bad happens
            return ('Beim Ausführen des SELECT-Befehls "{}" auf der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(command, self.path, repr(e)), None)
        
    def __select_prepared_statement_cursor(self, statement, tuples):
        try:
            cursor = self.connection.cursor()
            print(statement+ ' '+str(tuples))        
            cursor.execute(statement, tuples)
            return (None, cursor)     
        except Exception as e:
            return ('Beim Ausführen des SELECT-Befehls "{}" mit den Werten "{}" auf der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(statement, tuples, self.path, repr(e)), None)
        
    def __select_prepared_statement(self, statement, tuples):
        try:
            cursor = self.connection.cursor()
            print(statement+ ' '+str(tuples))        
            cursor.execute(statement, tuples)
            return (False, cursor.fetchall())     
        except Exception as e:
            return ('Beim Ausführen des SELECT-Befehls "{}" mit den Werten "{}" auf der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(statement, tuples, self.path, repr(e)), None)
            
    def __execute_prepared_statement(self, statement, tuples):
        try:
            print(statement + ' '+str(tuples))        
            return (False, self.connection.execute(statement, tuples))
        except Exception as e:
            return ('Beim Ausführen des Kommandos "{}" mit den Werten "{}" auf der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(statement, tuples, self.path, repr(e)), None)
        
    # creates a list of placeholders, like (?,?,?)
    def __create_statement_placeholder(self, number):
        return '(' + ','.join(['?' for x in range(0, number)])+')'
            
    # converts the column list string from sqllite to a python list
    def __convert_sql_schema_to_column_list(self, schema):
        return [attribute[1] for attribute in schema]
        
    # retrieve needed information
    def __update_columns(self):
        try:
            # clear dictionary
            self.table_columns = {}       
            # for each table
            for table in self.table_names:
                # store column information
                cursor = self.connection.cursor()
                cursor.execute(Statement.column_names.value.format(table))
                # scan tables for columns
                self.table_columns[table] = self.__convert_sql_schema_to_column_list(cursor.fetchall())
            return (False, True)
        except Exception as e:
            return (repr(e), None)
        
    # save all table names of this database
    def __update_table_names(self):
        try:
            # clear list
            self.table_names = []          
            # select all table names
            cursor = self.connection.cursor()
            cursor.execute(Statement.table_names.value)
            # store the names in the local var, only the first column (name) is needed
            self.table_names = [table_name[self.FIRST_COLUMN] for table_name in cursor.fetchall()]
            return (False, True)
        except Exception as e:
            return (repr(e), None)
        
    # public functions
        
    # CONNECTION-MANAGEMENT and VALIDATION
    # check if db is connected to the db and functional
    def is_connected(self):
        try:
            self.connection.execute(Statement.table_names.value)
        except:
            return False
        else:
            return True
    # connect to the db
    def connect(self):
        try:
            self.connection = sql.connect(self.path, timeout=self.TIMEOUT_IN_S)
            #print('Datenbank geöffnet in Thread ' + str(id(self)))
            return (False, True)
        except Exception as e:
            return ('Beim Verbindungsaufbau mit der Datenbank "{}" ist ein Fehler aufgetreten. {}'.format(self.path, repr(e)), None)
        
    # commit changes to the db
    def commit(self):
        try:
            
            return (False, self.connection.commit())
        except Exception as e:
            return ('Fehler beim Commit-Vorgang. {}'.format(repr(e)), None)
    
    # close the database connection, uncommitted changes will be reverted
    def close(self):
        self.connection.close()
        #print('Datenbank geschlossen in Thread ' + str(id(self)))

    # checks if table exists in this db
    def table_exists(self, table):
        return self.__select(Statement.table_exist.value.format(table))[1]
        
    # VIEW
    # returns all columns of the given table
    def get_columns(self, table):
        if table in self.table_columns:
            return self.table_columns[table]
        # the table didn't exist!
        else:
            # 'Die Datenbank "{}" enthält keine Tabelle namens "{}"'.format(self.path, table)
            return []
    # direct execute to the sql database without error handling
    def test_execute(self, statement):
        cursor = self.connection.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
        
    # selects all rows from a table
    def select_all_rows(self, table):
        return self.__select(Statement.select_all_rows.value.format(table))
    
    # NOTE: it's not clean to code using this function! 
    def select(self, statement_string):
        return self.__select(statement_string)
        
    def execute(self, statement_string):
        self.connection.execute(statement_string)
        
    def select_with_info(self, stmt_info):
        statement = self.builder.build_select_statement(stmt_info.get_table(), stmt_info.get_columns_select(), stmt_info.get_columns_where(), stmt_info.get_where_condition_types(), stmt_info.get_max_rows(), stmt_info.get_columns_order())
        return self.__select_prepared_statement(statement, tuple(stmt_info.get_where_condition_values()))
        
    def select_cursor_with_info(self, stmt_info):
        statement = self.builder.build_select_statement(stmt_info.get_table(), stmt_info.get_columns_select(), stmt_info.get_columns_where(), stmt_info.get_where_condition_types(), stmt_info.get_max_rows(), stmt_info.get_columns_order())
        return self.__select_prepared_statement_cursor(statement, tuple(stmt_info.get_where_condition_values()))
        
    def insert_update_with_info(self, stmt_info):
        statement = self.builder.build_insert_statement(stmt_info.get_table(), stmt_info.get_insert_columns())
        return self.__execute_prepared_statement(statement, tuple(stmt_info.get_insert_values()))
    # fetches the content of the next row of the given cursor
    def next_row(self, cursor):
        return cursor.fetchone()        
        
    # MANIPULATION
    # inserts a list of tuples into the db
    # data has to have a specific structure
    def list_insert_into(self, table, columns, data):
        cursor = self.connection.cursor()
        placeholder = self.__create_statement_placeholder(len(columns))
        for items in data:  
            try:
                cursor.execute(Statement.insert_into.value.format(table, '', placeholder), tuple(items))
            except Exception as e:
                return ('Fehler beim Einfügen des Datansatzes {} in die Tabelle {}. {}'.format(items, table, repr(e)), None)
        return (False, True)
        
    # deletes a table
    def drop_table(self, table):
        # drop table            
        return self.__execute(Statement.drop_table.value.format(table))
        
    # create a table with the given columns and ranges
    def create_table(self, table, columns_and_ranges):
        # drop table if it exists
        (error, result) = self.drop_table(table)
        if not error:
            # create table
            (error, result) = self.__execute(Statement.create_table.value.format(table, columns_and_ranges))
            if not error:
                # store table names and columns
                (error, result) = self.__update_table_names()
                if not error:
                    (error, result) = self.__update_columns()
        
        return (error, None)