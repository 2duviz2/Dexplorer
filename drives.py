import sys
import os
import win32api
import subprocess
import platform

exceptFolders = ["$Recycle.Bin", "$RECYCLE.BIN"]
exceptFiles = []
exceptedExtensions = [".sys", ".tmp", ".dll", ".ini"]
allowedExtensions = [".exe", ".ink", ".url", ".png", ".jpg", ".jpeg", ".mp4", ".mp3"]

filterMode = "excepted" # allowed, excepted, none

def listContent(r, type):
    returning = []
    try:
        with os.scandir(r) as entry:
            for e in entry:
                if e.is_dir() and type == "folders":
                    if e.name in exceptFolders:
                        continue
                    returning.append(e.name)
                elif e.is_file() and type == "files":
                    if e.name in exceptFiles:
                        continue
                    if os.path.splitext(e.name)[1] in exceptedExtensions and filterMode == "excepted":
                        continue
                    if os.path.splitext(e.name)[1] not in allowedExtensions and filterMode == "allowed":
                        continue
                    returning.append(e.name)
            return returning
    except PermissionError:
        print(f"[{type}] Access denied trying to access: {r}")
        return returning
    
def openFile(file):
    try:
        if platform.system() == 'Windows':
            subprocess.Popen([file], cwd=os.path.dirname(file), shell=True)
            return True
        elif platform.system() == 'Linux':
            subprocess.Popen(['wine', 'cmd.exe', '/C', file], cwd=os.path.dirname(file))
            return True
        else:
            os.system(f"xdg-open {file}")
            return True
    except Exception as e:
        print(f"Couldn't open file {file}: {e}")
        return False

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