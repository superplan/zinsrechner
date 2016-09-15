# -*- coding: iso-8859-1 -*-
'''
Dies ist das Main-Modul des Projekts.
Von hier aus werden grundlegende Intialisierungen angestoßen
und die Hauptanwendung gestartet.

@author: Michael Kamfor
'''
import sys
import os
from zinsrechner.controller.main_controller import MainController
from zinsrechner.model import config_manager

# version info
__version__ = '0.0.0'


def main():
    """Initialisierung der Anwendung"""

    # Hole und speichere den Pfad zur Anwendung
    path = set_app_path()

    # load the config file
    config_manager.init(path)

    # Initialisiere den Controller des Hauptfensters
    controller = MainController()

    # Zeige die Benutzerschnittstelle
    controller.run()

def set_app_path():
    """Ermittle den Pfad der Anwendung
    Ist die Anwendung gepackt als .exe (freezed) oder
    wird Sie in der Entwicklungsumgebung ausgeführt?
    """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path


if __name__ == '__main__':
    main()
