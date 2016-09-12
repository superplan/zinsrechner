# -*- coding: utf-8 -*-
import os
from module.config import setuptools

# Starten des Buildvorgangs
# Die erstellte spe-Datei kann nach dem erstmaligem Ausführen beliebig geändert werden
# Einige Einträge werden jedoch bei jedem Build automatisch generiert (UI-Dateien z.b.)
params = setuptools.run_setup(inputfile='main.py', 
                              name='PlausiOff', 
                              gui_folder=os.path.realpath(r'zrechner/view'))
