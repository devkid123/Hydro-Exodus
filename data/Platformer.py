import pygame,sys,random,math,time,datetime
import data.menu as m
import data.engine as e
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('Hydro Exodus')

WINDOW_SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

def load_map(path):
    f = open(path + '.txt','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

e.load_animations('data/images/entities/')

grass_img = pygame.image.load('data/images/block/grass/grass.png')
full_grass_img = pygame.image.load('data/images/block/grass/full_grass.png')
top_corner_grass_img = pygame.image.load('data/images/block/grass/top_corner_grass.png')
left_grass_img = pygame.image.load('data/images/block/grass/left_grass.png')
right_grass_img = pygame.image.load('data/images/block/grass/right_grass.png')
top_left_grass_img = pygame.image.load('data/images/block/grass/left_top_grass.png')
top_right_grass_img = pygame.image.load('data/images/block/grass/right_top_grass.png')
sword_img = pygame.image.load('data/images/noob_sword.png')

dirt_img = pygame.image.load('data/images/block/grass/dirt.png')
full_dirt_img = pygame.image.load('data/images/block/grass/full_dirt.png')
left_dirt_img = pygame.image.load('data/images/block/grass/left_dirt.png')
right_dirt_img = pygame.image.load('data/images/block/grass/right_dirt.png')

finishline_img = pygame.image.load('data/images/finishline.png')

foods_list = [
    pygame.image.load('data/images/pizza.png'),
    pygame.image.load('data/images/strawberry.png'),
    pygame.image.load('data/images/cheesecake.png'),
    pygame.image.load('data/images/cookie.png'),
    pygame.image.load('data/images/chicken.png')
]

jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
jump_sound.set_volume(0.4)
powerup_sound = pygame.mixer.Sound('data/audio/powerUp.wav')
powerup_sound.set_volume(0.4)
ocean_sound = pygame.mixer.Sound('data/audio/ocean.wav')
ocean_sound.set_volume(0.2)
stamina_sound = pygame.mixer.Sound('data/audio/fill_stamina.wav')
stamina_sound.set_volume(0.6)
hit_sound = pygame.mixer.Sound('data/audio/hit.wav')
hit_sound.set_volume(0.6)
bg_music = pygame.mixer.Sound('data/audio/bg music.wav')
#bg_music.set_volume(0.9)
bg_music2 = pygame.mixer.Sound('data/audio/music2.wav')
bg_music2.set_volume(0.8)
lava_sound = pygame.mixer.Sound('data/audio/lava.wav')
lava_sound.set_volume(8)

grass_sounds = [pygame.mixer.Sound('data/audio/grass_0.wav'),pygame.mixer.Sound('data/audio/grass_1.wav')]
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)

music = pygame.mixer.Sound("data/audio/music.wav")
music.set_volume(0.7)

grass_sound_timer = 0

tile_dict = {}
image_cache = {}

font = pygame.font.Font('data/Peepo.ttf',18)
font_2 = pygame.font.Font('data/retro_computer_personal_use.ttf',18)

def render_textrect(string, font, rect, text_color):
    words = [word.split(' ') for word in string.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = rect.size

    lines = []
    for line in words:
        for word in line:
            if lines:
                if font.size(' '.join(lines[-1] + [word]))[0] <= max_width:
                    lines[-1].append(word)
                else:
                    lines.append([word])
            else:
                lines.append([word])

    y = rect.top
    for line in lines:
        text_surface = font.render(' '.join(line), False, text_color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (rect.left + max_width // 2, y)
        display.blit(text_surface, text_rect)
        y += font.size('Tg')[1]

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))


def display_dialogue(dialogues,text_color=(0,0,0)):
    img = pygame.transform.scale(pygame.image.load('data/images/dialogues/dialogue_box.png'), (295, 120)).convert_alpha()
    x, y = 300 / 2 - img.get_width() / 2, 80

    text_rect = pygame.Rect(x + 10, y + 30, img.get_width() - 20, img.get_height() - 20)

    dialogue_blip = pygame.mixer.Sound(f'data/audio/boy_dialogue_blip.ogg')
    dialogue_blip.set_volume(0.3)

    flag = True

    # Iterate over each dialogue in the list
    for dialogue in dialogues:
        text = dialogue['text']
        wait_time = 1400

        text_complete = False
        play_sound = False

        # Render each character of the text one by one
        for i in range(len(text) + 1):  # Adding 1 to include full text rendering
            display.blit(img, (x, y))
            render_textrect(text[:i], font, text_rect, text_color)
            pygame.display.update()
            time.sleep(0.045)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

            # Once the entire text has been rendered
            if i == len(text):
                text_complete = True
                flag = False
                break

            if not play_sound:
                dialogue_blip.play()
                play_sound = True

        if text_complete:
            dialogue_blip.stop()
            play_sound = False
            
        # Wait for the set amount of time (can be adjusted)
        pygame.time.wait(wait_time)


def draw_text(screen,font,text, pos):
    label = font.render(text, True, (255,255,255))
    screen.blit(label, pos)

def create_vignette(size, intensity=150, color=(0, 0, 0)):
    vignette = pygame.Surface(size, pygame.SRCALPHA)  # Create transparent surface
    width, height = size
    center_x, center_y = width // 2, height // 2
    max_distance = math.sqrt(center_x ** 2 + center_y ** 2)

    # Loop over every pixel of the surface
    for x in range(width):
        for y in range(height):
            distance_to_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            distance_factor = distance_to_center / max_distance

            alpha = min(255, int(distance_factor * intensity))

            vignette.set_at((x, y), (*color, alpha))

    return vignette

def generate_particles(display,particles,coords,radius,scroll):
    counter = 0
    particles.append([coords,[random.randint(0,10)/10-1,-2],radius])
    for particle in particles:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.1
        particle[1][1] += 0.1
        pygame.draw.circle(display, (255, 0, 0), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
        if particle[2] <= 0:
            particles.remove(particle)

def spawn_food(foods,foods_coords,scroll,player,stamina_rect):
    for i in range(len(foods) - 1, -1, -1):
        count = 0
        coords = foods_coords[i]
        food_rect, food_img, sound_played = foods[i]

        ey = coords[1] - scroll[1]
        display.blit(food_img, (coords[0] - scroll[0], ey))
        # If the player collides with the food
        if player.obj.rect.colliderect(food_rect):
            # Only play the sound if it hasn't been played yet for this food
            if not sound_played:
                stamina_sound.play()  # Play the sound
                foods[i] = (food_rect, food_img, True)  # Mark the sound as played

            # Increase stamina
            if abs(stamina_rect.width - 126) >= 40:
                stamina_rect.width += 40
            elif abs(stamina_rect.width - 126) < 40:
                stamina_rect.width += abs(stamina_rect.width - 126)

            # Remove the food from the list after the player collects it
            del foods[i]
            del foods_coords[i]

def draw_sword(screen, original_sword_img, sword_x, sword_y, mouse_pos, scroll, sword_flip):
    # Adjust the mouse position for camera scroll
    rel_x, rel_y = (mouse_pos[0] + scroll[0]) - sword_x, (mouse_pos[1] + scroll[1]) - sword_y
    angle = math.degrees(math.atan2(-rel_y, rel_x))  # Calculate the angle for rotation

    # Rotate the sword image from the original (unrotated) high-res image
    rotated_sword = pygame.transform.rotate(original_sword_img, angle)

    # Flip the sword image if sword_flip is True
    if sword_flip:
        rotated_sword = pygame.transform.flip(rotated_sword, True, False)  # Horizontal flip only

    # Adjust the sword's position according to the camera scroll
    sword_rect = rotated_sword.get_rect(center=(sword_x - scroll[0], sword_y - scroll[1]))

    # Draw the rotated and flipped sword on the screen
    screen.blit(rotated_sword, sword_rect.topleft)

with open('data/images/block/tile/tiles.txt', 'r') as f:
    file_ = str(f.read())

last_time = time.time()
pos = 0
dt = 0
def level_1():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll, ocean_rect

    player = e.entity(768, 1632, 32, 32, 'player')
    bg1 = pygame.image.load('data/images/background1.png')
    game_map = load_map('data/map/map1')
    ocean = pygame.image.load('data/images/ocean.png')

    previous_player_y = player.obj.rect.y
    water_rise_speed = 0.8
    
    true_scroll = [768,1632]
    font = pygame.font.Font('data/Peepo.ttf', 10)
    counter = 0
    
    # Fixing ocean rect initialization
    ocean_rect2 = pygame.Rect(ocean_rect.x, ocean_rect.y + 120, ocean_rect.width, ocean_rect.height)

    foods_coords = [(704,416)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    display_food = True
    stamina_reduce_speed = 2
    ocean_sound.play(-1)
    bg_music.play(-1)
    d = 0
    while True:
        display.blit(bg1, (0, 0))

        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        # Update scroll with player movement
        true_scroll[0] += (player.obj.rect.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.obj.rect.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    display.blit(dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '2':
                    display.blit(grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == 'i':
                    display.blit(finishline_img, (x * 32 - scroll[0], y * 32 - scroll[1]))

                if tile != '0' and tile != 'i' and tile != 's' and tile != 'f':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                #if tile == 'f':
                #    print(x*32,y*32)
                if tile == 'i':
                    rect = pygame.Rect(x * 32, y * 32, 32, 32)
                    if player.obj.rect.colliderect(rect):
                        ocean_sound.stop()
                        bg_music.stop()
                        player.set_pos(736,992)
                        moving_right = False
                        moving_left = False
                        m.level_passed(level_2,1,2)
                x += 1
            y += 1

        c = 0
        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            air_timer = 0
            vertical_momentum = 0
        else:
            air_timer += 1

        player.change_frame(1)
        player.display(display, scroll)

        spawn_food(foods,foods_coords,scroll,player,stamina_rect)

        # Sync player rect with scroll (correct collision position)
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        falling_down = 2
        if player.y < previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y += (previous_player_y - player.y) * 0.3  # Lower the water based on the amount player has moved up
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down  # Player is moving up
        elif player.y > previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y -= water_rise_speed
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down
        elif vertical_momentum == 3:
            ocean_rect.y -= falling_down

        previous_player_y = player.y

        ocean.set_alpha(160)
        ocean_rect2 = pygame.Rect(ocean_rect.x, ocean_rect.y + 110, ocean_rect.width, ocean_rect.height)

        display.blit(ocean, (0, ocean_rect.y))

        # Sync ocean rect for collision with scroll
        ocean_rect_scaled = pygame.Rect(
            ocean_rect.x,
            ocean_rect.y,
            ocean_rect.width,
            ocean_rect.height
        )

        if player_rect_scaled.colliderect(ocean_rect2):
            ocean_sound.stop()
            bg_music.stop()
            player.set_pos(736,992)
            moving_right = False
            moving_left = False
            m.gameOver(level_1)

        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    c += stamina_reduce_speed
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_momentum = -6.5
            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False

        stamina_rect.width -= c
        if stamina_rect.width <= 15:
            display.blit(vignette, (0, 0))
        if stamina_rect.width == 0:
            player.set_pos(736,992)
            moving_right = False
            moving_left = False
            ocean_sound.stop()
            m.gameOver(level_3)
        # Blit scaled display onto the screen
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)
coins = 0
def level_2():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,coins,last_time,pos,dt

    player = e.entity(224,3328,32,32,'player')
    bg1 = pygame.image.load('data/images/background1.png')
    game_map = load_map('data/map/map2')
    ocean = pygame.image.load('data/images/ocean.png')
    #blit_transparent = False
    previous_player_y = player.y  # Track player's previous y position
    water_rise_speed = 0.6  # Speed at which the water rises if the player isn't moving up
    jump_count = 0
    jump_boost = False
    true_scroll = [224,3328]
    super_jump = e.entity(32,2688,16,16,'jump')
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',10)
    text = font.render('Collect for Jump Boost',True,(255,255,255))
    ocean_rect = pygame.Rect(0, 180, ocean.get_width(), ocean.get_height())

    enemy_coords = [(928,640),(960,1120),(544,1792),(960,2944)]
    enemies = []
    for coord in enemy_coords:
        enemies.append((e.entity(coord[0],coord[1],32,32,'enemy'),False,60))

    foods_coords = [(768,512),(672,1120),(448,2464)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect2 = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    stamina_reduce_speed = 2
    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    
    bullet_timer = 0
    bullets = []
    bullet_speed = 2
    blit_rect = True
    render_offset = [0,0]
    shake = 0
    particles = []
    ocean_sound.play(-1)
    bg_music.play(-1)
    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    decrease_enemy_health = 30
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)
    enemy_coins_gained = random.randint(20,120)
    coin_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin_alpha = 255

    coin2_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin2_alpha = 255
    coins = 0
    
    damage_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage_alpha = 255
    display_damage = False
    enemy_killed = False
    show_red = False
    mouse_clicked = False
    mouse_released = True
    count = 0
    fps = 60
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 60
        last_time = time.time()

        display.blit(bg1, (0, 0))

        pos += 3*dt
        # display.fill((146,244,255))

        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
    
        if shake > 0:
            shake -= 1
        if shake:
            scroll[0] += random.randint(0,8) - 4
            scroll[1] += random.randint(0,8) - 4

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    display.blit(dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '2':
                    display.blit(grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '3':
                    display.blit(right_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '4':
                    display.blit(right_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '5':
                    display.blit(left_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '6':
                    display.blit(left_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '7':
                    display.blit(top_right_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '8':
                    display.blit(top_left_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == 'g':
                    display.blit(top_corner_grass_img,(x*32-scroll[0],y*32-scroll[1]))
                if tile == 'd':
                    display.blit(full_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == 'i':
                    display.blit(finishline_img, (x * 32-scroll[0], y * 32-scroll[1]))
                if tile != '0' and tile != 'i' and tile != 'f' and tile != 'e' and tile != '#':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                
                if tile == '#':
                    rect_ = pygame.Rect(x * 32, y * 32, 32,32)
                    if player.obj.rect.colliderect(rect_):
                        player.set_pos(224,3328)
                        moving_right = False
                        moving_left = False
                        ocean_sound.stop()
                        m.gameOver(1,level_2)

                if tile == 'i':
                    rect = pygame.Rect(x * 32, y * 32, 32, 32)
                    if player.obj.rect.colliderect(rect):
                        ocean_sound.stop()
                        bg_music.stop()
                        player.set_pos(224,3328)
                        moving_right = False
                        moving_left = False
                        m.level_passed(level_3,1,2)
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_flip(True)
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        else:
            air_timer += 1
        
        if blit_jump:
            super_jump.change_frame(1)
            super_jump.display(display, scroll)
        player.change_frame(1)
        player.display(display, scroll)
        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)

        if player.obj.rect.colliderect(super_jump.obj.rect):
            start_time = time.time()
            counter += 0.5
            if counter == 1:
                powerup_sound.play()
            blit_jump = False
            jump_boost = True
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        spawn_food(foods,foods_coords,scroll,player,stamina_rect)
        
        if show_red:
            count += 1  # Increment count only if show_red is True

            # Show the vignette for the first 16 frames (or ticks)
            if count < 14:
                display.blit(red_vignette, (0, 0))
            else:
                show_red = False  # Stop showing the vignette after 16 frames
                count = 0
        
        bullet_timer += 1

        if bullet_timer >= 150:
            for i in range(len(enemies) - 1, -1, -1):  
                coords = enemy_coords[i]
                enemy,sound_played,enemy_health = enemies[i]

                # Spawn a bullet from each enemy after 30 frames
                bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': False}  # You can adjust direction as needed
                bullets.append(bullet)

            bullet_timer = 0  # Reset timer after bullets are spawned

        for coords in enemy_coords:
            if not enemy_killed:
                coin_alpha = 255
                coin_text.set_alpha(coin_alpha)

            if enemy_killed:
                coins = coins+enemy_coins_gained
                display.blit(coin_text,((coords[0])-scroll[0],(coords[1]-20)-scroll[1]))
                coin_text.set_alpha(coin_alpha)
                coin_alpha -= 1
                if coin_alpha < 0:
                    coin_alpha = 0
                    enemy_killed = False

            if not display_damage:
                damage_alpha = 255
                damage_text.set_alpha(damage_alpha)
            
            if display_damage:
                display.blit(damage_text,((coords[0]-26)-scroll[0],(coords[1]-10)-scroll[1]))
                damage_text.set_alpha(damage_alpha)
                damage_alpha -= 1
                if damage_alpha < 0:
                    damage_alpha = 0
                    display_damage = False

        for i in range(len(enemies) - 1, -1, -1):  
            coords = enemy_coords[i]
            enemy, sound_played, enemy_health = enemies[i]

            if blit_rect and bullet_timer > 0 or bullet_timer < 0:
                enemy.change_frame(1)
                enemy.display(display, scroll)
            
            #enemy_healthbar = pygame.Rect(enemy.x-scroll[0], (enemy.y - 15)-scroll[1], 30, 4)
            enemy_rect = pygame.Rect(coords[0], coords[1], 32, 32)

            if enemy_health == 0:
                enemy_killed = True
                #del enemy_coords[i]
                del enemies[i]
                continue

            if sword_rect.colliderect(enemy_rect):
                if mouse_clicked and mouse_released:
                    if not sound_played:
                        hit_sound.play()
                        enemies[i] = (enemy, True, enemy_health)  # Update sound_played status

                    enemy_health -= decrease_enemy_health
                    display_damage = True
                    shake = 21

                    enemies[i] = (enemy, sound_played, enemy_health)

                    mouse_released = False  # Lock to prevent continuous decrease until mouse is released

            # Check if the mouse button has been released
            if not mouse_clicked:
                mouse_released = True

        bullets_to_remove = []

        for bullet in bullets[:]:
            bx = bullet_speed * bullet['direction']  
            bullet['rect'].x -= bx  # Move the bullet

            pygame.draw.rect(display, (255, 0, 0), pygame.Rect(bullet['rect'].x - scroll[0], bullet['rect'].y - scroll[1], 8, 4))

            if player.obj.rect.colliderect(bullet['rect']):
                show_red = True
                hearts -= 1  # Mark bullet for removal
                heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                display.blit(heart_img,(10,180))

                if hearts <= 0:
                    player.set_pos(224,3328)
                    moving_right = False
                    moving_left = False
                    ocean_sound.stop()
                    bg_music.stop()
                    m.gameOver(1,level_2)
                    
                bullets.remove(bullet)
                shake = 10
                if not bullet['sound']:
                    hit_sound.play()
                    bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': True}
                    bullets.append(bullet)
                
            
            if bullet['rect'].x < 0 or bullet['rect'].x > WINDOW_SIZE[0]:
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            bullets.remove(bullet)
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))

        falling_down = 1.2
        if player.y < previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y += (previous_player_y - player.y) * 0.4  # Lower the water based on the amount player has moved up
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down  # Player is moving up
        elif player.y > previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y -= water_rise_speed
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down
        elif vertical_momentum == 3:
            ocean_rect.y -= falling_down

        previous_player_y = player.y

        ocean.set_alpha(160)
        ocean_rect2 = pygame.Rect(ocean_rect.x, ocean_rect.y + 120, ocean_rect.width, ocean_rect.height)

        display.blit(ocean, (0, ocean_rect.y))

        # Sync ocean rect for collision with scroll
        ocean_rect_scaled = pygame.Rect(
            ocean_rect.x,
            ocean_rect.y,
            ocean_rect.width,
            ocean_rect.height
        )

        if player_rect_scaled.colliderect(ocean_rect2):
            player.set_pos(224,3328)
            moving_right = False
            moving_left = False
            ocean_sound.stop()
            bg_music.stop()
            m.gameOver(1,level_2)

        pygame.draw.rect(display,(31, 76, 112),stamina_rect2)
        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))
        c = 0        
        display.blit(text,(38-scroll[0],(super_jump.x-30)-scroll[1]))
        display.blit(heart_img,(10,180))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        c += stamina_reduce_speed
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -6.5

                    if jump_boost:
                        jump_count += 1

                        if time.time() - start_time < 35:
                            if jump_count > 0 and jump_count < 3:
                                c += stamina_reduce_speed
                                vertical_momentum = -6.5
                                jump_sound.play()
                            
                            if air_timer < 6:
                                
                                vertical_momentum = -6
                                jump_sound.play()
                        else:
                            c += stamina_reduce_speed
                            if air_timer < 6:
                                jump_sound.play()
                                vertical_momentum = -6.5

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False
                    
        stamina_rect.width -= c
        if stamina_rect.width <= 20:
            display.blit(vignette, render_offset)
        if stamina_rect.width == 0:
            player.set_pos(224,3328)
            moving_right = False
            moving_left = False
            ocean_sound.stop()
            m.gameOver(1,level_2)

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), render_offset)
        pygame.display.update()

def level_3():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,coins,last_time,pos,dt

    player = e.entity(512,4256,32,32,'player')
    bg1 = pygame.image.load('data/images/background1.png')
    game_map = load_map('data/map/map3')
    ocean = pygame.image.load('data/images/ocean.png')
    #blit_transparent = False
    previous_player_y = player.y  # Track player's previous y position
    water_rise_speed = 0.6  # Speed at which the water rises if the player isn't moving up
    jump_count = 0
    jump_boost = False
    true_scroll = [512,4256]
    super_jump = e.entity(32,1000,16,16,'jump')
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',10)
    text = font.render('Collect for Jump Boost',True,(255,255,255))
    ocean_rect = pygame.Rect(0, 190, ocean.get_width(), ocean.get_height())

    # !!!!! Add diffferent coords these are 2nd level ones bro !!!!! - done
    enemy_coords = [(960,192),(736,672),(512,1536),(704,2688),(864,3296),(352,3680)]
    enemies = []
    for coord in enemy_coords:
        enemies.append((e.entity(coord[0],coord[1],32,32,'enemy'),False,60))

    foods_coords = [(736, 288),(640,1248),(352,2400),(64,2976),(416,3072)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    stamina_rect2 = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    stamina_reduce_speed = 2
    
    ocean_sound.play(-1)
    bullet_timer = 0
    bullets = []  # List to store bullets
    bullet_speed = 2  # Speed of bullets
    blit_rect = True
    start_time = 0

    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    shake = 0
    bg_music.play(-1)

    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    mouse_clicked = False
    mouse_released = True
    show_red = False
    count = 255
    decrease_enemy_health = 30
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)
    
    enemy_coins_gained = random.randint(20,120)
    coin_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin_alpha = 255
    
    damage_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage_alpha = 255
    display_damage = False
    enemy_killed = False
    coins = 0
    fps = 60
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 60
        last_time = time.time()

        display.blit(bg1, (0, 0))

        pos += 3*dt
        if grass_sound_timer > 0:
            grass_sound_timer -= 1

        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if shake > 0:
            shake -= 1
        if shake:
            scroll[0] += random.randint(0,8) - 4
            scroll[1] += random.randint(0,8) - 4

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    display.blit(dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '2':
                    display.blit(grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '3':
                    display.blit(right_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '4':
                    display.blit(right_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '5':
                    display.blit(left_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '6':
                    display.blit(left_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '7':
                    display.blit(top_right_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == '8':
                    display.blit(top_left_grass_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                if tile == 'i':
                    display.blit(finishline_img, (x * 32-scroll[0], y * 32-scroll[1]))
                if tile == 'g':
                    display.blit(top_corner_grass_img,(x*32-scroll[0],y*32-scroll[1]))
                if tile == 'd':
                    display.blit(full_dirt_img, (x * 32 - scroll[0], y * 32 - scroll[1]))
                #if tile == 'f':
                #   print(f"Food: {(x*32,y*32)}")
                #if tile == 'e':
                #   print(f"Enemy: {(x*32,y*32)}")
                #if tile == 'p':
                #    print(f"Player: {(x*32,y*32)}")
                if tile != '0' and tile != 'i' and tile != 'f' and tile != 'e' and tile != '#':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                if tile == '#':
                    rect_ = pygame.Rect(x * 32, y * 32, 32,32)
                    if player.obj.rect.colliderect(rect_):
                        player.set_pos(512,4256)
                        moving_right = False
                        moving_left = False
                        ocean_sound.stop()
                        bg_music.stop()
                        m.gameOver(2,level_3)

                if tile == 'i':
                    rect = pygame.Rect(x * 32, y * 32, 32, 32)
                    if player.obj.rect.colliderect(rect):
                        ocean_sound.stop()
                        bg_music.stop()
                        player.set_pos(512,4256)
                        moving_right = False
                        moving_left = False
                        m.level_passed(level_4,2,3)
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        else:
            air_timer += 1
        
        if blit_jump:
            super_jump.change_frame(1)
            super_jump.display(display, scroll)

        player.change_frame(1)
        player.display(display, scroll)

        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)
        
        if show_red:
            count += 1
            if count < 14:
                display.blit(red_vignette, (0, 0))
            else:
                show_red = False  # Stop showing the vignette after 16 frames
                count = 0
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))

        if player.obj.rect.colliderect(super_jump.obj.rect):
            start_time = time.time()
            counter += 0.5
            if counter == 1:
                powerup_sound.play()
            blit_jump = False
            jump_boost = True
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        spawn_food(foods,foods_coords,scroll,player,stamina_rect)

        bullet_timer += 1

        if bullet_timer >= 150:
            for i in range(len(enemies) - 1, -1, -1):  
                coords = enemy_coords[i]
                enemy,sound_played,enemy_health = enemies[i]

                # Spawn a bullet from each enemy after 30 frames
                bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': False}  # You can adjust direction as needed
                bullets.append(bullet)

            bullet_timer = 0  # Reset timer after bullets are spawned

        for coords in enemy_coords:
            if not enemy_killed:
                coin_alpha = 255
                coin_text.set_alpha(coin_alpha)

            if enemy_killed:
                coins = coins+enemy_coins_gained
                display.blit(coin_text,((coords[0])-scroll[0],(coords[1]-20)-scroll[1]))
                coin_text.set_alpha(coin_alpha)
                coin_alpha -= 1
                if coin_alpha < 0:
                    coin_alpha = 0
                    enemy_killed = False

            if not display_damage:
                damage_alpha = 255
                damage_text.set_alpha(damage_alpha)
            
            if display_damage:
                display.blit(damage_text,((coords[0]-26)-scroll[0],(coords[1]-10)-scroll[1]))
                damage_text.set_alpha(damage_alpha)
                damage_alpha -= 1
                if damage_alpha < 0:
                    damage_alpha = 0
                    display_damage = False
        

        for i in range(len(enemies) - 1, -1, -1):  
            coords = enemy_coords[i]
            enemy, sound_played, enemy_health = enemies[i]

            if blit_rect and bullet_timer > 0 or bullet_timer < 0:
                enemy.change_frame(1)
                enemy.display(display, scroll)
            
            #enemy_healthbar = pygame.Rect(enemy.x-scroll[0], (enemy.y - 15)-scroll[1], 30, 4)
            enemy_rect = pygame.Rect(coords[0], coords[1], 32, 32)

            if enemy_health == 0:
                enemy_killed = True
                del enemy_coords[i]
                del enemies[i]
                continue

            if sword_rect.colliderect(enemy_rect):
                if mouse_clicked and mouse_released:
                    if not sound_played:
                        hit_sound.play()
                        enemies[i] = (enemy, True, enemy_health)  # Update sound_played status

                    enemy_health -= decrease_enemy_health
                    display_damage = True
                    shake = 21

                    enemies[i] = (enemy, sound_played, enemy_health)

                    mouse_released = False  # Lock to prevent continuous decrease until mouse is released

            # Check if the mouse button has been released
            if not mouse_clicked:
                mouse_released = True

        bullets_to_remove = []

        for bullet in bullets[:]:
            bx = bullet_speed * bullet['direction']  
            bullet['rect'].x -= bx  # Move the bullet

            pygame.draw.rect(display, (255, 0, 0), pygame.Rect(bullet['rect'].x - scroll[0], bullet['rect'].y - scroll[1], 8, 4))

            if player.obj.rect.colliderect(bullet['rect']):
                show_red = True
                hearts -= 1  # Mark bullet for removal
                heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                display.blit(heart_img,(10,180))

                if hearts <= 0:
                    player.set_pos(512,4256)
                    moving_right = False
                    moving_left = False
                    ocean_sound.stop()
                    bg_music.stop()
                    m.gameOver(2,level_3)
                    
                bullets.remove(bullet)
                shake = 10
                if not bullet['sound']:
                    hit_sound.play()
                    bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': True}
                    bullets.append(bullet)
                
            
            if bullet['rect'].x < 0 or bullet['rect'].x > WINDOW_SIZE[0]:
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        falling_down = 1.3
        if player.y < previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y += (previous_player_y - player.y) * 0.3  # Lower the water based on the amount player has moved up
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down  # Player is moving up
        elif player.y > previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y -= water_rise_speed
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down
        elif vertical_momentum == 3:
            ocean_rect.y -= falling_down

        previous_player_y = player.y

        ocean.set_alpha(160)
        ocean_rect2 = pygame.Rect(ocean_rect.x, ocean_rect.y + 120, ocean_rect.width, ocean_rect.height)

        display.blit(ocean, (0, ocean_rect.y))

        ocean_rect_scaled = pygame.Rect(
            ocean_rect.x,
            ocean_rect.y,
            ocean_rect.width,
            ocean_rect.height
        )
        
        if player_rect_scaled.colliderect(ocean_rect2):
            player.set_pos(512,4256)
            moving_right = False
            moving_left = False
            ocean_sound.stop()
            bg_music.stop()
            m.gameOver(2,level_3)
        
        pygame.draw.rect(display,(31, 76, 112),stamina_rect2)
        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))
        c = 0
        display.blit(text,(38-scroll[0],950-scroll[1]))
        display.blit(heart_img,(10,180))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        c += stamina_reduce_speed
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -6.5

                    if jump_boost:
                        jump_count += 1

                        while time.time() - start_time < 35:
                            if jump_count > 0 and jump_count < 3:
                                vertical_momentum = -6.5
                                jump_sound.play()
                            
                            if air_timer < 6:
                                vertical_momentum = -6
                                jump_sound.play()

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False
                    
        stamina_rect.width -= c
        if stamina_rect.width <= 15:
            display.blit(vignette, (0, 0))
        if stamina_rect.width == 0:
            player.set_pos(512,4256)
            moving_right = False
            moving_left = False
            ocean_sound.stop()
            bg_music.stop()
            m.gameOver(2,level_3)
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        #clock.tick(80)

def level_4():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,last_time,pos,dt,coins

    for line in file_.splitlines():
        a, b = line.split(' ', 1)  # Split each line into key and value
        tile_dict[a] = b
    
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)

    player = e.entity(448,3264,32,32,'player')
    bg2 = pygame.image.load('data/images/background2.png')
    game_map = load_map('data/map/map4')
    ocean = pygame.image.load('data/images/lava.png')
    #blit_transparent = False
    previous_player_y = player.y  # Track player's previous y position
    water_rise_speed = 0.4
    jump_count = 0
    jump_boost = False
    true_scroll = [448,3264]
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',12)
    text = font.render('Collect for Jump Boost',True,(255,255,255))

    # !!!!! Add diffferent coords these are 3rd level ones bro !!!!! - done
    enemy_coords = [(864, 1312),(800,1888),(960,3104),(480,160),(928,544),(736,928)]
    enemies = []
    for coord in enemy_coords:
        enemies.append((e.entity(coord[0],coord[1],32,32,'enemy'),False,60))
    bullet_timer = 0
    bullets = []
    bullet_speed = 2
    decrease_enemy_health = 30
    damage_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage_alpha = 255
    display_damage = False
    enemy_killed = False
    enemy_coins_gained = random.randint(20,120)
    coin_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin_alpha = 255

    ocean_rect = pygame.Rect(0, 185, ocean.get_width(), ocean.get_height())
    enemy2_coords = [(96,1984),(640,2592),(96,2880),(64,1120),(608,448)]
    enemies2 = []
    for cord in enemy2_coords:
        enemies2.append((e.entity(cord[0],cord[1],32,32,'enemy2'),False,60))
    bullet2_timer = 0
    bullet2s = []
    bullet2_speed = 3
    decrease_enemy2_health = 30
    damage2_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage2_alpha = 255
    display_damage2 = False
    enemy2_killed = False
    enemy2_coins_gained = random.randint(20,120)
    coin2_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin2_alpha = 255

    foods_coords = [(736, 1696),(352,2080),(64,2496),(160,352)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    stamina_rect2 = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    stamina_reduce_speed = 2
    
    lava_sound.play(-1)
    blit_rect = True
    start_time = 0
    coins = 0

    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    shake = 0
    bg_music2.play(-1)

    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    mouse_clicked = False
    mouse_released = True
    mouse_clicked2 = False
    mouse_released2 = True
    show_red = False
    count = 255
    blit_enemy_rect = True
    
    start_ticks = pygame.time.get_ticks()
    previous_time = time.time()
    fps = 60
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 60
        last_time = time.time()

        display.blit(bg2, (0, 0))

        pos += 3*dt

        #display.fill((50,50,50))
        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if shake > 0:
            shake -= 1
        if shake:
            scroll[0] += random.randint(0,8) - 4
            scroll[1] += random.randint(0,8) - 4

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile in tile_dict:
                    tile_image_name = tile_dict[tile]

                    if tile_image_name not in image_cache:
                        image_cache[tile_image_name] = pygame.image.load(f'data/images/block/tile/{tile_image_name}.png')

                    display.blit(image_cache[tile_image_name], (x * 32 - scroll[0], y * 32 - scroll[1]))
                #if tile == 'F':
                  # print(f"Food: {(x*32,y*32)}")
                #if tile == 'e':
                #   print(f"Enemy: {(x*32,y*32)}")
                #if tile == 'j':
                #    print(f"Enemy2: {(x*32,y*32)}")
                if tile == 'i':
                    display.blit(finishline_img, (x * 32-scroll[0], y * 32-scroll[1]))

                if tile != '0' and tile != 'i' and tile != 'e' and tile != 'j' and tile != 'F' and tile != '#':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                
                if tile == '#':
                    rect_ = pygame.Rect(x * 32, y * 32, 32,32)
                    if player.obj.rect.colliderect(rect_):
                        player.set_pos(448,3264)
                        moving_right = False
                        moving_left = False
                        lava_sound.stop()
                        bg_music2.stop()
                        m.gameOver(3,level_4,background=bg2)
                
                if tile == 'i':
                    rect = pygame.Rect(x * 32, y * 32, 32, 32)
                    if player.obj.rect.colliderect(rect):
                        ocean_sound.stop()
                        bg_music2.stop()
                        player.set_pos(224,3328)
                        moving_right = False
                        moving_left = False
                        m.level_passed(cutscene_1,3,4)
                    
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
        else:
            air_timer += 1

        player.change_frame(1)
        player.display(display, scroll)

        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)
        
        if show_red:
            count += 1
            if count < 14:
                display.blit(red_vignette, (0, 0))
            else:
                show_red = False
                count = 0
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        spawn_food(foods,foods_coords,scroll,player,stamina_rect)

        bullet_timer += 1

        if bullet_timer >= 150:
            for i in range(len(enemies) - 1, -1, -1):  
                coords = enemy_coords[i]
                enemy,sound_played,enemy_health = enemies[i]

                # Spawn a bullet from each enemy after 30 frames
                bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': False}  # You can adjust direction as needed
                bullets.append(bullet)

            bullet_timer = 0

        for coords in enemy_coords:
            if not enemy_killed:
                coin_alpha = 255
                coin_text.set_alpha(coin_alpha)

            if enemy_killed:
                coins = coins+enemy_coins_gained
                coin_x,coin_y = coords[0]-scroll[0],(coords[1]-20)-scroll[1]
                display.blit(coin_text,(coin_x,coin_y))
                coin_text.set_alpha(coin_alpha)
                coin_alpha -= 1
                if coin_alpha < 0:
                    coin_alpha = 0
                    enemy_killed = False

            if not display_damage:
                damage_alpha = 255
                damage_text.set_alpha(damage_alpha)
            
            if display_damage:
                display.blit(damage_text,((coords[0]-26)-scroll[0],(coords[1]-10)-scroll[1]))
                damage_text.set_alpha(damage_alpha)
                damage_alpha -= 1
                if damage_alpha < 0:
                    damage_alpha = 0
                    display_damage = False
        

        for i in range(len(enemies) - 1, -1, -1):  
            coords = enemy_coords[i]
            enemy, sound_played, enemy_health = enemies[i]

            if blit_rect and bullet_timer > 0 or bullet_timer < 0:
                enemy.change_frame(1)
                enemy.display(display, scroll)
            
            #enemy_healthbar = pygame.Rect(enemy.x-scroll[0], (enemy.y - 15)-scroll[1], 30, 4)
            enemy_rect = pygame.Rect(coords[0], coords[1], 32, 32)

            if enemy_health == 0:
                enemy_killed = True
                del enemy_coords[i]
                del enemies[i]
                continue

            if sword_rect.colliderect(enemy_rect):
                if mouse_clicked and mouse_released:
                    if not sound_played:
                        hit_sound.play()
                        enemies[i] = (enemy, True, enemy_health)  # Update sound_played status

                    enemy_health -= decrease_enemy_health
                    #print(enemy_health,decrease_enemy_health)
                    display_damage = True
                    enemy_killed = True
                    shake = 21

                    enemies[i] = (enemy, sound_played, enemy_health)

                    mouse_released = False  # Lock to prevent continuous decrease until mouse is released

            # Check if the mouse button has been released
            if not mouse_clicked:
                mouse_released = True

        bullets_to_remove = []

        for bullet in bullets[:]:
            bx = bullet_speed * bullet['direction']  
            bullet['rect'].x -= bx  # Move the bullet

            pygame.draw.rect(display, (255,0,0), pygame.Rect(bullet['rect'].x - scroll[0], bullet['rect'].y - scroll[1], 8, 4))

            if player.obj.rect.colliderect(bullet['rect']):
                show_red = True
                hearts -= 1  # Mark bullet for removal
                heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                display.blit(heart_img,(10,180))

                if hearts <= 0:
                    player.set_pos(448,3264)
                    moving_right = False
                    moving_left = False
                    lava_sound.stop()
                    bg_music2.stop()
                    m.gameOver(3,level_4,background=bg2)
                    
                bullets.remove(bullet)
                shake = 10
                if not bullet['sound']:
                    hit_sound.play()
                    bullet = {'rect': pygame.Rect(enemy.obj.rect.x, enemy.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': True}
                    bullets.append(bullet)
            
            if bullet['rect'].x < 0 or bullet['rect'].x > WINDOW_SIZE[0]:
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        bullet2_timer += 1

        if bullet2_timer >= 120:
            for i in range(len(enemies2) - 1, -1, -1):  
                coords = enemy2_coords[i]
                enemy2,sound_played,enemy2_health = enemies2[i]

                # Spawn a bullet2 from each enemy2 after 30 frames
                bullet2 = {'rect': pygame.Rect(enemy2.obj.rect.x, enemy2.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': False}  # You can adjust direction as needed
                bullet2s.append(bullet2)

            bullet2_timer = 0  # Reset timer after bullet2s are spawned

        for coords in enemy2_coords:
            if not enemy2_killed:
                coin2_alpha = 255
                coin2_text.set_alpha(coin_alpha)

            if enemy2_killed:
                coins = coins+enemy2_coins_gained
                display.blit(coin2_text,((coords[0])-scroll[0],(coords[1]-20)-scroll[1]))
                coin2_text.set_alpha(coin2_alpha)
                coin2_alpha -= 1
                if coin2_alpha < 0:
                    coin2_alpha = 0
                    enemy2_killed = False

            if not display_damage2:
                damage2_alpha = 255
                damage2_text.set_alpha(damage2_alpha)
            
            if display_damage2:
                display.blit(damage2_text,((coords[0]-26)-scroll[0],(coords[1]-10)-scroll[1]))
                damage2_text.set_alpha(damage2_alpha)
                damage2_alpha -= 1
                if damage2_alpha < 0:
                    damage2_alpha = 0
                    display_damage2 = False
        
        for i in range(len(enemies2) - 1, -1, -1):  
            coords = enemy2_coords[i]
            enemy2, sound_played, enemy2_health = enemies2[i]

            if blit_rect and bullet2_timer > 0 or bullet2_timer < 0:
                enemy2.change_frame(1)
                enemy2.display(display, scroll)
            
            #enemy2_healthbar = pygame.Rect(enemy2.x-scroll[0], (enemy2.y - 15)-scroll[1], 30, 4)
            enemy2_rect = pygame.Rect(coords[0], coords[1], 32, 32)

            if enemy2_health == 0:
                enemy2_killed = True
                del enemy2_coords[i]
                del enemies2[i]
                continue

            if sword_rect.colliderect(enemy2_rect):
                if mouse_clicked2 and mouse_released2:
                    if not sound_played:
                        hit_sound.play()
                        enemies2[i] = (enemy2, True, enemy2_health)  # Update sound_played status

                    enemy2_health -= decrease_enemy2_health
                    display_damage2 = True
                    enemy2_killed = True
                    shake = 21

                    enemies2[i] = (enemy2, sound_played, enemy2_health)

                    mouse_released2 = False  # Lock to prevent continuous decrease until mouse is released

            # Check if the mouse button has been released
            if not mouse_clicked2:
                mouse_released2 = True

        bullet2s_to_remove = []

        for bullet2 in bullet2s[:]:
            bx = bullet2_speed * bullet2['direction']  
            bullet2['rect'].x += bx  # Move the bullet2

            pygame.draw.rect(display, (165, 24, 255), pygame.Rect(bullet2['rect'].x - scroll[0], bullet2['rect'].y - scroll[1], 8, 4))

            if player.obj.rect.colliderect(bullet2['rect']):
                show_red = True
                hearts -= 1  # Mark bullet2 for removal
                heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                display.blit(heart_img,(10,180))

                if hearts <= 0:
                    player.set_pos(448,3264)
                    moving_right = False
                    moving_left = False
                    lava_sound.stop()
                    bg_music2.stop()
                    m.gameOver(3,level_4,background=bg2)
                    
                bullet2s.remove(bullet2)
                shake = 10
                if not bullet2['sound']:
                    hit_sound.play()
                    bullet2 = {'rect': pygame.Rect(enemy2.obj.rect.x, enemy2.obj.rect.y + 16, 8, 4), 'direction': 1, 'sound': True}
                    bullet2s.append(bullet2)
            
            if bullet2['rect'].x < 0 or bullet2['rect'].x > WINDOW_SIZE[0]:
                bullet2s_to_remove.append(bullet2)

        for bullet2 in bullet2s_to_remove:
            bullet2s.remove(bullet2)


        falling_down = 0
        bounce = 0.1
        #print(vertical_momentum)

        #if time.time() - previous_time > 5 and time.time() - previous_time < 10:
        #    display.blit(text,(300/2-text.get_width()/2,20))
        #    text.set_alpha(text_alpha)
        #    text_alpha -= 1
        #    if text_alpha < 0:
        #        text_alpha = 0

        if time.time() - previous_time >= 10:
            # Update ocean_rect.y based on the player's movement
            falling_down = 1
            bounce = 0.4
            water_rise_speed = 0.7

        if player.y < previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y += (previous_player_y - player.y) * bounce  # Lower the water based on player's upward movement
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down  # Player is moving up, move the ocean down

        elif player.y > previous_player_y:
            if vertical_momentum != 3:
                ocean_rect.y -= water_rise_speed  # Move the ocean up as player goes down
            elif vertical_momentum == 3:
                ocean_rect.y -= falling_down

        elif vertical_momentum == 3:
            ocean_rect.y -= falling_down

        previous_player_y = player.y

        ocean_rect2 = pygame.Rect(ocean_rect.x, ocean_rect.y + 120, ocean_rect.width, ocean_rect.height)
        #pygame.draw.rect(display,(0,0,0),ocean_rect2,1)

        ocean.set_alpha(230)
        display.blit(ocean, (0, ocean_rect.y))

        ocean_rect_scaled = pygame.Rect(
            ocean_rect.x,
            ocean_rect.y,
            ocean_rect.width,
            ocean_rect.height
        )
        
        if player_rect_scaled.colliderect(ocean_rect2):
            player.set_pos(448,3264)
            moving_right = False
            moving_left = False
            lava_sound.stop()
            bg_music2.stop()
            m.gameOver(3,level_4,background=bg2)
        
        pygame.draw.rect(display,(31, 76, 112),stamina_rect2)
        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))
        c = 0
        display.blit(heart_img,(10,180))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        c += stamina_reduce_speed
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -6.5

                    if jump_boost:
                        jump_count += 1

                        while time.time() - start_time < 35:
                            if jump_count > 0 and jump_count < 3:
                                vertical_momentum = -6.5
                                jump_sound.play()
                            
                            if air_timer < 6:
                                vertical_momentum = -6
                                jump_sound.play()

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False
                    mouse_clicked2 = False
                    
        stamina_rect.width -= c
        if stamina_rect.width <= 15:
            display.blit(vignette, (0, 0))
        if stamina_rect.width == 0:
            player.set_pos(448,3264)
            moving_right = False
            moving_left = False
            lava_sound.stop()
            bg_music2.stop()
            m.gameOver(3,level_4,background=bg2)
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        #clock.tick(fps)

def fade_in():
    display.fill((0,0,0))
    for alpha in range(0, 255, 5):
        display.set_alpha(alpha)
        screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
        pygame.display.update()
        pygame.time.delay(30)

def cutscene_1():
    global coins,grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,last_time,pos,dt

    for line in file_.splitlines():
        a, b = line.split(' ', 1)  # Split each line into key and value
        tile_dict[a] = b
    
    lava_sound.stop()
    ocean_sound.stop()
    
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)
    coins = 0
    player = e.entity(448,3264,32,32,'player')
    bg2 = pygame.image.load('data/images/background2.png')
    game_map = load_map('data/map/map5')
    #blit_transparent = False
    previous_player_y = player.y  # Track player's previous y position
    water_rise_speed = 0.4
    jump_count = 0
    jump_boost = False
    true_scroll = [448,3264]
    super_jump = e.entity(32,1000,16,16,'jump')
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',12)
    text = font.render('Collect for Jump Boost',True,(255,255,255))

    # !!!!! Add diffferent coords these are 3rd level ones bro !!!!! - done
    enemy_coords = [(864, 1312),(800,1888),(960,3104),(480,160),(928,544),(736,928)]
    enemies = []
    for coord in enemy_coords:
        enemies.append((e.entity(coord[0],coord[1],32,32,'enemy'),False,60))
    bullet_timer = 0
    bullets = []
    bullet_speed = 2
    decrease_enemy_health = 30
    damage_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage_alpha = 255
    display_damage = False
    enemy_killed = False
    enemy_coins_gained = random.randint(20,120)
    coin_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin_alpha = 255

    enemy2_coords = [(96,1984),(640,2592),(96,2880),(64,1120),(608,448)]
    enemies2 = []
    for cord in enemy2_coords:
        enemies2.append((e.entity(cord[0],cord[1],32,32,'enemy2'),False,60))
    bullet2_timer = 0
    bullet2s = []
    bullet2_speed = 3
    decrease_enemy2_health = 30
    damage2_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage2_alpha = 255
    display_damage2 = False
    enemy2_killed = False
    enemy2_coins_gained = random.randint(20,120)
    coin2_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin2_alpha = 255

    foods_coords = [(736, 1696),(352,2080),(64,2496),(160,352)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    stamina_rect2 = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    stamina_reduce_speed = 2
    
    lava_sound.play(-1)
    blit_rect = True
    start_time = 0

    text = smol_font.render(f'Lava rises in 5 seconds',True,(255,119,0))
    text_alpha = 255

    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    shake = 0

    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    mouse_clicked = False
    mouse_released = True
    mouse_clicked2 = False
    mouse_released2 = True
    show_red = False
    count = 255
    blit_enemy_rect = True
    
    start_ticks = pygame.time.get_ticks()
    previous_time = time.time()
    dialogues = [{'text': 'Hmm, strange'},
                 {'text': "There is no lava, no enemies, something's up"}]
    d = 0
    fps = 60
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 60
        last_time = time.time()

        display.blit(bg2, (0, 0))

        pos += 3*dt

        #display.fill((50,50,50))
        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if shake > 0:
            shake -= 1
        if shake:
            scroll[0] += random.randint(0,8) - 4
            scroll[1] += random.randint(0,8) - 4

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile in tile_dict:
                    tile_image_name = tile_dict[tile]

                    if tile_image_name not in image_cache:
                        image_cache[tile_image_name] = pygame.image.load(f'data/images/block/tile/{tile_image_name}.png')

                    display.blit(image_cache[tile_image_name], (x * 32 - scroll[0], y * 32 - scroll[1]))
                #if tile == 'F':
                  # print(f"Food: {(x*32,y*32)}")
                #if tile == 'e':
                #   print(f"Enemy: {(x*32,y*32)}")
                #if tile == 'j':
                #    print(f"Enemy2: {(x*32,y*32)}")
                if tile == 'i':
                    display.blit(finishline_img, (x * 32-scroll[0], y * 32-scroll[1]))

                if tile != '0' and tile != 'i' and tile != 'e' and tile != 'j' and tile != 'F' and tile != '#':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                
                if tile == '#':
                    rect_ = pygame.Rect(x * 32, y * 32, 32,32)
                    if player.obj.rect.colliderect(rect_):
                        player.set_pos(448,3264)
                        moving_right = False
                        moving_left = False
                        lava_sound.stop()
                        bg_music2.stop()
                        m.gameOver(4,cutscene_1,background=bg2)
                    
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
        else:
            air_timer += 1
        
        if blit_jump:
            super_jump.change_frame(1)
            super_jump.display(display, scroll)

        player.change_frame(1)
        player.display(display, scroll)

        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)
        
        if show_red:
            count += 1
            if count < 14:
                display.blit(red_vignette, (0, 0))
            else:
                show_red = False
                count = 0
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))

        if player.obj.rect.colliderect(super_jump.obj.rect):
            start_time = time.time()
            counter += 0.5
            if counter == 1:
                powerup_sound.play()
            blit_jump = False
            jump_boost = True
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        #spawn_food(foods,foods_coords,scroll,player,stamina_rect)

        #print(vertical_momentum)

        #if time.time() - previous_time > 5 and time.time() - previous_time < 10:
        #    display.blit(text,(300/2-text.get_width()/2,20))
        #    text.set_alpha(text_alpha)
        #    text_alpha -= 1
        #    if text_alpha < 0:
        #        text_alpha = 0

        #pygame.draw.rect(display,(0,0,0),ocean_rect2,1
        
        pygame.draw.rect(display,(31, 76, 112),stamina_rect2)
        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))
        c = 0
        display.blit(text,(38-scroll[0],950-scroll[1]))
        display.blit(heart_img,(10,180))
        
        d += 1
        if d == 40:
            moving_right = False
            moving_left = False
            display_dialogue(dialogues)
            level_5()

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        c += stamina_reduce_speed
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -6.5

                    if jump_boost:
                        jump_count += 1

                        while time.time() - start_time < 35:
                            if jump_count > 0 and jump_count < 3:
                                vertical_momentum = -6.5
                                jump_sound.play()
                            
                            if air_timer < 6:
                                vertical_momentum = -6
                                jump_sound.play()

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False
                    mouse_clicked2 = False
                    
        stamina_rect.width -= c
        if stamina_rect.width <= 15:
            display.blit(vignette, (0, 0))
        if stamina_rect.width == 0:
            player.set_pos(448,3264)
            moving_right = False
            moving_left = False
            lava_sound.stop()
            bg_music2.stop()
            m.gameOver(4,cutscene_1,background=bg2)
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        #clock.tick(fps)
    
def level_5():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,last_time,pos,dt

    for line in file_.splitlines():
        a, b = line.split(' ', 1)  # Split each line into key and value
        tile_dict[a] = b
    
    lava_sound.stop()
    ocean_sound.stop()
    
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)

    player = e.entity(448,3264,32,32,'player')
    bg2 = pygame.image.load('data/images/background2.png')
    game_map = load_map('data/map/map5')
    ocean = pygame.image.load('data/images/lava.png')
    #blit_transparent = False
    previous_player_y = player.y  # Track player's previous y position
    water_rise_speed = 0.4
    jump_count = 0
    jump_boost = False
    true_scroll = [448,3264]
    super_jump = e.entity(32,1000,16,16,'jump')
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',12)
    text = font.render('Collect for Jump Boost',True,(255,255,255))

    # !!!!! Add diffferent coords these are 3rd level ones bro !!!!! - done
    enemy_coords = [(864, 1312),(800,1888),(960,3104),(480,160),(928,544),(736,928)]
    enemies = []
    for coord in enemy_coords:
        enemies.append((e.entity(coord[0],coord[1],32,32,'enemy'),False,60))
    bullet_timer = 0
    bullets = []
    bullet_speed = 2
    decrease_enemy_health = 30
    damage_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage_alpha = 255
    display_damage = False
    enemy_killed = False
    enemy_coins_gained = random.randint(20,120)
    coin_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin_alpha = 255

    enemy2_coords = [(96,1984),(640,2592),(96,2880),(64,1120),(608,448)]
    enemies2 = []
    for cord in enemy2_coords:
        enemies2.append((e.entity(cord[0],cord[1],32,32,'enemy2'),False,60))
    bullet2_timer = 0
    bullet2s = []
    bullet2_speed = 3
    decrease_enemy2_health = 30
    damage2_text = smol_font.render(str(decrease_enemy_health),True,(255,0,0))
    damage2_alpha = 255
    display_damage2 = False
    enemy2_killed = False
    enemy2_coins_gained = random.randint(20,120)
    coin2_text = smol_font.render(f"+{enemy_coins_gained}",True,(255, 242, 0))
    coin2_alpha = 255

    foods_coords = [(736, 1696),(352,2080),(64,2496),(160,352)]
    foods = []
    for coords in foods_coords:
        foods.append((pygame.Rect(coords[0],coords[1],16,16),random.choice(foods_list),False))

    stamina_color = (100,162,240)
    stamina = pygame.transform.scale(pygame.image.load("data/images/stamina bar.png"),(128,20))
    stamina_rect = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    stamina_rect2 = pygame.Rect((300/2-stamina.get_width()/2)+1,171,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    stamina_reduce_speed = 2
    
    blit_rect = True
    start_time = 0

    text = smol_font.render(f'Lava rises in 5 seconds',True,(255,119,0))
    text_alpha = 255

    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    shake = 0

    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    mouse_clicked = False
    mouse_released = True
    mouse_clicked2 = False
    mouse_released2 = True
    show_red = False
    count = 255
    blit_enemy_rect = True
    
    start_ticks = pygame.time.get_ticks()
    previous_time = time.time()
    dialogues = [{'text': 'Hmm, strange'},
                 {'text': "There is no lava, no enemies, something's up"}]
    
    portal = e.entity(384,2880,32,32,'portal')
    fps = 70
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 70
        last_time = time.time()

        display.blit(bg2, (0, 0))

        pos += 3*dt

        #display.fill((50,50,50))
        true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if shake > 0:
            shake -= 1
        if shake:
            scroll[0] += random.randint(0,8) - 4
            scroll[1] += random.randint(0,8) - 4

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile in tile_dict:
                    tile_image_name = tile_dict[tile]

                    if tile_image_name not in image_cache:
                        image_cache[tile_image_name] = pygame.image.load(f'data/images/block/tile/{tile_image_name}.png')

                    display.blit(image_cache[tile_image_name], (x * 32 - scroll[0], y * 32 - scroll[1]))
                #if tile == 'F':
                  # print(f"Food: {(x*32,y*32)}")
                #if tile == 'e':
                #   print(f"Enemy: {(x*32,y*32)}")
                #if tile == 'j':
                #    print(f"Enemy2: {(x*32,y*32)}")
                if tile == 'i':
                    display.blit(finishline_img, (x * 32-scroll[0], y * 32-scroll[1]))

                if tile != '0' and  tile != 'i' and tile != 'e' and tile != 'j' and tile != 'F' and tile != '#' and tile != 'P':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                
                if tile == '#':
                    rect_ = pygame.Rect(x * 32, y * 32, 32,32)
                    if player.obj.rect.colliderect(rect_):
                        player.set_pos(448,3264)
                        moving_right = False
                        moving_left = False
                        lava_sound.stop()
                        bg_music2.stop()
                        m.gameOver(4,cutscene_1,background=bg2)
                    
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
        else:
            air_timer += 1
        
        if blit_jump:
            super_jump.change_frame(1)
            super_jump.display(display, scroll)

        player.change_frame(1)
        player.display(display, scroll)

        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)
        
        if show_red:
            count += 1
            if count < 14:
                display.blit(red_vignette, (0, 0))
            else:
                show_red = False
                count = 0
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))

        if player.obj.rect.colliderect(super_jump.obj.rect):
            start_time = time.time()
            counter += 0.5
            if counter == 1:
                powerup_sound.play()
            blit_jump = False
            jump_boost = True
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        #spawn_food(foods,foods_coords,scroll,player,stamina_rect)

        #print(vertical_momentum)

        #if time.time() - previous_time > 5 and time.time() - previous_time < 10:
        #    display.blit(text,(300/2-text.get_width()/2,20))
        #    text.set_alpha(text_alpha)
        #    text_alpha -= 1
        #    if text_alpha < 0:
        #        text_alpha = 0
        
        portal.change_frame(1)
        portal.display(display,scroll)

        if player.obj.rect.colliderect(portal.obj.rect):
            fade_in()
            boss_fight()

        pygame.draw.rect(display,(31, 76, 112),stamina_rect2)
        pygame.draw.rect(display,stamina_color,stamina_rect)
        display.blit(stamina,(300/2-stamina.get_width()/2,160))
        c = 0
        display.blit(text,(38-scroll[0],950-scroll[1]))
        display.blit(heart_img,(10,180))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    c += stamina_reduce_speed
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    c += stamina_reduce_speed
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        c += stamina_reduce_speed
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -6.5

                    if jump_boost:
                        jump_count += 1

                        while time.time() - start_time < 35:
                            if jump_count > 0 and jump_count < 3:
                                vertical_momentum = -6.5
                                jump_sound.play()
                            
                            if air_timer < 6:
                                vertical_momentum = -6
                                jump_sound.play()

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False
                    mouse_clicked2 = False
                    
        stamina_rect.width -= c
        if stamina_rect.width <= 15:
            display.blit(vignette, (0, 0))
        if stamina_rect.width == 0:
            player.set_pos(448,3264)
            moving_right = False
            moving_left = False
            lava_sound.stop()
            bg_music2.stop()
            m.gameOver(4,cutscene_1,background=bg2)
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        #clock.tick(fps)

boss_music = pygame.mixer.Sound('data/audio/boss_music.wav')
boss_music.set_volume(0.8)

def boss_fight():
    global grass_sound_timer, vertical_momentum, moving_left, moving_right, air_timer, true_scroll,last_time,pos,dt

    for line in file_.splitlines():
        a, b = line.split(' ', 1)  # Split each line into key and value
        tile_dict[a] = b
    
    smol_font = pygame.font.Font("data/retro_computer_personal_use.ttf",12)

    player = e.entity(192,96,32,32,'player')
    bg2 = pygame.image.load('data/images/background2.png')
    game_map = load_map('data/map/boss')
    ocean = pygame.image.load('data/images/lava.png')
    jump_count = 0
    jump_boost = False
    true_scroll = [320,96]
    super_jump = e.entity(32,1000,16,16,'jump')
    blit_jump = True
    counter = 0
    font = pygame.font.Font('data/Peepo.ttf',12)
    text = font.render('Collect for Jump Boost',True,(255,255,255))

    boss_color = (255,0,0)
    boss_bar = pygame.transform.scale(pygame.image.load("data/images/boss bar.png"),(128,20))
    boss_bar_rect = pygame.Rect((300/2-boss_bar.get_width()/2)+1,10,126,8)
    boss_bar_rect2 = pygame.Rect((300/2-boss_bar.get_width()/2)+1,10,126,8)
    vignette = create_vignette((300,200))
    red_vignette = create_vignette((300,200),intensity=100,color=(255,0,0))
    boss_bar_reduce_speed = 2
    
    blit_rect = True
    start_time = 0

    text = smol_font.render(f'Lava rises in 5 seconds',True,(255,119,0))
    text_alpha = 255

    hearts = 3
    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
    shake = 0
    lava_sound.stop()
    ocean_sound.stop()

    sword_img = pygame.transform.scale(pygame.image.load('data/images/noob_sword.png'),(16,16))
    sword_flip = not player.flip
    sword_flip2 = False

    mouse_clicked = False
    mouse_released = True
    mouse_clicked2 = False
    mouse_released2 = True
    show_red = False
    count = 255
    scroll = [40,-40]
    boss = e.entity(40,155,200,100,'boss')
    boss_music.play(-1)

    dialogues = [{'text': 'Well Well Well...'},
                 {'text': "Look who it is, Hydro."},
                 {'text': 'You said you would evolve from being my minion'},
                 {'text': "And look at you, you had killed all of my minions"},
                 {'text': "So let's see how you do against me"}]


    dialogues2 = [{'text': 'Hmm, Impressive'},
                  {'text': 'But I expected better from someone like you'},
                {'text': "You should have probably stayed in my training for longer"}]
    
    dialogues3 = [{'text': 'Ok, I had enough'}]

    dialogues4 = [{'text': 'H-H-H-H HOWW?!?!?!?!?!'},
                {'text': 'HOW CAN SOMEONE LIKE YOU'},
                {'text': "DEFEAT ME???!?!?!?"},
                {'text': "I-I-I I CAN NOT ACCEPT THIS"},
                {'text': 'M-M MY STATUS, M-M MY DIGNITY, AND MY EMPIRE IS IN SHAMBLES'},
                {'text': "I-I CURSE YOU, H-HYDRO!!!!!"}]

    d = 0
    d2 = 0
    d3 = 0
    bullet_timer = 0
    bullets = []
    bullet_speed = 4
    render_offset = [0,0]
    hit_cooldown = 0
    sword_cooldown = 0
    red_vignette_timer = 0
    brs = 2
    damage_text = smol_font.render('5',True,(255,0,0))
    damage_alpha = 255
    display_damage = False

    bullet2_timer = 0
    bullet2s = []
    bullet2_speed = 4
    
    random_text = random.choice(['Too weak','This but a scratch'])
    text1 = smol_font.render(str(random_text),True,(255,255,255))
    alpha = 255
    display_text = False
    text_timer = 0
    #dx = random.randint(int(boss.x+100),int(boss.x+190))
    #dy = -(random.randint(int(abs(boss.y)),int(abs(boss.y+50))))
    boss_death = False

    beem_timer = 0
    beem_coords = []
    charge_up = pygame.mixer.Sound('data/audio/charge_up.wav')
    explosion = pygame.mixer.Sound('data/audio/explosion.wav')
    victory = pygame.mixer.Sound('data/audio/victory_music.wav')
    victory_music_played = False
    coun = 0
    fps = 100
    while True:
        clock.tick(fps)

        if not (clock.get_fps() == 0):
            dt = fps/clock.get_fps()
        dt += 100
        last_time = time.time()

        display.fill((60,60,60))

        pos += 3*dt
        
        #true_scroll[0] += (player.x - true_scroll[0] - 152) / 20
        #true_scroll[1] += (player.y - true_scroll[1] - 106) / 20
        #scroll = true_scroll.copy()
        #scroll[0] = int(scroll[0])
        #scroll[1] = int(scroll[1])


        if shake > 0:
            shake -= 1
        if shake:
            render_offset[0] += random.randint(0,8) - 4
            render_offset[1] += random.randint(0,8) - 4
        else:
            render_offset = [0,0]

        boss.y -= 1.5
        if boss.y <= -15:
            boss.y = -15

        boss.change_frame(1)
        boss.display(display,scroll)

        tile_rects = []
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '$':
                    display.blit(pygame.image.load('data/images/block/tile/real_full_tile.png'),(x*32-scroll[0],y*32-scroll[1]))
                #if tile == 'F':
                  # print(f"Food: {(x*32,y*32)}")
                #if tile == 'e':
                #   print(f"Enemy: {(x*32,y*32)}")
                #if tile == 'p':
                #    print(f"Player: {(x*32,y*32)}")

                if tile != '0' and tile != 'p':
                    tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))

                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(False)
            player.set_action('run')
        
        sword_flip = not player.flip

        collision_types = player.move(player_movement, tile_rects)

        if collision_types['bottom']:
            jump_count = 0
            air_timer = 0
            vertical_momentum = 0
        else:
            air_timer += 1
        
        if blit_jump:
            super_jump.change_frame(1)
            super_jump.display(display, scroll)

        player.change_frame(1)
        player.display(display, scroll)

        if player.flip:
            sword_rect = pygame.Rect(player.x+20,player.y+10,8,8)
        else:
            sword_rect = pygame.Rect(player.x-4,player.y+10,8,8)

        if show_red:
            if red_vignette_timer > 0:
                red_vignette_timer -= 1  # Reduce the timer each frame
                display.blit(red_vignette, (0, 0))  # Render the red vignette
            else:
                show_red = False  # Stop showing the vignette after timer expires
        
        new_sword_img = pygame.transform.flip(sword_img,sword_flip,sword_flip2)
        display.blit(new_sword_img,(sword_rect.x-scroll[0],sword_rect.y-scroll[1]))

        if player.obj.rect.colliderect(super_jump.obj.rect):
            start_time = time.time()
            counter += 0.5
            if counter == 1:
                powerup_sound.play()
            blit_jump = False
            jump_boost = True
        
        player_rect_scaled = pygame.Rect(
            player.obj.rect.x - scroll[0],
            player.obj.rect.y - scroll[1],
            player.obj.rect.width,
            player.obj.rect.height
        )

        display.blit(text,(38-scroll[0],950-scroll[1]))
        display.blit(heart_img,(10,180))

        core = pygame.Rect((boss.size_x/2-16/2)+48,(boss.size_y/2-16/2)+75,16,16)
        new_sword_rect = pygame.Rect(sword_rect.x-scroll[0],sword_rect.y-scroll[1],16,16)
        #pygame.draw.rect(display,(255,0,0),new_sword_rect,1)

        if sword_cooldown > 0:
            sword_cooldown -= 1

        dx = int(boss.x + 190)
        dy = int(boss.y + 10)

        if display_text:
            display.blit(text1,((text.get_width()-100)-scroll[0],(-10)-scroll[1]))
            text1.set_alpha(alpha)
            alpha -= 1
            if alpha < 0:
                alpha = 0

        if display_damage:
            display.blit(damage_text,((dx)-scroll[0],(dy)-scroll[1]))
            damage_text.set_alpha(damage_alpha)
            damage_alpha -= 10
            if damage_alpha < 0:
                damage_alpha = 0
                display_damage = False
        else:
            damage_alpha = 255
            damage_text.set_alpha(damage_alpha)
        
        if boss_bar_rect.width <= 0:
            boss_death = True

        if new_sword_rect.colliderect(core):
            #print('hello')
            if mouse_clicked and mouse_released and sword_cooldown == 0:
                shake = 5
                hit_sound.play()
                display_damage = True
                boss_bar_rect.width -= brs
                sword_cooldown = 40
                mouse_released = False
        
        if not mouse_clicked:
            mouse_released = True
        if boss.y == -15:
            d += 1
            if d == 20:
                display_dialogue(dialogues)
                moving_right = False
                moving_left = False
                previouss_time = time.time()
            if d > 20:
                #pygame.draw.rect(display,(255,0,0),core,1)
                if time.time()-previouss_time < 25:
                    #print(time.time()-previouss_time)
                    text_timer += 1
                    if text_timer >= random.randint(500,1000):
                        display_text = True
                    bullet_timer += 1
                    if bullet_timer >= random.randint(50,100):
                        for i in range(random.randint(1, 4)):
                            bullet_color = random.choice([(165, 24, 255),(255,0,0)])
                            bullet = {'rect': pygame.Rect(random.choice([100,150,300,200,250,400,410,210,120]), -(random.randint(80,210)), 5,16), 'direction': 1, 'sound': False}
                            bullets.append(bullet)
                        bullet_timer = 0
                    
                    bullets_to_remove = []

                    for bullet in bullets[:]:
                        by = bullet_speed * bullet['direction']  
                        bullet['rect'].y += by

                        # Render bullets
                        pygame.draw.rect(display, bullet_color, pygame.Rect(bullet['rect'].x - scroll[0], bullet['rect'].y - scroll[1], 5,16))

                        # Bullet collision with player (only if cooldown is 0)
                        if player.obj.rect.colliderect(bullet['rect']) and hit_cooldown == 0:
                            bullets_to_remove.append(bullet)
                            show_red = True
                            
                            hearts -= 1  # Decrease hearts
                            heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                            display.blit(heart_img, (10, 180))

                            # Set the hit cooldown to avoid further damage for a brief period
                            hit_cooldown = 60  # 1 second if your game runs at 60 fps
                            red_vignette_timer = 20

                            # Check for game over
                            if hearts <= 0:
                                player.set_pos(448,3264)
                                moving_right = False
                                moving_left = False
                                m.gameOver(boss_fight, background=bg2)
                                lava_sound.stop()
                                boss_music.stop()

                            shake = 10

                            if not bullet['sound']:
                                hit_sound.play()
                                bullet['sound'] = True
                            
                        # Remove bullets that go off-screen
                        if bullet['rect'].y > WINDOW_SIZE[1]+40:
                            bullets_to_remove.append(bullet)

                    # Remove bullets marked for removal
                    for bullet in bullets_to_remove:
                        bullets.remove(bullet)
                    if not mouse_clicked:
                        mouse_released = True
                else:
                    d2 += 1
                    if d2 == 20:
                        display_dialogue(dialogues2)
                        moving_right = False
                        moving_left = False
                        new_previous_time = time.time()
                    if d2 > 20:
                        if time.time()-new_previous_time < 18:
                            text_timer += 1
                            if text_timer >= random.randint(500,1000):
                                display_text = True
                            bullet_timer += 1
                            if bullet_timer >= random.randint(50,180):
                                for i in range(random.randint(1,4)):
                                    bullet_color = random.choice([(165, 24, 255),(255,0,0)])
                                    bullet = {'rect': pygame.Rect(random.choice([x for x in range(100,500)]), -(random.randint(40,80)), 5,25), 'direction': 1, 'sound': False}
                                    bullets.append(bullet)
                                bullet_timer = 0
                            
                            bullets_to_remove = []

                            for bullet in bullets[:]:
                                by = 5 * bullet['direction']  
                                bullet['rect'].y += by

                                # Render bullets
                                pygame.draw.rect(display, bullet_color, pygame.Rect(bullet['rect'].x - scroll[0], bullet['rect'].y - scroll[1], 5,25))

                                # Bullet collision with player (only if cooldown is 0)
                                if player.obj.rect.colliderect(bullet['rect']) and hit_cooldown == 0:
                                    bullets_to_remove.append(bullet)
                                    show_red = True
                                    
                                    hearts -= 1  # Decrease hearts
                                    heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                                    display.blit(heart_img, (10, 180))

                                    # Set the hit cooldown to avoid further damage for a brief period
                                    hit_cooldown = 60  # 1 second if your game runs at 60 fps
                                    red_vignette_timer = 20

                                    # Check for game over
                                    if hearts <= 0:
                                        player.set_pos(448,3264)
                                        moving_right = False
                                        moving_left = False
                                        m.gameOver(boss_fight, background=bg2)
                                        lava_sound.stop()
                                        boss_music.stop()

                                    shake = 10

                                    if not bullet['sound']:
                                        hit_sound.play()
                                        bullet['sound'] = True
                                    
                                # Remove bullets that go off-screen
                                if bullet['rect'].y > WINDOW_SIZE[1]+40:
                                    bullets_to_remove.append(bullet)

                            # Remove bullets marked for removal
                            for bullet in bullets_to_remove:
                                bullets.remove(bullet)
                            if not mouse_clicked:
                                mouse_released = True
                        else:
                            beam_damage_delay = 30
                            d3 += 1
                            if d3 == 20:
                                display_dialogue(dialogues3,text_color=(255,0,0))
                                moving_right = False
                                moving_left = False
                                new_new_previous_time = time.time()
                            if d3 > 20:
                                if time.time() - new_new_previous_time < 30:
                                    text_timer += 1
                                    if text_timer >= random.randint(500,1000):
                                        display_text = True
                                    bullet2_timer += 1
                                    if bullet2_timer >= random.randint(80,120):
                                        for i in range(1):
                                            bullet2_color = random.choice(['r_beem','p_beem'])
                                            bullet2 = {'rect': e.entity(random.choice([x for x in range(100,300)]), -50,25,150,bullet2_color), 'direction': 1, 'sound': False, 'sound2': False}
                                            bullet2s.append(bullet2)
                                        bullet2_timer = 0
                                    
                                    bullet2s_to_remove = []

                                    for bullet2 in bullet2s[:]:
                                        by = 5 * bullet2['direction']  
                                        bullet2['rect'].y += by

                                        if not bullet2['sound2']:
                                            explosion.play()
                                            bullet2['sound2'] = True

                                        # Render bullet2s
                                        bullet2['rect'].change_frame(1)
                                        bullet2['rect'].display(display,scroll)

                                        # bullet2 collision with player (only if cooldown is 0)
                                        if player.obj.rect.colliderect(bullet2['rect']) and hit_cooldown == 0:
                                            bullet2s_to_remove.append(bullet2)
                                            show_red = True
                                            
                                            hearts -= 1  # Decrease hearts
                                            heart_img = pygame.image.load(f"data/images/heart {hearts}.png")
                                            display.blit(heart_img, (10, 180))

                                            # Set the hit cooldown to avoid further damage for a brief period
                                            hit_cooldown = 100  # 1 second if your game runs at 60 fps
                                            red_vignette_timer = 20

                                            # Check for game over
                                            if hearts <= 0:
                                                player.set_pos(448,3264)
                                                moving_right = False
                                                moving_left = False
                                                m.gameOver(boss_fight, background=bg2)
                                                lava_sound.stop()
                                                boss_music.stop()

                                            shake = 10

                                            if not bullet2['sound']:
                                                hit_sound.play()
                                                bullet2['sound'] = True
                                            
                                        # Remove bullet2s that go off-screen
                                        if bullet2['rect'].y > WINDOW_SIZE[1]-10:
                                            bullet2s_to_remove.append(bullet2)

                                    # Remove bullet2s marked for removal
                                    for bullet2 in bullet2s_to_remove:
                                        bullet2s.remove(bullet2)
                                    if not mouse_clicked:
                                        mouse_released = True

            # Decrease hit cooldown over time
            if hit_cooldown > 0:
                hit_cooldown -= 1
            if not mouse_clicked:
                mouse_released = True

        if boss_death:
            bullets.clear()
            bullet2s.clear()
            boss_music.stop()
            boss.set_action('death')

            # Play victory music only once
            if not victory_music_played:
                victory.play(-1)
                victory_music_played = True  # Set the flag to True so it won't play again
            
            # Other boss death-related code...
            coun += 1
            if coun == 100:
                display_dialogue(dialogues4)
                fade_in()
                m.you_won()
        else:
            boss.set_action('idle')

        pygame.draw.rect(display,(119,0,0),boss_bar_rect2)
        pygame.draw.rect(display,boss_color,boss_bar_rect)
        display.blit(boss_bar,(300/2-boss_bar.get_width()/2,-1))
        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = True
                if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                    if not jump_boost:
                        if air_timer < 6:
                            jump_sound.play()
                            vertical_momentum = -4

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    sword_flip2 = True
                    mouse_clicked = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sword_flip2 = False
                    mouse_clicked = False

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), render_offset)
        pygame.display.update()