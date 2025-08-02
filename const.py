import pygame
if not pygame.get_init():
    pygame.init()

WIDTH = 540
HEIGHT = 960
SPEED = 6.18125 # 1.0-10.0
WIDTH_SCALE = WIDTH / 540
HEIGHT_SCALE = HEIGHT / 960
HIT_SCALE = 0.23 * WIDTH_SCALE
Y = 100 * HEIGHT_SCALE
LINEWIDTH = 4 * WIDTH_SCALE
FONT = pygame.font.Font(".\\Resources\\fonts\\font.ttf", 75)