# -*- coding: iso-8859-1 -*-
'''
Creation of the main window from the desigenr XML. 
NC user have to use the command within the python folder!
NOT NEEDED IF uic.loadUiType USED
pyuic4 main.ui > main.py

@author: Moritz Kurt Heilemann
'''
import PyQt4
from PyQt4 import uic, QtGui
from zrechner.view.table_model import TableModel

#from sys import path
#path.append("W:\Org_AEPB1D\AEPB1D_Mitarbeiter\Mitarbeiter\Kamfor\WinPython-64bit-3.4.4.2\notebooks\StandardModule\module")
from module.config import resource

# loading of the UI file
Ui_MainWindow, QtBaseClass = uic.loadUiType(resource.get(r'main.ui'))

# main window class
class Main(PyQt4.QtGui.QMainWindow, Ui_MainWindow):
    
    
    def __init__(self):
        PyQt4.QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.tableViewZRechner.horizontalHeader().setStretchLastSection(True)
        self.tableViewZRechner.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
    
    def set_table(self, result):
        (error, columns, data) = result
        if error:
            self.textBrowserStatus.setText(str(error))
        if data:
            self.textBrowserStatus.setText("SQL-Abfrage erfolgreich abgeschickt.")
            self.tableViewZRechner.clearSpans()
            table_model = TableModel(self, data, columns)
            self.tableViewZRechner.setModel(table_model)
            self.tableViewZRechner.resizeRowsToContents()