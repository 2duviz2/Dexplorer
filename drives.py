import sys
import os
import win32api
import subprocess
import platform

def listContent(r, type):
    returning = []
    try:
        with os.scandir(r) as entry:
            for e in entry:
                if e.is_dir() and type == "folders":
                    returning.append(e.name)
                elif e.is_file() and type == "files":
                    returning.append(e.name)
            return returning
    except PermissionError:
        print(f"[{type}] Access denied trying to access: {r}")
        return returning
    
def openFile(file):
    try:
        if platform.system() == 'Windows':
            subprocess.Popen([file], cwd=os.path.dirname(file), shell=True)
        elif platform.system() == 'Linux':
            subprocess.Popen(['wine', 'cmd.exe', '/C', file], cwd=os.path.dirname(file))
        else:
            os.system(f"xdg-open {file}")
    except Exception as e:
        print(f"Couldn't open file {file}: {e}")

def deleteSlash(rute):
    if rute.count('/') < 2:
        return ""
    
    ultima_barra = rute[:-1].rfind('/')
    
    if ultima_barra != -1:
        return rute[:ultima_barra+1]
    else:
        return rute
    
def drivesList():
    drives_list = []
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for drive in drives:
        drives_list.append(drive)
    return drives_list