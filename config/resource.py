# -*- coding: utf-8 -*-
"""Dieses Modul bietet vereinheitlichten Zugriff auf die Ressourcen-Dateien
der Python-Projekte. Die Ressourcendatei (Endung .qrc) enthält Bilder und .ui
Dateien.

Es wird unterschieden zwischen dem Zugriff auf die Ressourcen in:
    1) der Entwicklungsumgebung (Dateien liegen im Ordner view)
    2) in der gebauten .exe     (Dateien liegen im Temp-Ordner / PyInstaller)

WICHTIG: Damit der Zugriff auf die Ressource für 1) funktioniert, muss folgendes gelten:
    - Die <gui>.ui-Datei liegt im gleichen Ordner, wie die dazugehörige <gui>.py-Datei

@author: Moritz Kurt Heilemann
"""
import sys
import os
import inspect
from config.process import Process

def get(relative_view_path):
    """Liefert den Pfad zur Ressource in Abhängigkeit von 1) und 2)"""
    try:
        # PyInstaller erstellt einen temporären Ordner namens _MEIPASS
        base_path = sys._MEIPASS
    except:
        # Hole aus dem aufrufenden Kontext den Dateipfad
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        base_path = os.path.dirname(module.__file__)

    return os.path.join(base_path, relative_view_path)

def create(res_path):
    """Erstelle eine Ressourcen-Datei aus der angegebenen Ressource"""
    command = r'W:\Org_AEPB1D\AEPB1D_Mitarbeiter\Mitarbeiter\Heilemann\WinPython\python-3.4.3.amd64\Lib\site-packages\PyQt4\pyrcc4 -py3 -o res_rc.py res.qrc'
    error, output = Process.start_process(command, stdout_enabled=True)
    if error:
        print(str(error))
    if output:
        print(str(output))
        