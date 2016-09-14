# -*- coding: utf-8 -*-
'''
Handles the config-file of the application.

@author: Moritz Kurt Heilemann
'''
from os import path as ospath
from configparser import SafeConfigParser
#from module.datasource.sql_stmt_info import SQLStmtInfo
#from module.datasource.sql_builder import Statement



# define a private module variable
__config_parser = None
__local_db = None
__config_file = "config.cfg"

def init(path):
    # load config data
    global __config_parser
    global __config_file
    # create config parser object to access and save program data
    __config_parser = SafeConfigParser()
    __config_file = ospath.join(path, __config_file)
    
    print('Verwendete Konfigurationsdatei: ' + str(__config_file))    
    
    # try to find the config file
    if __config_file not in __config_parser.read(__config_file):
        path = r'W:\Org_AEPB1D\AEPB1D_Mitarbeiter\Mitarbeiter\Kamfor\WinPython-64bit-3.4.4.2\projects\ZRechner'
        __config_parser.read(ospath.join(path, __config_file))
        print('Config-Manager erfolgreich initialisiert!')
        
    
    # check if config file valid
    if not key_exists('DATA', 'path'):
        # if the file is not valid create a new one
        __config_parser.add_section('DATA')
        __config_parser.set('DATA', 'path', r'data\zinsdaten.db')
        __config_parser.set('DATA', 'report_path', r'data\report')
        __config_parser.add_section('LOG')
        __config_parser.set('LOG', 'file', r'log\zrechner.log')
        __config_parser.add_section('APP')
        __config_parser.set('APP', 'path', path)
        
        # save the config file, overwrite
        with open(__config_file, 'w') as config_file:
            __config_parser.write(config_file)
            
    
def get(section, key):
    return __config_parser.get(section, key)
    
def set(section, key, value):
    global __config_parser
    __config_parser.set(section, key, value)
    # save changes
    with open(__config_file, 'w+', encoding='utf8') as configfile:
        __config_parser.write(configfile)
    
# help function for easier use of this module
def get_path(key):
    return __config_parser.get('PATH', key)

# returns True if the section, key exists
def key_exists(section, key):
    if __config_parser:
        return __config_parser.has_section(section) and __config_parser.has_option(section, key)
    else:
        return False
        
def set_database(db):
    global __local_db
    __local_db = db

def is_database_ready():
    global __local_db
    return __local_db
    
def __get_option_string(obj):
    if hasattr(obj, 'value'):  
        return obj.value
    else:
        return obj
