import pygame
import sys
import os
import win32api
import subprocess
import platform
import drives
import tempfile

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LINE = (100, 100, 100)
colors = {
    "&Red&": (255, 0, 0),
    "&Green&": (0, 255, 0),
    "&Blue&": (0, 0, 255),
    "&Black&": (0, 0, 0),
    "&White&": (255, 255, 255),
    "&Folder&": (0, 0, 0),
    "&File&": (50, 50, 50),
}

size = (800, 400)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Dexplorer")

bg = pygame.image.load('bg.png')
bg = pygame.transform.rotate(bg, 45)
bgy = -800
bgrealy = 0
outline = pygame.image.load('outline.png')

font = pygame.font.Font('Font.ttf', 30)
lineFont = pygame.font.Font('Font.ttf', 20)

text = ""
rute = ""
files = []
folders = []
lines = []

tempImage = None
tempImagePath = None

def UpdateFolders():
    global text, folders, files, lines
    text = ""

    if rute != "":
        files = drives.listContent(rute, "files")
        folders = drives.listContent(rute, "folders")
        if files != None:
            files.sort(key=str.lower)
        if folders != None:
            folders.sort(key=str.lower)

        if len(folders) > 0:
            for f in folders:
                text = text + "&Folder&" + f + "\n"
        if len(files) > 0:
            for f in files:
                text = text + "&File&" + f + "\n"
    else:
        folders = drives.drivesList()
        if len(folders) > 0:
            for f in folders:
                text = text + "&Folder&" + f + "\n"
                
    if text == "":
        text = "Nothing to display"
    UpdateWindowName()
    lines = text.splitlines()

def Search(s):
    global cursor, yrealoffset
    cc = 0
    fFound = False
    fFoundN = ""
    fFoundC = 0
    if len(folders) > 0:
        for f in folders:
            if str(f).lower().startswith(s.lower()):
                if not fFound:
                    fFound = True
                    fFoundN = f
                    fFoundC = cc
                canMoveCursor = False
                if len(folders) > cursor:
                    if cursor != cc and (cursor < cc or not str(folders[cursor]).lower().startswith(s)):
                        canMoveCursor = True
                if len(folders)+len(files) > cursor and not len(folders) > cursor:
                    if cursor != cc and (cursor < cc or not str(files[cursor-len(folders)]).lower().startswith(s)):
                        canMoveCursor = True

                if canMoveCursor:
                    cursor = cc
                    yrealoffset = -(font.get_height() + 5) * (cursor)
                    return
            cc+=1
    cc = 0
    if len(files) > 0:
        for f in files:
            if str(f).lower().startswith(s.lower()):
                if not fFound:
                    fFound = True
                    fFoundN = f
                    fFoundC = cc
                canMoveCursor = False
                if len(files) > cursor-len(folders) and cursor-len(folders) >= 0:
                    if cursor != cc+len(folders) and (cursor < cc+len(folders) or not str(files[cursor-len(folders)]).lower().startswith(s)):
                        canMoveCursor = True
                if len(files) > cursor-len(folders) and not cursor-len(folders) >= 0:
                    if cursor != cc+len(folders) and (cursor < cc+len(folders) or not str(folders[cursor]).lower().startswith(s)):
                        canMoveCursor = True

                if canMoveCursor:
                    cursor = cc+len(folders)
                    yrealoffset = -(font.get_height() + 5) * (cursor)
                    return
            cc+=1
    if fFound:
        cursor = fFoundC
        yrealoffset = -(font.get_height() + 5) * (cursor)

def UpdateWindowName():
    pygame.display.set_caption(f"Dexplorer > {rute}")

def loadImage(r):
    global tempImage, tempImagePath
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        tempImagePath = temp_file.name
    tempImage = pygame.image.load(r)
    
    NEW_SIZE = (100, 100)
    rescaledImage = pygame.transform.scale(tempImage, NEW_SIZE)
    
    pygame.image.save(rescaledImage, tempImagePath)
    
    tempImage = pygame.image.load(tempImagePath)

def deleteImage():
    global tempImage, tempImagePath
    if tempImagePath:
        os.remove(tempImagePath)
        tempImage = None
        tempImagePath = None

UpdateFolders()

yoffset = 0
yrealoffset = 0
xoffset = 0
cursor = 0
lastcursor = 0
lastyrealoffset = 0

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.MOUSEWHEEL:
            #yrealoffset += evento.y * 10
            if evento.y < 0:
                cursor += 1
                yrealoffset -= font.get_height() + 5
                deleteImage()
            else:
                cursor -= 1
                yrealoffset += font.get_height() + 5
                deleteImage()
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:
                if cursor < len(folders):
                    rute = rute + folders[cursor] + "/"
                    lastcursor = cursor
                    lastyrealoffset = yrealoffset
                    cursor = 0
                    yrealoffset = 0
                    yoffset = 0
                    xoffset = 20
                    UpdateFolders()
                elif cursor < len(folders) + len(files):
                    drives.openFile(rute+files[cursor-len(folders)])
            if evento.button == 3:
                rute = drives.deleteSlash(rute)
                #print(rute)
                #print(eliminar_penultimo_directorio(rute))
                cursor = lastcursor
                yrealoffset = lastyrealoffset
                yoffset = lastyrealoffset
                lastyrealoffset = 0
                lastcursor = 0
                xoffset = 20
                UpdateFolders()
        elif evento.type == pygame.KEYDOWN:
            Search(pygame.key.name(evento.key))

    screen.blit(bg, (-2400/1.9, bgy-500))
    bgy = bgy - (bgy - bgrealy)/30
    bgrealy = yrealoffset/10
    if bgrealy < -2000:
        bgrealy = -2000

    yoffset = yoffset - (yoffset - yrealoffset)/5
    xoffset = xoffset - (xoffset - 0)/10
    if yrealoffset > 0:
        yrealoffset = -(font.get_height() + 5) * (len(lines)-1)
        cursor = len(lines)-1
    y = 10 + yoffset
    l = 0
    c = 0
    #if cursor >= len(lines):
    #    cursor -= 1
    #    yrealoffset += font.get_height() + 5

    if cursor >= len(lines):
        yrealoffset = 0
        cursor = 0
    for line in lines:
        if c < cursor-6 or c > cursor+20:
            l+=1
            c+=1
            if l >= 100:
                l = 0
            y += font.get_height() + 5
            continue
        color = BLACK
        for tag in colors.keys():
            if line.startswith(tag):
                color = colors[tag]
                line = line[len(tag):]
                break
        if c == cursor:
            line = "> "+line
        rendered_text = font.render(line, True, color)
        screen.blit(rendered_text, (30+(xoffset*(y*.1)), y))
        rendered_text = lineFont.render(str(l), True, LINE)
        screen.blit(rendered_text, (0+(xoffset*(y*.1)), y))
        l+=1
        c+=1
        if l >= 100:
            l = 0
        
        y += font.get_height() + 5
    if cursor >= len(folders) and len(files) > 0:
        if str(files[cursor-len(folders)]).endswith(".png") or str(files[cursor-len(folders)]).endswith(".jpeg") or str(files[cursor-len(folders)]).endswith(".jpg"):
            if tempImage:
                screen.blit(outline, (688, 288))
                screen.blit(tempImage, (690, 290))
            else:
                loadImage(rute+files[cursor-len(folders)])
        else:
            if tempImage:
                deleteImage()

    pygame.display.flip()

pygame.quit()
sys.exit()
