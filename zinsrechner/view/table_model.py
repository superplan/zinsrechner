# -*- coding: utf-8 -*-
'''
Represents an implemented TableModel, that can be used as a PyQt-Table in Forms.

@author: Moritz Kurt Heilemann
'''
from PyQt4 import QtCore

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, columns, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = columns
        
    def rowCount(self, parent):
        return len(self.mylist)
        
    def columnCount(self, parent):
        if len(self.mylist) > 0:
            return len(self.mylist[0])
        else:
            return 0
            
    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
        
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and len(self.header) > 0:
            return self.header[col]
        return None