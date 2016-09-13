# -*- coding: utf-8 -*-
'''
This controller handles all functional requests for the main.py/main.ui.
It delegates the functionality from the model to the display/view.

@author: Moritz Kurt Heilemann
'''
import sys
from PyQt4 import QtGui
from zinsrechner.view.main import Main
from zinsrechner.model.tables.table_zdata import ZDATA
from zinsrechner.model.db_manager import DBManager
from zinsrechner.controller.rechenkern import Rechenkern
from util.util import util as ut
from module.datasource.sql_stmt_info import SQLStmtInfo
#from module.datasource.sql_builder import Statement

class MainController():
    """Haupt Controller der Anwendung"""    
    
    def __init__(self):
        """Initialisiert den Controller und registriert Events"""
        # VIEW    
        # creating and starting the ui main window
        self.app = QtGui.QApplication(sys.argv)
        
        # init ui elements and events
        self.view = Main()
        self.view.app = self.app
  
        # register events
        self.register_events()
        self.init_elements()
        
        
    # handle all events that have to be forwarded to the model
    def register_events(self):
        self.view.commandLinkButtonBerechnen.clicked.connect(self.compute)
        self.view.lineEditTotal.returnPressed.connect(self.compute)
        self.view.lineEditJZ.returnPressed.connect(self.compute)
        self.view.lineEditSZB.returnPressed.connect(self.compute)
        self.view.lineEditRate.returnPressed.connect(self.compute)
        
        self.view.lineEditJZ.textChanged.connect(self.compute)
        self.view.lineEditTotal.textChanged.connect(self.compute)
        self.view.lineEditRate.textChanged.connect(self.compute)
        self.view.lineEditJZ.textChanged.connect(self.compute)
        self.view.lineEditSZB.textChanged.connect(self.compute)
        self.view.dateEditBeginn.dateChanged.connect(self.compute)
        
    def init_elements(self):
        self.view.textBrowserStatus.setText("ZRechner ist gestartet.")
        self.view.labelRestschuld.setText("")
        self.view.labelZKosten.setText("")
        self.view.labelZKostenTotal.setText("")
        self.view.labelDauer.setText("")
        self.view.labelNetto.setText("")
        self.view.labelBrutto.setText("")
        self.view.lineEditSteuer.setText("40")
        self.view.lineEditJZ.setText("1.39")
        self.view.lineEditSZB.setText("10")
        self.view.dateEditBeginn.setDate(ut.dat_konv("01.01.2018"))
        
    def read_elements(self):
        
        return ({"FinSumme": self.view.lineEditTotal.text(), \
                 "Rate":     self.view.lineEditRate.text(),  \
                 "EffJZ":    self.view.lineEditJZ.text(),    \
                 "SollZB":   self.view.lineEditSZB.text(),   \
                 "Beginn":   self.view.dateEditBeginn.text()})

    def compute(self):  

        rechenkern = Rechenkern(self.read_elements())
        rechenkern.print_para()
        if rechenkern.status_ok():
            # Nun kann gerechnet werden
            print("OK!!")
        
            self.view.textBrowserStatus.setText("Starte Berechnung")
            db_manager = DBManager()
            db_manager.mytest("TABLE01")        
            self.view.set_table(db_manager.mytest_select("TABLE01"))
        


        # Hinzufügen von WHERE-Bedingungen
#        stmt.add_where_condition('ORDN_BEGR', Statement._condition_equality.value, '068371146')
#        stmt.add_where_condition('SN_METHOD', Statement._condition_equality.value, method) 


    def run(self):
        # all ui and and program initialization is done 
        # show the ui
        self.view.show()
        # define exit point
        sys.exit(self.app.exec_())
