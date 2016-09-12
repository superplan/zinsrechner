# -*- coding: utf-8 -*-

from util.util import util as ut

class Rechenkern():
    
    def __init__(self, paramList = ""):
        
        self.finSumme   = 0
        self.rate       = 0
        self.effJZ      = 0
        self.sollZB     = 0
        self.beginn     = 0
        if len(paramList) == 5:
            self.set_fin_summe (paramList[0])
            self.set_rate      (paramList[1])
            self.set_effJZ     (paramList[2])
            self.set_soll_ZB   (paramList[3])
            self.set_beginn    (paramList[4])

    def set_fin_summe(self, val):
        if len(str(val)) > 0:
            self.finSumme = int(val)

    def set_rate(self, val):
        if len(str(val)) > 0:
            self.rate = int(val)
            
    def set_effJZ(self, val):
        if len(str(val)) > 0:
            self.rate = float(val)
            
    def set_soll_ZB(self, val):
        if len(str(val)) > 0:
            self.rate = int(val) 
            
    def set_beginn(self, val):
        if len(str(val)) > 0:
            self.rate = ut.dat_konv(val)
            
    def print_para(self):
        out = [["param","wert"],\
               ["-----","----------"],\
               ["total", self.finSumme],\
               ["rat", self.rate],\
               ["effJZ", self.effJZ],\
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

