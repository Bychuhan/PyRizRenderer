import pygame
if not pygame.get_init():
    pygame.init()

WIDTH = 1080
HEIGHT = 1920
SPEED = 3.2 # 1.0-10.0
WIDTH_SCALE = WIDTH / 540
HEIGHT_SCALE = HEIGHT / 960
HIT_SCALE = 0.23 * WIDTH_SCALE
Y = 100 * HEIGHT_SCALE
LINEWIDTH = 4 * WIDTH_SCALE
FONT = pygame.font.Font(".\\Resources\\fonts\\font.ttf", 75)