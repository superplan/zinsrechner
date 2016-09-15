# -*- coding: utf-8 -*-
'''
Diese Klasse repräsentiert ein Prozess der in Python gestartet und verwaltet wird.
Ein gestarteter Prozess kann jedes mögliche Programm sein. Es ist optimiert für die 
Benutzung mit Windows-Batchdateien.

Quelle: https://docs.python.org/2/library/subprocess.html

@author: V933402
'''

import subprocess
import os
from enum import Enum

class Process():
    
    # Liste von allen Typen/Arten von Prozessen
    # Eine Unterscheidung ist sinnvoll, um prozessspezifische Anforderungen umzusetzen
    class TYPE(Enum):
        WINDOWS_BATCH = 'cmd.exe'
        GIT_CMD = '\\corp.ergo\public\Org_AEPB1D\AEPB1D_Mitarbeiter\Mitarbeiter\Kamfor\GIT\git-cmd.exe'
        
    def __init__(self, proc_type=TYPE.WINDOWS_BATCH, stdout_enabled=False):
        self.type = proc_type.value if proc_type in self.TYPE else proc_type
        self.process = None
        # Note: Do not use stdout=PIPE or stderr=PIPE with this function 
        # as that can deadlock based on the child process output volume. 
        # Use Popen with the communicate() method when you need pipes.
        self.stdout_enabled = stdout_enabled
        
    # Liefert einen Bytestream, der von der Windows-Kommandozeile gelesen werden kann
    def __create_cmd_line(string):
        return bytes(string + '\n', 'ascii')
        
    def __convert_input(obj):
        # 1. Wenn es ein String ist
        if isinstance(obj, str):
            return Process.__create_cmd_line(obj)

        # 2. Wenn es eine Liste ist und mind. das erste Element ein String
        if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], str):
            _bytes = b''
            for line in obj:
                _bytes += Process.__create_cmd_line(str(line))
            return _bytes
            
        return None
        
    # PUBLIC
    # Erstelle bzw. starte den Prozess
    def create(self, **kwargs):
        try:
            self.process = subprocess.Popen(self.type, 
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE if self.stdout_enabled else None,
                                            **kwargs)
            return False, True
        except Exception as e:
            return repr(e), None
            
    def create2(self, *args, **kwargs):
        try:
            self.process = subprocess.Popen([self.type, args], 
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE if self.stdout_enabled else None,
                                            **kwargs)
            return False, True
        except Exception as e:
            return repr(e), None
            
    # Schicke Zeichenketten = Kommandos zum Subprozess
    def write(self, lines):
        try:
            input_lines = Process.__convert_input(lines)
            if input_lines:
                # Übermitteln des Inputs an den Prozess
                stdout, stderr = self.process.communicate(input_lines)
                return (stderr, stdout)
            else:
                return(Exception('Der Input ist nicht zulässig'), None)
        except Exception as e:
            return repr(e), None
    
    # Win32 API TerminateProcess
    def kill(self):
        self.process.kill()
        
    # Win32 API TerminateProcess     
    def terminate(self):
        self.process.terminate()
        
    # Check if child process has terminated. Set and return returncode attribute.
    # Liefert einen Returncode
    def is_running(self):
        self.process.poll()
        
    # Wait for child process to terminate. Set and return returncode attribute.
    # WARNING:
    # This will deadlock when using stdout=PIPE and/or stderr=PIPE and the child 
    # process generates enough output to a pipe such that it blocks waiting for 
    # the OS pipe buffer to accept more data. Use communicate() to avoid that.
    def wait(self):
        self.process.wait()
        
    def get_return_code(self):
        return self.process.returncode
        
    def get_process_id(self):
        return self.process.pid
        
    def start_process(lines, **kwargs):
        obj = Process(**kwargs)
        obj.create()
        return obj.write(lines)
        
    def start_process_check(lines, **kwargs):
        obj = Process(**kwargs)
        obj.create()
        return obj.write_check(lines)
    
    def start_os_process(lines):
        try:
            return False, os.system(lines)
        except Exception as e:
            return repr(e), None

    def start_terminal(term, script):
#        cmdline = [term, "/q", "/k", "echo off"]
        obj = Process(**kwargs)
        obj.create()
        cmd.stdin.write(script)
        cmd.stdin.flush() # Must include this to ensure data is passed to child process
        return cmd.stdout.read()
            
    def test(lines):
        subprocess.check_output(lines)



"""
######################################
###    MAIN
######################################
"""
if __name__ == '__main__':

    notepad  = r'%windir%\system32\notepad.exe'
    testfile = r'\\corp.ergo\public\VPLeben\iLife\Python\DEV\StandardModule\script\test.cmd'
    
#    # Einzeiler (z.B. Datei öffnen mit einem Programm)
#    error, output = Process.start_os_process(notepad + ' ' + testfile)
    
    # Mehrezeiler (z.B. Skript ausführen)
    # Skript wird ausgeführt, der Terminal-Output wird NICHT eingefangen
    myScript = []
    myScript += ["echo hi"]
    myScript += ["cd /d H:\VPLeben\iLife\Tools"]
    myScript += ["dir"]
    
    
    # Muss getestet werden:
    '''
    proc = Process(stdout_enabled=True)
    err, data = proc.create2("/q", "/k", "echo off")
    err, data = proc.write(myScript)

    if err:
        print(str(err))
    if data:
        print(str(data.decode('iso-8859-9')))
    '''
    
    #error, data = Process.start_process(myScript, stdout_enabled=True)
    #print(data.decode('iso-8859-9'))
    


    

    


