'''
Repräsentiert die Zinsrechentabelle.

@author: Kamfor
'''
from enum import Enum
from util.util import util as ut

class ZDATA():
    
    NAME = 'zdata'

    HIDE_COLUMNS = ['TFID']
    
    COLUMN_ORDER = [
        'FORMELID ASC'
    ]
        
    # important data with their column names
    class COLUMN(Enum):
        DATUM='DATUM'
        RESTSCHULD='RESTSCHULD'
        ZKOSTEN='ZKOSTEN'
        
        
    COLUMNS = [
        'DATUM', 'RESTSCHULD', 'ZKOSTEN'
    ]
    
        
    COLUMNS_AND_TYPES = "'DATUM' DATE, 'RESTSCHULD' REAL, 'ZKOSTEN' REAL"


    
    def __init__(self, dictionary):
        
        self.finSumme   = 0
        self.rate       = 0
        self.effJZ      = 0
        self.sollZB     = 0
        self.beginn     = 0
        
        for name, val in dictionary.items():
            if name == "FinSumme" and len(str(val)) > 0:
                setattr(self, 'finSumme', ut.str_to_int(val))
            if name == "Rate"     and len(str(val)) > 0:
                setattr(self, 'rate',     ut.str_to_int(val))
            if name == "EffJZ"    and len(str(val)) > 0:
                setattr(self, 'effJZ',    ut.str_to_float(val))
            if name == "SollZB"   and len(str(val)) > 0:
                setattr(self, 'sollZB',   ut.str_to_int(val))
            if name == "Beginn"   and len(str(val)) > 0:
                setattr(self, 'beginn',   ut.dat_konv(val))
            
    def print_para(self):
        out = [["param" , "wert"],\
               ["------", "----------"],\
               ["total" , self.finSumme],\
               ["rat"   , self.rate],\
               ["effJZ" , self.effJZ],\
               ["sollZB", self.sollZB],\
               ["beginn", self.beginn],\
               ["----------------------",""]]
        ut.view_2d_list(out)
    
    def status_ok(self):
        try:
            if self.finSumme  > 0 \
              and self.rate   > 0 \
              and self.effJZ  > 0 \
              and self.sollZB > 0:
                  return True
            else:
                return False
        except:
            return False
    
    def forward_projection(self):
        
        out = []
        rest   = self.finSumme
        kosten = 0
        maxDauer = 12*50 + 1
        
        if self.finSumme * (self.effJZ/12) / 100 > self.rate:
            print("Rate ist zu klein")
            return
        
        for step in range(0, maxDauer):
            tmpDate  = ut.add_month(self.beginn, step)
            out     += [(tmpDate, "%.2f" % rest, "%.2f" % kosten)]
#############################################
#           Hier ist des Pudels Kern
#############################################
            kostenMonat = rest * (self.effJZ/12) / 100
            kosten += kostenMonat
            rest   += kostenMonat - self.rate
            if rest < 0:
                return out
#############################################
#############################################
        return out
    
    def eval_cost(self, val):
        dauerSZB   = 12 * self.sollZB
        dauerTotal = len(val)
        
        restSchuld  = val[-1][0]
        kostenSZB   = 0
        kostenTotal = val[-1][1]
        
        if dauerTotal >= dauerSZB:
            kostenSZB = val[dauerSZB][1]
        else:
            kostenSZB = kostenTotal

        return (restSchuld, kostenSZB, kostenTotal, dauerTotal)
