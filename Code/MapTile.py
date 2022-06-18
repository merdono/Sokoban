import pygame

'''
;   @ - pemain.
;   $ - Box.
;   . - goal.
;   + - Pemain & goal
;   * - Box & goal
;  (space) - kosong
;   # - wall
'''

LEGENDS = ('$', '.', '@', '+', '*')

IMAGESDICT =   {'uncovered goal': pygame.image.load('Graphics\OFF_Selector.png'),
                'covered goal': pygame.image.load('Graphics\ON_Selector.png'),
                'box': pygame.image.load('Graphics\Box.png'),
                'corner': pygame.image.load('Graphics\Wall_2.png'),
                'wall': pygame.image.load('Graphics\Wall.png'),
                'inside floor': pygame.image.load('Graphics\InFloor.png'),
                'outside floor': pygame.image.load('Graphics\OutFloor.png'),
                'robot': pygame.image.load('Graphics\Robot.png')}

TILEMAPPING =   {'x': IMAGESDICT['corner'],
                 '#': IMAGESDICT['wall'],
                 'o': IMAGESDICT['inside floor'],
                 ' ': IMAGESDICT['outside floor']}

PLAYERIMAGES = IMAGESDICT['robot']