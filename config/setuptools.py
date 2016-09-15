# -*- coding: utf-8 -*-
'''
Dieses Modul dient als Werkzeug zur Ausführung von Python-Setups mit PyInstaller.

# #1
# Starten des Buildvorgangs
# 1. entweder vollständigen Pfad zur Inputdatei angeben, 
# oder wenn sie im gleichen Verzeichnis liegt den Dateinamen
# 2. Den Namen der Ausgabe-exe ohne das ".exe" angeben
# 3. optional: icon-Pfad angeben
# 4. optional: debug modus aktivieren
setuptools.run_setup('__init__.py', name='Doku_Tool', icon='res\icon.ico', debug=True)


# #2 Falls der Versions-String in einer anderen Datei liegt
input_file = '__init__.py'
version = setuptools.get_version(filepath="versions_datei_pfad")
setuptools.run_setup(inputfile=input_file, name='Doku_Tool', version=version)

@author: V933402
'''
import os
import re
import traceback
import win32com.client
from module.config.process import Process

# Erlaubt sind Versionen-Strings der Form "0.0.0"
# Wenn später weitere erlaubt sein sollen, müssen die regulären 
# Ausdrücke angepasst werden
__VERSION_VAR_STRING = r'__version__[ ]?=[ ]?[\'\"][0-9\.]+[\"\']'
__VERSION_STRING = r'[0-9\.]+'

# Liefert einen Bytestream, der von der Windows-Kommandozeile gelesen werden kann
def __create_cmd_line(string):
    return bytes(string + '\n', 'ascii')

# Liefert einen Versions-String aus einer einem Python-Modul, ohne dieses Modul
# inkludieren zu müssen. Der Versions-String muss die Form "0.0.0" besitzen.
def get_version(filepath):
    # Lies die Version von der angegebenen Datei ein __init__
    version_file = filepath
    file = open(version_file, 'rt')
    version_file_string = file.read()
    file.close()
    
    # Durchsuchen der Datei nach dem regulären Ausdruck
    search = re.search(__VERSION_VAR_STRING, version_file_string, re.M)
    if search:
        search = re.search(__VERSION_STRING, str(search.group(0)), re.M)
        if search:
            return str(search.group(0))
    # wenn kein Versionsstring gefunden wurde:
    raise RuntimeError('Version nicht gefunden oder nicht korrekt formatiert in %s!' % (version_file,))
    
def set_version(filepath, version):
    version_file = filepath
    with open(version_file, 'r+') as file:
        version_file_string_start = file.read()
        version_file_string = re.sub(__VERSION_VAR_STRING, '__version__ = \'{}\''.format(version), version_file_string_start)
        # Ersetze nur die Datei, wenn der neue Inhalt in etwa so groß ist wie der alte
        # Falls der neue Inhalte mehr als 10 Zeichen kleiner ist als der alte ist möglicherweise ein Fehler passiert!
        if (len(version_file_string_start) - 10) <= len(version_file_string):
            file.seek(0)    
            file.write(version_file_string)
            file.truncate()
        else:
            raise Exception('Fehler beim überschreiben der Versions {} in {}'.format(version, filepath)) 
        
def get_ui_files(project_path):
    """Durchsucht das angegebene Verzeichnis nach allen UI-Dateien
    und sammelt die Pfade in einer Liste"""
    ui_files = []    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.ui'):
                ui_files.append(os.path.realpath((os.path.join(root, file))))
        
    print('Gefundene GUI-Dateien: ' + str(ui_files))
    return ui_files
    
def get_all_folders(project_path):
    """Durchsucht das angegebene Verzeichnis nach allen UI-Dateien
    und sammelt die Pfade in einer Liste"""
    folder = []    
    for root, dirs, files in os.walk(project_path):
        for _dir in dirs:
            if _dir != '__pycache__':
                folder.append(os.path.normpath(os.path.realpath((os.path.join(root, _dir)))))
        
    print('Gefundene Ordner: ' + str(folder))
    return folder
    
# Erwartet wird ein versions-string der Form "x.y.z"
def increment_version_micro(version):
    version_parts = version.split('.')
    return version_parts[0] + '.' + version_parts[1] + '.' + str(int(version_parts[2]) + 1) 
    
def increment_version_minor(version):
    version_parts = version.split('.')
    return version_parts[0] + '.' + str(int(version_parts[1]) + 1)  + '.' + version_parts[2]
       
def increment_version_major(version):
    version_parts = version.split('.')
    return str(int(version_parts[0]) + 1) + '.' + version_parts[1] + '.' + version_parts[2]
    
def get_dir_from_calling_function(stack_depth):
    try:
        return os.path.dirname(path_format(traceback.extract_stack()[stack_depth][0]))
    except Exception as e:
        raise Exception("Pfad der aufrufenden Datei nicht ermittelbar! "+str(repr(e)))
        
def get_abs_path(path, root=None):
    """Liefert Zu einem Pfad (relativ oder absolut) und seinem Stammverzeichnis den absoluten Pfad.
    Hat keine Wirkung, wenn der Pfad vorher schon absolut war.
    Formatiert den übergebenen Pfad-String"""
    if path:
        path = path_format(path)
    if root:
        root = path_format(root)
        
    if root and path and not os.path.isabs(path):
        return os.path.normpath(os.path.join(root, path))
    elif path:
        return os.path.normpath(path)
    elif root:
        return os.path.normpath(root)
        
def path_format(path):
    return path.replace('\\', '/')
        
# startet den PyInstaller direkt mit den angegeben Parametern
def start_pyinstaller_cmd(inputfile, outputfile, distpath='.', specpath='./build', workpath='./build', build_spec=False, paths=[], **kwargs):
    # Speichere Parameter zur Ergänzung der Rückgabewerte
    kwargs['inputfile'] = inputfile  
    kwargs['outputfile'] = outputfile  
    kwargs['specpath'] = specpath
    kwargs['workpath'] = workpath
    kwargs['distpath'] = distpath
    
    is_test = 'test' in kwargs and kwargs['test']
    
    # 1. Zeile: wechseln ins Projektverzeichnis
    line1 = r'cd /d ' + os.path.dirname(inputfile)
    
    if build_spec:
        line2 = r'pyi-makespec '
    else:
        line2 = r'pyinstaller --noconfirm '

    # 2. Zeile: Ausführen von PyInstaller
    line2 += r'--onefile --name="{name}" '.format(name=outputfile)
    
    # In Abhängigkeit gelieferter Parameter wird der PyInstaller-String gebaut
    if 'debug' in kwargs and kwargs['debug']:
        line2 += r'--debug --console '
    else:
        line2 += r'--noconsole '
    if 'icon' in kwargs:
        line2 += r'--icon="{}" '.format(kwargs['icon'])
    if 'log_level' in kwargs:
        line2 += r'--log-level="{}" '.format(kwargs['log_level'])
    if specpath:
        line2 += r'--specpath="{}" '.format(specpath)
    if not build_spec and not is_test:
        if distpath:
            line2 += r'--distpath="{}" '.format(distpath)
        if workpath:
            line2 += r'--workpath="{}" '.format(workpath)
        if paths and len(paths) > 0:
            line2 += r'--paths={} '.format('"' + '":"'.join(paths)+'"')
        

    line2 += inputfile
    
    print('Buildvorgang startet!')
    print('1. Eingabedatei: {}'.format(inputfile))
    print('2. Ausgabedatei: {}'.format(os.path.join(os.path.dirname(inputfile), outputfile)))
    print('3. Befehl: {}'.format(line2))
    
    # Build only if it's not a test
    if is_test is not True:
        # Übermitteln der 2 Zeilen an den Prozess
        # Der Prozess ruft PyInstaller auf
        error, output = Process.start_process([line1, line2], stdout_enabled=True)
        
        # Zum Abschluss werden die Ausgabeparameter ausgegeben
        if error:
            print('Fehler: ' + str(error))
        if output:
            print('Ausgabe: ' + str(output))
            
        if is_test:
            print('Test erfolgreich abgeschlossen!')
        
    # Gib alle gesetzten parameter zurück
    return kwargs

# Bietet eine komfortable Schnittstelle zum Aufruf des PyInstallers. Abholen der Version und zusammenbauen
# des EXE-Namens werden hier automatisiert.
def run_setup(inputfile, name, name_format='{name}_{version}', version=False, auto_version=False, **kwargs):
    """
    gui_folder: Bestimmt, ob die GUI-Dateien mit in die .exe gepackt werden sollen. 
                Gibt den Ordner an, wo nach GUI-Dateien gesucht werden soll
    """
    
    # Behandle relative Pfade!!!
    if 'path_root' in kwargs:
        path_root = kwargs['path_root']
    else:
        path_root = os.path.normpath(os.path.join(get_dir_from_calling_function(-3)))
    
    
    inputfile = path_format(os.path.realpath(path_format(inputfile)))
    kwargs['distpath'] = get_abs_path(kwargs.get('distpath', None), path_root)
    kwargs['specpath'] = get_abs_path(kwargs.get('specpath', None) or r'build/', path_root)
    kwargs['workpath'] = get_abs_path(kwargs.get('workpath', None) or r'build/', path_root)
    if 'gui_folder' in kwargs:
        kwargs['gui_folder'] = get_abs_path(kwargs.get('gui_folder', None), path_root)
    kwargs['path_root'] = path_root

    is_test = 'test' in kwargs and kwargs['test']
    normal_exe_name = name + '.exe'
    normal_spec_name = normal_exe_name + '.spec'
    
    # Der Ort, an dem die spec-Datei zu dieser Installation erwartet bzw. erstellt wird
    specfile = os.path.normpath(os.path.join(kwargs['specpath'], normal_spec_name))

    # MAGIE! Wenn das gelieferte Inputfile keinen vollständigen Pfad besitzt (z.b. "__init__.py")
    # Versuche die Datei im Ordner zu finden, in welchem sich die setup.py befindet
    if not os.path.isfile(inputfile):
        new_inputfile = os.path.join(path_root, inputfile)
        # Wenn die Datei jetzt nicht gefunden wird, gibt es einen Fehler
        if not os.path.isfile(inputfile):
            raise Exception('Das Setup kann die Datei {} nicht finden!'.format(inputfile))
        else:
            inputfile = new_inputfile

    # Wenn keine Version angegeben ist und diese automatisch gefunden werden soll:
    if not version and auto_version:
        # Der Versions-String sollte standardmäßig in der Input-Skriptdatei stecken
        version = get_version(inputfile)
        
        # Erhähe die Versionsnummer
        version = increment_version_micro(version)

    # Falls eine Version angegeben ist, wird diese in den Dateinamen geschrieben
    if version:

        # Setze die Versionsnummer
        set_version(inputfile, version)
        
        outputfile = name_format.format(name=name, version=version) + '.exe'
    else:
        outputfile = name + '.exe'
        
        
    # Schau, ob du die .spec-Datei findest:
    if not is_setup_found(specfile) or kwargs.get('create_spec', True): 
        if not is_setup_found(specfile):
            print('PyInstaller-Setup-Datei gefunden!')
        
        if is_test:
            kwargs['test'] = False
            
        # Anlegen der .spec-Datei 
        start_pyinstaller_cmd(inputfile=inputfile, outputfile=os.path.basename(normal_exe_name), build_spec=True, **kwargs)
                
        # Wenn die .spec-Datei erstellt wurde, werden die beiden Standardprojektverzeichnisse angegeben,
        # wo PyInstaller letztendlich nach den Python-Scripts fürs packen sucht
        paths = [os.path.dirname(inputfile), r'\\\\\\\\corp.ergo\\\\public\\\\VPLeben\\\\iLife\\\\Python\\\\DEV\\\\StandardModule']
        setup_script_change_project_path(specfile, paths)

        if is_test:
            kwargs['test'] = is_test    
            
    # Entweder die spec-Datei wurde gerade erstellt oder Sie war vorhanden
    # Ändern des Namens der neuen Executable:
    setup_script_change_name(specfile, outputfile)

                    
    # Für das Hinzufügen von Dateien zur .exe setzt PyInstaller ist es erforderlich,
    # die Spec-Datei zu bearbeiten und die Dateien dort einzutragen
    if 'gui_folder' in kwargs:
        # Hole alle GUI-Dateien aus dem Ordner und Unterordnern
        files = get_ui_files(kwargs['gui_folder'])
        formated = []
        
        for file in files:
            # Eingetragene Dateien müssen in einer bestimmten Form erscheinen
            # Das 2. Element des Tupels gibt an, in welcher Ebene sich die Datei
            # Nach dem Entpacken der .exe befindet ('.' = Hauptverzeichnis des entpackten Ordners)
            formated.append(str((file.replace('\\', r'/'), '.')))
        
        # Falls es eine resourcendatei zur GUI gibt, muss diese angegeben werden!
        if 'gui_resource' in kwargs:
            formated.append(str((os.path.normpath(kwargs['gui_resource']).replace('\\', r'/'), '.')))
        
        # Ändern der .spec-Datei
        setup_script_add_files(specfile, formated)
        
    # Sagt PyInstaller, wo es nach Libraries bzw. Standardmodulen suchen soll
    # list(set(list)) entfernt Duplikate aus einer Liste, da diese in Sets nicht definiert sind
    if 'paths' in kwargs:
        kwargs['paths'] = list(set(kwargs['paths'] + get_paths(inputfile)))
    else:
        kwargs['paths'] = list(set(get_paths(inputfile)))
        
    #print('Yeah: ' + str(new_paths))
    # Rufe die Windows-Batchdatei mit dem Skript auf
    # Inputfile ist immer die Spec-Datei, diese enthält auch mehr parameter, 
    # als mit dem Kommandozeilenaufruf getätigt werden können
    return start_pyinstaller_cmd(inputfile=specfile, outputfile=outputfile, **kwargs)
    
def setup_script_change_name(spec_path, file_name):
    """Ändert vom angegebenen Skript/Spec-Datei den Namen der .exe."""
    replace_file_content(spec_path, r'name=[^\n]*', r"name='" + file_name +r"',")
    
def setup_script_change_project_path(spec_path, project_paths):
    """Ändert vom angegebenen Skript/Spec-Datei den Namen der .exe."""
    replace_file_content(spec_path, r'pathex=[^\n]*', r"pathex=['" + "', '".join(project_paths) +r"'],")
        
def setup_script_add_files(spec_path, gui_files):
    """Fügt die angegebenen GUI-Dateien der .spec-Datei von PyInstaller hinzu,
    damit diese in der .exe archiviert werden."""
    replace_file_content(spec_path, r'datas=[^\n]*', r'datas=[' + ", ".join(gui_files) +r'],')

def replace_file_content(filepath, regex, new_content):
    """Ersetzt innerhalb einer Tetdatei einen Teilstring, repräsentiert durch den regulären Ausdruck regex
    mit dem neuen Inhalt"""
    content = ''
    with open(filepath, 'r+', encoding='utf8') as file:
        content = file.read()
        content = re.sub(regex, new_content , content)
        file.seek(0)    
        file.write(content)
        file.truncate()  
        
def is_setup_found(spec_path):
    """Stellt fest, ob am angegebenen Pfad das Setup-Skript bereits erstellt wurde.
    Wenn es erstellt wurde, muss es nicht neu erstellt, sondern kann bearbeitet werden."""
    return os.path.isfile(spec_path) and spec_path.endswith('.spec')
    
def get_paths(filepath):
    """Ermittelt die aus der Inputfile angegebenen Libraries, die PyInstaller explizit genannt werden müssen.
    Es sucht aus der init-Datei alle Pfade, die in sys.path.append angegeben wurden."""
    paths = []
    with open(filepath, 'r+', encoding='utf8') as file:
        content = file.read()

        # Durchsuchen der Datei nach dem regulären Ausdruck
        found_matches = re.findall(r'sys.path.append\([^\n]*\)', content, re.M)
        
        for match in found_matches:
            # Die ersten 16 Stellen und die letzte Stele abschneiden
            found_string = match[16:-1]
            
            # Der Pfad kann nur hinzugefügt werden, wenn er konstant ist, d.h. Code funktioniert nicht!
            if found_string[0] in ('r', '"', '\''):
                # Falls r (escape) verwendet wird, schneide die ersten beiden Zeichen (r') und das letzte (') Zeichen ab
                if found_string[0] == 'r':
                    found_string = found_string[2:-1]
                # Ansonsten schneide ' und ' ab        
                else:
                    found_string = found_string[1:-1]
                
                if found_string not in paths:
                    paths.append(found_string)
    print('Eingebundene Libraries: '+str(paths))
            
    return paths
    
# Erstellt eine Windows-Verknüpfung zu einer Datei mit festgelegten Argumenten
def create_shortcut(linked_file_path, shortcut_file_path, arguments=r''):
    shell = win32com.client.Dispatch('WScript.Shell')
    
    # Falls der angegebene Verknüpfung nicht auf '.lnk' endet, hänge es an
    if shortcut_file_path and not shortcut_file_path.endswith('.lnk'):
        shortcut_file_path += '.lnk'
    
    if os.path.isfile(linked_file_path) and not os.path.isabs(linked_file_path):
        linked_file_path = os.path.join(os.path.dirname(os.path.realpath(linked_file_path)), linked_file_path)
    elif not os.path.isfile(linked_file_path):
        raise Exception('Die zu verlinkende Datei "{}" wurde nicht gefunden!'.format(linked_file_path))
    
    # Wenn der Pfad relativ ist, z.b. "build/init.py" 
    if not os.path.isabs(shortcut_file_path):
        shortcut_file_path = os.path.join(os.path.dirname(os.path.realpath(linked_file_path)), shortcut_file_path)
     
    shortcut = shell.CreateShortCut(shortcut_file_path)
    shortcut.Targetpath = linked_file_path
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.save()
    
    print('Link zu {} erstellt in {}'.format(linked_file_path, shortcut_file_path))
    
    