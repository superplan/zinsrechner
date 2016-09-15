# -*- coding: utf-8 -*-
'''
Handles the connection of a db2 database

@author: Moritz Kurt Heilemann
'''
import ibm_db
import datetime
from module.datasource.sql_builder import SQLBuilder
from enum import Enum

class StoredProcedure(Enum):
    get_methods = 'DB2.VSUD1604'

class DatabaseDB2():
    # maximum row count received from the db
    MAXIMUM_ROWS = 10
    
    # Host date format
    DATE_FORMAT = '%Y-%m-%d-%H.%M.%S.%f'
    
    __connections = []
    
    def __init__(self, database, user, password):
        # save credentials
        self.user = user
        self.password = password
        self.database = database
        self.builder = SQLBuilder('db2')
        
    def str_to_date(string):
        return datetime.datetime.strptime(string, DatabaseDB2.DATE_FORMAT)
        
    def date_to_str(date):
        return date.strftime(DatabaseDB2.DATE_FORMAT)

        
    # executes a prepared statement ONLY with the following values
    def __execute(self, prepared_statement):
        try:
            ibm_db.execute(prepared_statement)
            return (False, prepared_statement)
        except Exception as e:
            return ('Fehler beim Ausführen des Statements {} auf der Datenbank {}! {}'.format(prepared_statement, self.database, repr(e)), None)
        
    # creates a prepared statement for a specific db connection
    def __create_prepared_statement(self, statement):
        print(statement)
        try:
            return (False, ibm_db.prepare(self.db_connection, statement))
        except Exception as e:
            return ('Fehler beim Erstellen des Prepared Statements {} auf der Datenbank {}! {}'.format(statement, self.database, repr(e)), None)
            
    # binds any value to the prepared statement
    def __bind_parameters(self, prepared_statement, values):
        try:
            for i in range (0, len(values)):
                ibm_db.bind_param(prepared_statement, i + 1, values[i])
            print('Gebundene Parameter: '+str(values))
            return (False, True)
        except Exception as e:
            return ('Fehler beim Binden der Parameter an das Prepared Statement {} mit den Werten {}! {}'.format(prepared_statement, str(values), repr(e)), None)
        
    # calls a stored procedure
    def __call_procedure(self, procedure_name, parameter_tuple):
        try:
            print(str(procedure_name) + ' ' + str(parameter_tuple))
            result_tuple = ibm_db.callproc(self.db_connection, procedure_name, parameter_tuple)
            return (False, result_tuple)
        except Exception as e:
            return ('Fehler beim Ausführen des Prepared Statements {} mit den Werten {} auf der Datenbank {}! {}'.format(procedure_name, str(parameter_tuple), str(self.database), repr(e)), None)

        
    # executes a statement and encapsulates its result in an python object
    def __get_result(self, prepared_statement):
        result = []
        (error, stmt) = self.__execute(prepared_statement)
        # if True was given: data can be accessed via the prepared statement
        if not error:
            row = ibm_db.fetch_tuple(prepared_statement)
            while row:
                # add each row to the list
                result.append(row)
                row = ibm_db.fetch_tuple(prepared_statement)
        # return the full answer from the db
        return (error, result)
        
    # connect to the database
    def connect(self):
        try:
            self.db_connection = ibm_db.pconnect(self.database, self.user, self.password)
            return (None, True)
        except Exception as e:
            return ('Fehler beim Herstellen der Verbindung zum DB2-Server! (Nutzer: {}, Datenbank: {}) {}'.format(self.user, self.database, repr(e)), False)
            
    # closes the db2 connection
    def close(self):
        try:
            ibm_db.close(self.db_connection)
            return (None, True)
        except Exception as e:
            return ('Fehler beim Schließen der Verbindung zum DB2-Server! (Nutzer: {}, Datenbank: {}) {}'.format(self.user, self.database, repr(e)), False)
            
    # fetches the content of the next row of the given cursor
    def next_row(self, cursor):
        return ibm_db.fetch_tuple(cursor)
        
    def select_with_info(self, stmt_info):
        statement = self.builder.build_select_statement(stmt_info.get_table(), stmt_info.get_columns_select(), stmt_info.get_columns_where(), stmt_info.get_where_condition_types(), stmt_info.get_max_rows(), stmt_info.get_columns_order())
        (error, prepared_statement) = self.__create_prepared_statement(statement)
        if error:
            return (error, None)
        (error, data) = self.__bind_parameters(prepared_statement, stmt_info.get_where_condition_values())
        if error:
            return (error, None)
        return self.__get_result(prepared_statement)
        
    def select_cursor_with_info(self, stmt_info):
        statement = self.builder.build_select_statement(stmt_info.get_table(), stmt_info.get_columns_select(), stmt_info.get_columns_where(), stmt_info.get_where_condition_types(), stmt_info.get_max_rows(), stmt_info.get_columns_order())
        (error, prepared_statement) = self.__create_prepared_statement(statement)
        self.__bind_parameters(prepared_statement, stmt_info.get_where_condition_values())        
        return self.__execute(prepared_statement)
           
    # select specific rows with conditions
    def select(self, table, columns, condition_columns, condition_types, values, max_rows, order_by_columns):
        (error, prepared_statement) = self.__create_prepared_statement(self.builder.build_select_statement(table, columns, condition_columns, condition_types, max_rows, order_by_columns))
        self.__bind_parameters(prepared_statement, values)        
        return self.__get_result(prepared_statement)
        
    # do the same thing as with "select" but return the cursor, for performance reasons
    def select_cursor(self, table, columns, condition_columns, condition_types, values, max_rows, order_by_columns):
        (error, prepared_statement) = self.__create_prepared_statement(self.builder.build_select_statement(table, columns, condition_columns, condition_types, max_rows, order_by_columns))
        self.__bind_parameters(prepared_statement, values)        
        return self.__execute(prepared_statement)
            
    # select all rows of a table
    def select_all(self, table):
        return self.select(table, ['*'], [], [], [], self.MAXIMUM_ROWS, [])
        
    '''
    Eingabe:                                          
    FKT-SL             CHAR(1),                       
    VERARB-ZT-SL       CHAR(5),                       
    ZIEL-SYSTEM        CHAR(10),                      
    VERW-SYS-SL        CHAR(2),                       
    SN-SERVICE-1       CHAR(8),                       
    SN-SERVICE-2       CHAR(8),                       
    SN-SERVICE-3       CHAR(8),                       
    SN-METHOD          CHAR(12),     
    VNR                                      
    EINST-ZP-VON       TIMESTAMP,                     
    EINST-ZP-BIS       TIMESTAMP,                     
                                                      
    Ausgabe:                                          
    RC                 CHAR(2),                       
    FTEXT              CHAR(80),                      
    EINST-ZP-LAST      TIMESTAMP,                     
    ANZ-AUFTRAEGE      INTEGER,                       
    ERGEBNIS-DATEN-X   VARCHAR(10000)                 
    '''
    # call the procedure for getting methods from VSTB0041
    def call_proc_get_methods(self, FKT_SL, VERARB_ZT_SL, ZIEL_SYSTEM, VERW_SYS_SL, SN_SERVICE_LIST, SN_METHOD, VNR, EINST_ZP_VON, EINST_ZP_BIS):
        in1 = FKT_SL
        in2 = VERARB_ZT_SL
        in3 = ZIEL_SYSTEM
        in4 = VERW_SYS_SL
        in5 = 'LFUD5001'
        in6 = 'LFUD5003'
        in7 = 'LFUD1501'
        in8 = ''
        in9 = VNR
        in10 = EINST_ZP_VON
        in11 = EINST_ZP_BIS
        if SN_SERVICE_LIST and len(SN_SERVICE_LIST) > 0:
            in5 = SN_SERVICE_LIST[0]
            if len(SN_SERVICE_LIST) > 1:
                in6 = SN_SERVICE_LIST[1]
                if len(SN_SERVICE_LIST) > 2:
                    in7 = SN_SERVICE_LIST[2]
        if SN_METHOD:
            in8 = SN_METHOD
        else:
            in8 = ''
        out1 = ''
        out2 = '' 
        
        param_tuple = (in1, in2, in3, in4, in5, in6, in7, in8, in9, in10, in11, out1, out2)        
        (error, result) = self.__call_procedure(StoredProcedure.get_methods.value, param_tuple)
        # if the result is not "False" the procedure was executed successfully
        if not error and result:
            # then the first var of the tuple represents the statement object/cursor
            return (None, result[0])
        else:
            return (error, None)


    def insert_param_into_table(self, sql_stmt, params):   
        #Workaround, vor Einführung der stored procedure um Inserts abzusetzen
        #DIES IST MIT VORSICHT ZU GENIESSEN!!!
        #TODO: Aus der AuftragsDB einspielen
        result = ibm_db.exec_immediate(self.db_connection, sql_stmt % params)

        #Dies sollte benutzt werden:
#        (error, prepared_statement) = self.__create_prepared_statement(sql_stmt)
#        if error:
#            print(str(error))
#
#        (error, result) = self.__bind_parameters(prepared_statement, params)
#        if error:
#            print(str(error))   
#  
#        (error, result) = self.__get_result(prepared_statement)
#        if error:
#            print(str(error))

        error = ""
        return (error, result)
        


if __name__ == '__main__':
    
    from module.datasource.sql_stmt_info import SQLStmtInfo
    from module.datasource.sql_builder import Statement
    
    db = DatabaseDB2('DDLG', 'VJLFAX4', 'KMtecU#1')
    (error, msg) =  db.connect()

    if not error:
        # Variablen
        method = 'PUTFNDBWG03'

        # Erstellen des Datentransferobjekts
        stmt_info = SQLStmtInfo()
        stmt_info.set_table('DB2.VSVW2041')
        stmt_info.set_max_rows(20)
	
        # Hinzufügen von WHERE-Bedingungen
        stmt_info.add_where_condition('ORDN_BEGR', Statement._condition_equality.value, '068371146')
        stmt_info.add_where_condition('SN_METHOD', Statement._condition_equality.value, method) 
    	
        # Ausführen der Anweisung, Mit DTO, Datensätze werden direkt gefetcht, kein Cursor
        (error, data) = db.select_with_info(stmt_info)
        
        if error:
            print("### ERROR ###")
            print(error)
        else:
            print("### DATA ###")
            print(data)
        	
        # Schließen der Host-Verbindung
        db.close() 
    else:
        print(error)
        
