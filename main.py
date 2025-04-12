"""

My best project yet...

"""
import pygame,random,time
import data.engine as e
import data.menu as m
import data.Platformer as p
import json
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('Hydro Exodus')

level = m.get_data()['lg']

m.menu(level)
#p.level_3()
#p.cutscene_1()
#p.boss_fight()
#m.level_passed(p.level_2,3,300)