# -*- coding: utf-8 -*-
'''
Represents an implemented TableModel, that can be used as a PyQt-Table in Forms.

@author: Moritz Kurt Heilemann
'''
from PyQt4 import QtCore
from zinsrechner.model.tables.zinsdaten import ZDATA
import locale

locale.setlocale( locale.LC_ALL, '' )

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

    def dateDDMMYYY(self, d):
        tmp = d.split('-')
        return tmp[2].zfill(2) + "." + tmp[1].zfill(2) + "." + tmp[0].zfill(4)

    def float_two_digits(self, num):
        return locale.format('%.2f', num, True)

    def data(self, index, role):

        if not index.isValid() or role not in (QtCore.Qt.DisplayRole, QtCore.Qt.TextAlignmentRole):
            return None

        # Ausrichtung
        if role == QtCore.Qt.TextAlignmentRole:
            if self.header[index.column()] in ZDATA.DATECOLUMNS:
                return QtCore.Qt.AlignCenter
            if self.header[index.column()] in ZDATA.FLOATCOLUMNS:
                return QtCore.Qt.AlignRight

        # Anzeigeformat
        if role == QtCore.Qt.DisplayRole:
            if self.header[index.column()] in ZDATA.DATECOLUMNS:
                return self.dateDDMMYYY(self.mylist[index.row()][index.column()])
            if self.header[index.column()] in ZDATA.FLOATCOLUMNS:
                return self.float_two_digits(self.mylist[index.row()][index.column()])

        return self.mylist[index.row()][index.column()]


    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and len(self.header) > 0:
            return self.header[col]
        return None