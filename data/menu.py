import pygame, sys, json,time
import data.engine as e
import data.Platformer as p
from data.Platformer import ocean_sound,boss_music
from data.Platformer import create_vignette
import data.menu as m
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('Hydro Exodus')

WINDOW_SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the display

#ddisplay = pygame.Surface((300,200))
bg_list = [pygame.transform.scale(pygame.image.load("data/images/entities/menu/idle/idle_0.png"),WINDOW_SIZE),
           pygame.transform.scale(pygame.image.load("data/images/entities/menu/idle/idle_1.png"),WINDOW_SIZE),
           pygame.transform.scale(pygame.image.load("data/images/entities/menu/idle/idle_2.png"),WINDOW_SIZE),
           pygame.transform.scale(pygame.image.load("data/images/entities/menu/idle/idle_3.png"),WINDOW_SIZE)]

music = pygame.mixer.Sound("data/audio/music.wav")
music.set_volume(0.7)
game_over_sound = pygame.mixer.Sound('data/audio/game_over.wav')
game_over_sound.set_volume(0.8)

def start_level(number):
    if number == 1:
        p.level_2()
    elif number == 2:
        p.level_3()
    elif number == 3:
        p.level_4()
    elif number == 4:
        p.cutscene_1()

def menu(level):
    last_time = time.time()
    pos = 0
    dt = 0
    music.play(-1)
    font = pygame.font.Font('data/Peepo.ttf', 80)
    label_color = (255, 255, 255)
    ocean_sound.stop()
    label = font.render("Hydro Exodus", 1, label_color)
    #play = font.render('Play', 1, (0,0,0))
    #quit_label = font.render('Quit', 1, (0,0,0))
    playButton = pygame.transform.scale(pygame.image.load(f'data/images/green button.png'), (276,124))
    playButtonH = pygame.transform.scale(pygame.image.load('data/images/hover green button.png'), (276,124))
    playButtonRect = pygame.Rect(WINDOW_SIZE[0]/2-playButton.get_width()/2,320,playButton.get_width(),playButton.get_height())

    quitButton = pygame.transform.scale(pygame.image.load(f'data/images/red button.png'), (276,124))
    quitButtonH = pygame.transform.scale(pygame.image.load('data/images/hover red button.png'), (276,124))
    quitButtonRect = pygame.Rect(WINDOW_SIZE[0]/2-quitButton.get_width()/2,490,quitButton.get_width(),quitButton.get_height())
    bg_count = 0
    fps = 60
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 60
        last_time = time.time()

        if bg_count + 1 >= 27:
            bg_count = 0
        
        screen.blit(bg_list[bg_count//9],(0,0))
        bg_count += 1

        pos += 3*dt
        
        mx,my = pygame.mouse.get_pos()

        if playButtonRect.collidepoint((mx,my)):
            screen.blit(playButtonH,(playButtonRect.x,playButtonRect.y))
            play = font.render('Play', 1, (255,255,255))
        else:
            play = font.render('Play', 1, (0,0,0))
            screen.blit(playButton,(playButtonRect.x,playButtonRect.y))
        if quitButtonRect.collidepoint((mx,my)):
            screen.blit(quitButtonH,(quitButtonRect.x,quitButtonRect.y))
            quit_label = font.render('Quit', 1, (255,255,255))
        else:
            quit_label = font.render('Quit', 1, (0,0,0))
            screen.blit(quitButton,(quitButtonRect.x,quitButtonRect.y))

        screen.blit(label, (WINDOW_SIZE[0]/2-label.get_width()/2,50))
        #screen.blit(quitButton,(quitButtonRect.x,quitButtonRect.y))
        screen.blit(play, (playButtonRect.x+61,playButtonRect.y-7))
        screen.blit(quit_label,(quitButtonRect.x+69,quitButtonRect.y-4))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if playButtonRect.collidepoint((mx,my)):
                        music.stop()
                        ocean_sound.play()
                        start_level(level)
                    if quitButtonRect.collidepoint((mx,my)):
                        pygame.quit()
                        sys.exit()
        
        pygame.display.update()
        #clock.tick(60)

arrow_hover_img = pygame.transform.scale(pygame.image.load("data/images/hover arrow.png"),(128,64))
arrow_img = pygame.transform.scale(pygame.image.load("data/images/arrow.png"),(128,64))
coin_img = pygame.image.load("data/images/coin.png")

def blit_background():
    bg_count = 0
    if bg_count + 1 >= 27:
        bg_count = 0
    screen.blit(bg_list[bg_count//9],(0,0))
    bg_count += 1

def you_won():
    big_font = pygame.font.Font('data/Peepo.ttf', 100)
    label = big_font.render('YOU WON!!!!!',0,(0,255,0))
    while True:
        screen.fill((60,60,60))

        screen.blit(label,(WINDOW_SIZE[0]/2-label.get_width()/2,WINDOW_SIZE[1]/2-label.get_height()/2))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
        clock.tick(60)

def get_data():
    with open('data/data.json', 'r') as f:
        data = f.read()
        real_data = json.loads(data)
    return real_data

def update_data(level):
    real_data = get_data()
    real_data['lg'] = level

    with open('data/data.json', 'w') as f:
        json.dump(real_data, f)

def level_passed(level,level_number,next_levels):
    bbf = pygame.font.Font('data/Peepo.ttf', 100)
    big_font = pygame.font.Font('data/Peepo.ttf', 80)
    font = pygame.font.Font('data/Peepo.ttf', 75)
    label_color = (255,255,255)
    next_level = font.render("Next Level",1,label_color)
    ocean_sound.stop()
    label = bbf.render(f"Level {level_number} Passed!", 1, (93,255,120))
    label3 = big_font.render(f"Coins: ", 1, label_color)
    arrow_rect = pygame.Rect((WINDOW_SIZE[0]/2-arrow_img.get_width()/2)-180,270,arrow_img.get_width(),arrow_img.get_height())
    #vignette = create_vignette(WINDOW_SIZE)
    music.play(-1)

    update_data(int(next_levels))

    while True:
        blit_background()
        mx,my = pygame.mouse.get_pos()

        next_level_rect = pygame.Rect(arrow_rect.x+(next_level.get_width()-210),arrow_rect.y-30,next_level.get_width(),next_level.get_height())

        if arrow_rect.collidepoint((mx,my)) or next_level_rect.collidepoint((mx,my)):
            label_color = (255,255,255)
            next_level = font.render("Next Level",1,label_color)
            screen.blit(arrow_hover_img,(arrow_rect.x,arrow_rect.y))
        else:
            label_color = (0,0,0)
            next_level = font.render("Next Level",1,label_color)
            screen.blit(arrow_img,(arrow_rect.x,arrow_rect.y))
        

        screen.blit(label,((WINDOW_SIZE[0]/2-label.get_width()/2)+20,10))
        screen.blit(next_level,(next_level_rect.x,next_level_rect.y))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if arrow_rect.collidepoint((mx,my)):
                        music.stop()
                        level()
                    if next_level_rect.collidepoint((mx,my)):
                        music.stop()
                        level()

        pygame.display.update()
        clock.tick(60)

def gameOver(level_number,level,background=pygame.image.load('data/images/background1.png')):
    font = pygame.font.Font('data/Peepo.ttf', 80)
    smol_font = pygame.font.Font('data/Peepo.ttf', 75)
    label = font.render(f'GAME OVER', 1, (255,0,0))
    label_3 = smol_font.render('Continue?', 1, (255,255,255))
    ocean_sound.stop()
    boss_music.stop()
    #yes = smol_font.render('Yes',1,(0,0,0))
    #no = smol_font.render('No',1,(0,0,0))
    yesButton = pygame.transform.scale(pygame.image.load('data/images/green button.png'), (276,124))
    yesButtonH = pygame.transform.scale(pygame.image.load('data/images/hover green button.png'), (276,124))
    yesButtonRect = pygame.Rect(30,490,yesButton.get_width(),yesButton.get_height())

    noButton = pygame.transform.scale(pygame.image.load('data/images/red button.png'), (276,124))
    noButtonH = pygame.transform.scale(pygame.image.load('data/images/hover red button.png'), (276,124))
    noButtonRect = pygame.Rect(980,500,noButton.get_width(),noButton.get_height())
    game_over_sound.play()
    while True:
        screen.blit(pygame.transform.scale(background,WINDOW_SIZE),(0,0))

        mx,my = pygame.mouse.get_pos()
        if noButtonRect.collidepoint((mx,my)):
            screen.blit(noButtonH,(noButtonRect.x,noButtonRect.y))
            no = font.render('No', 1, (255,255,255))
        else:
            no = font.render('No', 1, (0,0,0))
            screen.blit(noButton,(noButtonRect.x,noButtonRect.y))

        if yesButtonRect.collidepoint((mx,my)):
            screen.blit(yesButtonH,(yesButtonRect.x,yesButtonRect.y))
            yes = font.render('Yes', 1, (255,255,255))
        else:
            yes = font.render('Yes', 1, (0,0,0))
            screen.blit(yesButton,(yesButtonRect.x,yesButtonRect.y))

        screen.blit(label, (WINDOW_SIZE[0]/2-label.get_width()/2,60))
        screen.blit(label_3, ((WINDOW_SIZE[0]/2-label_3.get_width()/2)-2,240))
        #screen.blit(yesButton,(yesButtonRect.x,yesButtonRect.y))
        #screen.blit(noButton,(noButtonRect.x,noButtonRect.y))
        screen.blit(yes,(yesButtonRect.x+38,yesButtonRect.y-6))
        screen.blit(no,(noButtonRect.x+50,noButtonRect.y-6))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if yesButtonRect.collidepoint((mx,my)):
                        level()
                    if noButtonRect.collidepoint((mx,my)):
                        m.menu(level_number)
        
        pygame.display.update()
        clock.tick(60)

