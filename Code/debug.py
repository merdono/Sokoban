import pygame
pygame.init()
#font = pygame.font.SysFont("chiller", 30)
font = pygame.font.Font("ALAGARD.TTF", 30)

def debug(info, y= 10, x = 10):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info),True,'White')
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pygame.draw.rect(display_surface,'Black', debug_rect)
    display_surface.blit(debug_surf,debug_rect)
