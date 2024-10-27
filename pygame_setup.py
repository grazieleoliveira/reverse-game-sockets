import pygame
import constants as CONSTANTS

def pygame_setup():
    pygame.init()
    window = pygame.display.set_mode((CONSTANTS.WIDTH, CONSTANTS.HEIGHT))
    pygame.display.set_caption("Tabuleiro 8x8")
    font = pygame.font.SysFont('simhei', 20)  
    return window, font
