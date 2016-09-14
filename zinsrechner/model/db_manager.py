# -*- coding: utf-8 -*-
'''
This class manages the access to the foreign db2 database DTLG or DDLG

@author: Moritz Kurt Heilemann
'''
from module.datasource.database_sql import DatabaseSQL
from module.datasource.sql_stmt_info import SQLStmtInfo
from zinsrechner.model.tables.zinsdaten import ZDATA
from zinsrechner.model import config_manager
from os import path as ospath

import copy



class DBManager():
        
    # init the manager
    def __init__(self):
        # create database access object
        # in DAO-Pattern this object is defined by an interface and given by a factory class
        self.errors = False
        self.database = DatabaseSQL(self.get_db_path())
        (error, data) = self.database.connect()
        if not error:
            (error, data) = self.database.init()
            if not error:
                config_manager.set_database(self)
                self.init_out = (False, None)
                return 
        self.errors = True
        self.init_out = (error, None)        
      
    def init_tables(self):
        (error, data) = self.database.connect() 
        if not error:
            # init other database functions if database is built
            (error, data) = self.database.init()
        
        return (error, data)

    def get_init_error(self):
        return self.init_out        
        
    def get_db_path(self):
        return ospath.join(config_manager.get('APP', 'path'), config_manager.get('DATA','path'))
                
    # returns TRUE if initialization was successful, FALSE otherwise
    def is_ready(self):
        return not self.errors

    def commit(self):
        self.database.commit()
        
    def connect(self):
        self.database.connect()

    def close(self):
        self.database.close()

    def create_static_table(self):
 
        self.database.create_table(ZDATA.NAME, ZDATA.COLUMNS_AND_TYPES)
        
#       save changes and close the connection
        self.database.commit()
            
    
    # Retrieve a table with it's columns
    def get_table(self, table):
        self.database.connect()
        (error, data) = self.database.select_all_rows(table)
        columns = self.database.get_columns(table)
        return (columns, data)
        
#    def test_sql(self, sql):
#        (error, data) = self.database.connect()
#        if not error:
#            data = self.database.test_execute(sql)
#            self.database.commit()
#            #self.database.close()
#            return data
#        else:
#            return None
            
    def insert_rows(self, vals):
        if self.database.connect():
            
            # Tabelle anlegen
#            print(self.database.execute('CREATE TABLE IF NOT EXISTS ' 
#                                  + ZDATA.NAME + ' ("' \
#                                  + ZDATA.COLUMN.DATUM.value + '" DATE, "' \
#                                  + ZDATA.COLUMN.RESTSCHULD.value + '" TEXT, "' \
#                                  + ZDATA.COLUMN.ZKOSTEN.value + '" TEXT, PRIMARY KEY("' \
#                                  + ZDATA.COLUMN.DATUM.value +'") )'))
            
#            # DatenTranferObjekt anreichern
#            stmt = SQLStmtInfo(SQLStmtInfo.TYPE.INSERT_UPDATE)
#            stmt.set_table(ZDATA.NAME)
#            stmt.set_insert_columns(ZDATA.COLUMNS)
#            for el in vals:
#                stmt.set_insert_values(el)
#            
#            # Tabelle befüllen
#            (error, data) = self.database.insert_update_with_info(stmt)


            (error, data) = self.database.list_insert_into(ZDATA.NAME, ZDATA.COLUMNS, vals)
            if error:
                print("bin hier")
                print(str(error))
            else:
                self.database.commit()
                
    def get_cost(self):
        stmt = SQLStmtInfo()
        stmt.set_table(ZDATA.NAME)
        stmt.set_columns_select([ZDATA.COLUMN.RESTSCHULD, ZDATA.COLUMN.ZKOSTEN])
        (error, data) = self.database.select_with_info(stmt)
        
        if data:
            return (error, data)
        else:           
            print("Tabelle ist leer")
            return (error, None)  
            
    def mytest(self, tableName):
        if self.database.connect():
            # Tabellendefinitionen
            col = ('SPALTE01', 'SPALTE02', 'SPALTE03')
            val = ("foo", "bar", "spam")
            
            # Tabelle anlegen
            self.database.execute('CREATE TABLE IF NOT EXISTS ' + str(tableName) + ' ("'+col[0]+'" TEXT, "'+col[1]+'" DATE, "'+col[2]+'" TEXT, PRIMARY KEY("SPALTE01", "SPALTE02") )')
            
            # DatenTranferObjekt anreichern
            stmt = SQLStmtInfo(SQLStmtInfo.TYPE.INSERT_UPDATE)
            stmt.set_table(tableName)
            stmt.set_insert_columns(col)
            stmt.set_insert_values(val)
            
            # Tabelle befüllen
            (error, data) = self.database.insert_update_with_info(stmt)
            if error:
                print(str(error))
            else:
                self.database.commit()

        
    def mytest_select(self, tableName):
        stmt = SQLStmtInfo()
        stmt.set_table(tableName)
        (error, data) = self.database.select_with_info(stmt)
        self.database.close()
        
        if data:
            return (error, self.database.get_columns(tableName), data)
        else:           
            print("Tabelle ist leer")
            return (error, None, None)          

            
    # get data with known max rows 
    def select_data(self, stmt_info):
        error = True
        if self.database.connect():
            stmt_info.format_select_where_columns('"')
            stmt_info.format_order_by_columns('"')
            (error, data) = self.database.select_with_info(stmt_info)
            if stmt_info.is_select_all():
                columns = self.database.get_columns(stmt_info.get_table())
            else:
                # remove ""
                columns = [column[1:-1] for column in stmt_info.get_columns_select()]
            self.database.close()
        return (error, columns, data)  
        
    def next_row(self, cursor):
        return self.database.next_row(cursor)
        
    def select_data_cursor(self, stmt_info):
        if self.database.connect():
            stmt_info.format_select_where_columns('"')
            stmt_info.format_order_by_columns('"')
            (error, cursor) = (True, None)
            
            copy_stmt = copy.deepcopy(stmt_info)
            copy_stmt.set_columns_order([])         
            copy_stmt.set_columns_select(['COUNT(*)'])
            # get the result as a cursor
            (error, count_result) = self.database.select_with_info(copy_stmt)
            if count_result and len(count_result) > 0:
                row_count = count_result[0][0]   
                row_count = min(row_count, stmt_info.get_max_rows())
            else:
                row_count = 0            
                
            if row_count > 0:
                (error, cursor) = self.database.select_cursor_with_info(stmt_info)
            
            if stmt_info.is_select_all():
                columns = self.database.get_columns(stmt_info.get_table())
            else:
                # remove ""
                columns = [column[1:-1] for column in stmt_info.get_columns_select()]
        return (error, columns, cursor, row_count)      
        
    def insert_update_data(self, stmt_info):
        if self.database.connect():
            stmt_info.format_insert_columns(r'"')            
            (error, data) = self.database.insert_update_with_info(stmt_info)
            self.database.commit()
            return True
        return False
        
    def insert_into_error_table(self, table, method, einst_zp, xml_position, error_type, error, entity, attr, ):
        self.database.execute('INSERT OR REPLACE INTO '+table+' VALUES ('+method+', '+einst_zp+', '+xml_position+', '+error_type+', '+error+', '+entity+', '+attr+', '++')')
        
    # NOTE: only for expensive operations!
    def execute(self, statement):
        self.database.execute(statement)

        