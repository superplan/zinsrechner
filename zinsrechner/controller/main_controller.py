# -*- coding: utf-8 -*-
'''
This controller handles all functional requests for the main.py/main.ui.
It delegates the functionality from the model to the display/view.

@author: Moritz Kurt Heilemann
'''
import sys
from PyQt4 import QtGui
from zinsrechner.view.main import Main
from zinsrechner.model.tables.zinsdaten import ZDATA
from zinsrechner.model.db_manager import DBManager
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
        self.init_elements()
        self.register_events()
        self.update_salary_infos()
        self.compute()
        
        
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
        
        
        self.view.lineEditRate.returnPressed.connect(self.update_salary_infos)
        self.view.lineEditSteuer.returnPressed.connect(self.update_salary_infos)
        self.view.lineEditRate.textChanged.connect(self.update_salary_infos)
        self.view.lineEditSteuer.textChanged.connect(self.update_salary_infos)
        
    def init_elements(self):
        self.view.textBrowserStatus.setText("ZRechner ist gestartet.")
        self.view.labelRestschuld.setText("")
        self.view.labelZKosten.setText("")
        self.view.labelZKostenTotal.setText("")
        self.view.labelDauer.setText("")
        self.view.labelNetto.setText("")
        self.view.labelBrutto.setText("")
        self.view.lineEditSteuer.setText("40")
        self.view.lineEditTotal.setText("300")
        self.view.lineEditRate.setText("100")
        self.view.lineEditJZ.setText("1.39")
        self.view.lineEditSZB.setText("10")
        self.view.dateEditBeginn.setDate(ut.dat_konv("01.01.2018"))
        
    def read_elements(self):
        
        return ({"FinSumme": self.view.lineEditTotal.text(), \
                 "Rate":     self.view.lineEditRate.text(),  \
                 "EffJZ":    self.view.lineEditJZ.text(),    \
                 "SollZB":   self.view.lineEditSZB.text(),   \
                 "Beginn":   self.view.dateEditBeginn.text()})
        
    def update_elements(self, werte):
#        werte = (restSchuld, kostenSZB, kostenTotal, dauerTotal)
        self.view.labelRestschuld.setText  ("%.2f" % werte[0])
        self.view.labelZKosten.setText     ("%.2f" % werte[1])
        self.view.labelZKostenTotal.setText("%.2f" % werte[2])
        
        dauerTotalMonate = werte[3]
        dauerJahre       = int(dauerTotalMonate / 12)
        dauerMonate      = dauerTotalMonate - dauerJahre * 12
        self.view.labelDauer.setText(str(dauerJahre) + " Jahre, " + str(dauerMonate) + " Monate")
        

    def update_salary_infos(self):
        tmpRate   = float(self.view.lineEditRate.text())
        tmpNetto  = tmpRate / 40 * 100
        tmpBrutto = tmpNetto / (1 - float(self.view.lineEditSteuer.text()) / 100)
        self.view.labelNetto.setText ("%.2f" % tmpNetto)
        self.view.labelBrutto.setText("%.2f" % tmpBrutto)  

    def compute(self):  

        zinsdat = ZDATA(self.read_elements())
        if zinsdat.status_ok():
            
            # Nun kann gerechnet werden            
            self.view.textBrowserStatus.setText("Starte Berechnung")
            db_manager = DBManager()
            db_manager.create_static_table()
                        
            results = zinsdat.forward_projection()
            if results:
                if len(results) > 0:
                    db_manager.insert_rows(results)
                    (error, kostenAlle) = db_manager.get_cost()
                    
                    if not error:
                        kostenEnde = zinsdat.eval_cost(kostenAlle)
                        self.update_elements(kostenEnde)
            else:
                self.view.textBrowserStatus.setText("Ergebnis konnte nicht berechnet werden")
            self.view.set_table(db_manager.mytest_select(ZDATA.NAME))
        


        # Hinzufügen von WHERE-Bedingungen
#        stmt.add_where_condition('ORDN_BEGR', Statement._condition_equality.value, '068371146')
#        stmt.add_where_condition('SN_METHOD', Statement._condition_equality.value, method) 


    def run(self):
        # all ui and and program initialization is done 
        # show the ui
        self.view.show()
        # define exit point
        sys.exit(self.app.exec_())
