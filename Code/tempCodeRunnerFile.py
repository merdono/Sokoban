
import pygame, sys, copy
from pygame.locals import *
from settings import *
from MapTile import *

# Awal pembangunan
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("SOKOBAN Re+ with Python") #set_caption berguna untuk menggantikan nama judul window 
clock = pygame.time.Clock()
font = pygame.font.Font("Alagard.ttf", 22)

def main():
    startscreen()
    levels = readLevel('Sokoban.txt')
    currentlevel = 0
    #Main game Loop
    while True:
        result = runningLevel(levels, currentlevel)

        if result in ('solved', 'next'):
            currentlevel += 1
            if currentlevel >= len(levels):
                currentlevel = 0
        elif result =='back':
            currentlevel -= 1
            if currentlevel < 0:
                currentlevel = len(levels)-1

        elif result == 'reset':
            pass

def startscreen():
    bg = pygame.image.load("Graphics\StartScreen.png")
    Petunjuk =['Cara Bermain game:',
               'Bantulah robot merapikan lingkungannya dengan mendorong kotak.',
               'Tanda panah untuk bergerak, WASD untuk menggerakkan kamera.',
               'r untuk mengulangi level, Esc untuk keluar.',
               '(+) Untuk ganti level selanjutnya, (-) untuk ganti level sebelumnya']
    screen.blit(bg,(0,0))
    y_coord = 270
    for i in range(len(Petunjuk)):
        textsurf = font.render(Petunjuk[i], 1, TEXTCOLOR)
        textrect = textsurf.get_rect()
        y_coord += 20
        textrect.top = y_coord
        textrect.centerx = (WIDTH/2)
        y_coord += textrect.height
        screen.blit(textsurf,textrect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                Quit()
            elif event.type == KEYDOWN:
                if event.type == K_ESCAPE:
                    Quit()
                return
        pygame.display.update()
        clock.tick(FPS)


def readLevel(filename):
    mapFile = open(filename, 'r')
    level = mapFile.readlines() + ['\r\n']
    mapFile.close()
    levels = []
    levelnum = 0
    mapTextLines = []
    mapObj = []

    for lineNum in range(len(level)):
        line = level[lineNum].rstrip('\r\n')

        if ';' in line:
            line = line[:line.find(';')]
        
        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None
            starty = None
            goals = []
            boxes = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        boxes.append((x, y))
            
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelnum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelnum+1, lineNum, filename)
            assert len(boxes) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelnum+1, lineNum, filename, len(goals), len(boxes))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'boxes': boxes}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelnum += 1
    return levels

def floodFill(mapObj, x, y, karakter_lama, karakter_baru):
    if mapObj[x][y] == karakter_lama:
        mapObj[x][y] = karakter_baru
    
    if x < len(mapObj) - 1 and mapObj[x+1][y] == karakter_lama:
        floodFill(mapObj, x+1, y, karakter_lama, karakter_baru) # >
    if x > 0 and mapObj[x-1][y] == karakter_lama:
        floodFill(mapObj, x-1, y, karakter_lama, karakter_baru) # <
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == karakter_lama:
        floodFill(mapObj, x, y+1, karakter_lama, karakter_baru) # v
    if y > 0 and mapObj[x][y-1] == karakter_lama:
        floodFill(mapObj, x, y-1, karakter_lama, karakter_baru) # ^

def drawMap(mapObj, gameStateObj, goals):
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]

            mapSurf.blit(baseTile, spaceRect)

            if (x, y) in gameStateObj['boxes']:
                if (x, y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)

                mapSurf.blit(IMAGESDICT['box'], spaceRect)
            elif (x, y) in goals:

                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES, spaceRect)

    return mapSurf

def decorateMap(mapObj, startxy):
    startx, starty = startxy
    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in LEGENDS:
                mapObjCopy[x][y] = ' '
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] == '#':
                if  (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                    (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                    (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                    (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'
    return mapObjCopy

def runningLevel(levels, levelNum):
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapRedraw = True
    levelSurf = font.render('Level %s of %s'%(levelNum+1, len(levels)), 1, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, HEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    cam_x_pan = abs((HEIGHT/2)- int(mapHeight/2)) + TILEWIDTH
    cam_y_pan = abs((WIDTH/2)- int(mapWidth/2)) + TILEHEIGHT

    Complete = False

    cam_x_offset = 0
    cam_y_offset = 0

    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                Quit()
            
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_ESCAPE:
                    Quit()
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                elif event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.unicode == '+':
                    return 'next'
                elif event.unicode == '-':
                    return 'back'
                elif event.key == K_r:
                    return 'reset'

            elif event.type == KEYUP: #Only for camera
                if event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False
                elif event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
        
        if playerMoveTo != None and not Complete:
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                gameStateObj['stepCounter'] += 1
                mapRedraw = True
            
            if isLevelDone(levelObj, gameStateObj):
                Complete = True
                keyPressed = False
            
        screen.fill(GRAY)
        if mapRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            Redraw = False

        #Vertical Handler
        if cameraUp and cam_y_offset < cam_x_pan:
            cam_y_offset += CAM_SPEED
        elif cameraDown and cam_y_offset > -(cam_x_pan):
            cam_y_offset -= CAM_SPEED

        #Horizontal Handler
        if cameraLeft and cam_x_offset < cam_y_pan:
            cam_x_offset += CAM_SPEED
        elif cameraRight and cam_x_offset > -(cam_y_pan):
            cam_x_offset -= CAM_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = ((WIDTH/2) + cam_x_offset, (HEIGHT/2) + cam_y_offset)

        screen.blit(mapSurf, mapSurfRect)
        screen.blit(levelSurf, levelRect)
        
        #Move or step Counter
        moveSurf = font.render('Langkah: %s'% (gameStateObj['stepCounter']), 1, WHITE)
        moveRect = moveSurf.get_rect()
        moveRect.bottomleft = (20, HEIGHT - 10)
        screen.blit(moveSurf, moveRect)

#Here   
        if Complete:
            Level_Complete = pygame.image.load('Graphics\Victory.png')
            victorySurf = Level_Complete.get_rect()
            victorySurf.center = ((WIDTH/2), (HEIGHT/2)-50)
            screen.blit(Level_Complete, victorySurf)

            if keyPressed:
                return 'solved'

        pygame.display.update()
        clock.tick()

def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#', 'x'):
        return True
    return False

def isBlocked(mapObj, gameStateObj, x, y):
    if isWall(mapObj, x, y):
        return True
    elif x < 0 or x >=len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True

    elif (x, y) in gameStateObj['boxes']:
        return True
    
    return False

def makeMove(mapObj, gameStateObj, playerMoveTo):
    playerx, playery = gameStateObj['player']
    boxes = gameStateObj['boxes']
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0
    
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if(playerx + xOffset, playery + yOffset) in boxes:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                ind = boxes.index((playerx + xOffset, playery + yOffset))
                boxes[ind] = (boxes[ind][0] + xOffset, boxes[ind][1] + yOffset)
            else:
                return False
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True

def isLevelDone(levelObj, gameStateObj):
    for goal in levelObj['goals']:
        if goal not in gameStateObj['boxes']:
            return False
    return True

def Quit():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()