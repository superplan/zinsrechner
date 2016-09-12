'''
Repräsentiert die Plausioff-Tabelle.

@author: Kamfor
'''
from enum import Enum

class ZDATA():
    
    NAME = 'zdata'

    HIDE_COLUMNS = ['TFID']
    
    COLUMN_ORDER = [
        'FORMELID ASC'
    ]
        
    # important data with their column names
    class COLUMN(Enum):
        DATE='DATE'
        REST='REST'
        ZKOSTEN='ZKOSTEN'
        
        
    DATECOLUMNS = ['GUEAB', 'GUEBIS']
    
        
    COLUMNS = [
        'DATE', 'REST', 'ZKOSTEN'
    ]

    
    def __init__(self):
        pass