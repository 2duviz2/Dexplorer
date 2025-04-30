import pygame
import sys
import os
import win32api
import subprocess
import platform
import drives
import tempfile
import threading

pygame.init()

BLACK = (0, 0, 0)
LINE = (100, 100, 100)
colors = {
    "&Red&": (255, 0, 0),
    "&Green&": (0, 255, 0),
    "&Blue&": (0, 0, 255),
    "&Black&": (0, 0, 0),
    "&White&": (255, 255, 255),
    "&Folder&": (0, 0, 0),
    "&File&": (50, 50, 50),
    "&Image&": (25, 25, 75),
    "&Executable&": (75, 25, 25),
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
loadingImage = False
currentLoadingImage = None
t = threading.Thread()

popUpText = "Popup text"
popUpActive = False
popUpTransparency = 0
popUpTimer = 0
popup = pygame.font.Font('Font.ttf', 20)
popUpOffset = -10
popUpOffsetY = 0

def UpdateFolders():
    global text, folders, files, lines
    text = ""

    if rute != "":
        files, filesError = drives.listContent(rute, "files")
        folders, foldersError = drives.listContent(rute, "folders")
        if filesError or foldersError:
            setPopup("Failed to load content")
        if files != None:
            files.sort(key=str.lower)
        if folders != None:
            folders.sort(key=str.lower)

        if len(folders) > 0:
            for f in folders:
                text = text + "&Folder&" + f + "\n"
        if len(files) > 0:
            for f in files:
                fileTag = "&File&"
                if f.endswith(".png") or f.endswith(".jpeg") or f.endswith(".jpg"):
                    fileTag = "&Image&"
                if f.endswith(".exe") or f.endswith(".cmd") or f.endswith(".bat") or f.endswith(".msi"):
                    fileTag = "&Executable&"
                text = text + fileTag + f + "\n"
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
    global tempImage, tempImagePath, loadingImage
    if os.stat(r).st_size / (1024 * 1024) < 100: # If image is too big, don't load it
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                tempImagePath = temp_file.name
            tempImage = pygame.image.load(r)
            
            # get scale of tempImage
            width = tempImage.get_width() 
            height = tempImage.get_height()

            # get a ratio of the image with a max of 100
            if width > height:
                ratio = 100 / width
            else:
                ratio = 100 / height

            #NEW_SIZE = (100, 100) old formula
            NEW_SIZE = (int(width * ratio), int(height * ratio))
            rescaledImage = pygame.transform.scale(tempImage, NEW_SIZE)

            if currentLoadingImage != r: # checked before saving in case the image changes before, to save some time if the image is big
                loadImage(currentLoadingImage)
                return
            
            pygame.image.save(rescaledImage, tempImagePath)

            if currentLoadingImage != r: # checked after saving
                loadImage(currentLoadingImage)
                return
            
            tempImage = pygame.image.load(tempImagePath)
        except:
            tempImage = None
            tempImagePath = None
            # I probably should add a placeholder image here for when the image can't be loaded
    loadingImage = False

def deleteImage():
    global tempImage, tempImagePath
    if tempImagePath:
        os.remove(tempImagePath)
        tempImage = None
        tempImagePath = None

def setPopup(msg):
    global popUpText, popUpActive, popUpTransparency, popUpTimer, popUpOffsetY
    popUpText = msg
    popUpActive = True
    popUpTransparency = 255
    popUpTimer = 0
    if popUpOffset != -10:
        popUpOffsetY = 0

UpdateFolders()

yoffset = 0
yrealoffset = 0
xoffset = 0
cursor = 0
lastcursor = []
lastyrealoffset = []
yTop = 80
offsets = []
xCursorOffset = -30

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y < 0:
                cursor += 1
                yrealoffset -= font.get_height() + 5
                if not loadingImage:
                    deleteImage()
            else:
                cursor -= 1
                yrealoffset += font.get_height() + 5
                if not loadingImage:
                    deleteImage()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if cursor < len(folders):
                    rute = rute + folders[cursor] + "/"
                    lastcursor.reverse()
                    lastyrealoffset.reverse()
                    lastcursor.append(cursor)
                    lastyrealoffset.append(yrealoffset)
                    lastcursor.reverse()
                    lastyrealoffset.reverse()
                    cursor = 0
                    yrealoffset = 0
                    yoffset = 0
                    xoffset = 20
                    UpdateFolders()
                elif cursor < len(folders) + len(files):
                    openFileResult = drives.openFile(rute+files[cursor-len(folders)])
                    if openFileResult:
                        setPopup(f"Opened {files[cursor-len(folders)]}")
                    else:
                        setPopup(f"Couldn't open {files[cursor-len(folders)]}")
            if event.button == 3:
                rute = drives.deleteSlash(rute)
                if len(lastcursor) == 0:
                    lastcursor.append(0)
                    lastyrealoffset.append(0)
                cursor = lastcursor[0]
                yrealoffset = lastyrealoffset[0]
                yoffset = lastyrealoffset[0]
                lastcursor.pop(0)
                lastyrealoffset.pop(0)
                xoffset = 20
                UpdateFolders()
        elif event.type == pygame.KEYDOWN:
            Search(pygame.key.name(event.key))

    screen.blit(bg, (-2400/1.9, bgy-500))
    bgy = bgy - (bgy - bgrealy)/30
    bgrealy = yrealoffset/10
    if bgrealy < -2000:
        bgrealy = -2000

    if yrealoffset + yTop > 10:
        yoffset = yoffset - (yoffset - -yTop - 10)/15
    else:
        yoffset = yoffset - (yoffset - yrealoffset)/15
    xoffset = xoffset - (xoffset - 0)/10
    if yrealoffset > 0:
        yrealoffset = -(font.get_height() + 5) * (len(lines)-1)
        cursor = len(lines)-1
    y = yTop + yoffset
    l = 0
    c = 0

    if cursor >= len(lines): # if the cursor goes out of bounds, reset to the start
        yrealoffset = 0
        cursor = 0

    if len(lines) != len(offsets):
        offsets = []
        for i in range(len(lines)):
            offsets.append(0)

    for line in lines:
        if c < cursor-6 or c > cursor+20:
            l+=1
            c+=1
            if l >= 100:
                l = 0
            y += font.get_height() + 5
            continue
        color = BLACK
        cursorInLine = c == cursor
        cursorOffset = 0
        if cursorInLine:
            cursorOffset = xCursorOffset
            offsets[c] = offsets[c] - (offsets[c] - 35)/10
        else:
            offsets[c] = offsets[c] - (offsets[c] - 0)/10
        for tag in colors.keys():
            if line.startswith(tag):
                color = colors[tag]
                line = line[len(tag):]
                break
        if c == cursor:
            line = "> "+line
        rendered_text = font.render(line, True, color)
        screen.blit(rendered_text, (30+(xoffset*(y*.1)+offsets[c]+cursorOffset), y))
        rendered_text = lineFont.render(str(l), True, LINE)
        screen.blit(rendered_text, (0+(xoffset*(y*.1)), y))
        l+=1
        c+=1
        if l >= 100:
            l = 0
        
        y += font.get_height() + 5
    if cursor >= len(folders) and len(files) > 0:
        if str(files[cursor-len(folders)]).endswith(".png") or str(files[cursor-len(folders)]).endswith(".jpeg") or str(files[cursor-len(folders)]).endswith(".jpg"):
            if tempImage and not loadingImage:
                screen.blit(outline, (688, 288))
                screen.blit(tempImage, (690, 290))
            else:
                currentLoadingImage = rute+files[cursor-len(folders)]
                if not loadingImage:
                    loadingImage = True
                    t = threading.Thread(target=loadImage, args=(rute+files[cursor-len(folders)],))
                    t.start()
        else:
            if tempImage and not loadingImage:
                    deleteImage()
    
    if popUpActive:
        popUpTimer += 1
        if popUpTimer > 0:
            popUpTransparency += 10
        if popUpTransparency > 255:
            popUpTransparency = 255
        if popUpTimer > 500:
            popUpTransparency -= 15
        if popUpTransparency < 0:
            popUpTransparency = 0
            popUpActive = False
            popUpOffset = -10
            popUpTimer = 0
        rendered_text = popup.render(popUpText, True, (0, 0, 0))
        rendered_text.set_alpha(popUpTransparency)
        popUpOffset = popUpOffset - (popUpOffset - rendered_text.get_width()) / 10
        popUpOffsetY = popUpOffsetY - (popUpOffsetY - 0) / 10
        screen.blit(rendered_text, (790 - popUpOffset, 370 - popUpOffsetY))

    pygame.display.flip()

pygame.quit()
sys.exit()