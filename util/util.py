from datetime import date
from dateutil.relativedelta import relativedelta

class util:
    
    def str_to_int(val):
        try:
            return int(val)                
        except:
            print("Could not convert " + str(val) + " from int to string")
            return 0
            
    def str_to_float(val):
        try:
            return float(val)                
        except:
            print("Could not convert " + str(val) + " from float to string")
            return 0
                
    def view_2d_list(li):
        for elem in li:
            out = ""
            for col in elem:
                if len(out) > 0:
                    out += "\t"
                out += str(col)
            print(out)
            
    def add_month(date, mon):
        dat_rel = relativedelta(months=mon)
        return date + dat_rel
        
    def add_days(date, day):
        dat_rel = relativedelta(days=day)
        return date + dat_rel
        
    # Datumsformatierung: von "tt.mm.jjj" nach datetime.date
    def dat_konv(dat):
        (tmpTag, tmpMonat, tmpJahr) = dat.split(".")
        return date(int(tmpJahr), int(tmpMonat), int(tmpTag))
        
    def dat_konv_back(dat):
        return str(dat.day).zfill(2) + "." + str(dat.month).zfill(2) + "." + str(dat.year).zfill(4)
    
    def sum_right_col_2d_list(myList):
        out = 0
        for elem in myList:
            out += elem[1]
        return out
    
    def form(num):
        return format(num, '.2f').replace('.', ',')

    def to_file(pfad, myList):
        try:
            datei=open(pfad, "w")
            for elem in myList:
                datei.write(str(elem[0]) + ";" + str(elem[1])+ ";" + str(elem[2]) + "\n")          
        except IOError:
            print("############################")
            print("Fehler beim Öffnen der Datei: " + pfad)
        else:
            datei.close()
    
    def niceprint(li):
        for elem in li:
            print(elem[0] + "\t" + elem[1] + "\t" + elem[2])
#    def szenario(vonJahr, bisJahr):
#        it = it_gh()
#        ab = ab_gh()
#        it.set_bdat("01.10.2013")
#        for jahr in range(vonJahr, bisJahr + 1):
#            for mon in range(1, 13):
#                dat = "28." + str(mon) + "." + str(jahr)
#                it.set_kdat(dat)
#                ab.set_bdat(ut.dat_konv_back(ut.add_days(it.last_day, 1)))
#                datName = r"F:\\gh\out_" + str(jahr) + "_" + str(mon) + ".csv"
#                ut.to_file(datName, it.verlauf(2010, 2022) + ab.verlauf(2010, 2022)