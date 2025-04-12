'''
        bullet2_timer += 1
        if bullet2_timer >= random.randint(50,100):
            for i in range(random.randint(1, 4)):
                bullet2_color = random.choice([(165, 24, 255),(255,0,0)])
                bullet2 = {'rect': pygame.Rect(random.choice([100,150,300,200,250,400,410,210,120]), -(random.randint(80,210)), 5,16), 'direction': 1, 'sound': False}
                bullet2s.append(bullet2)
            bullet2_timer = 0
        
        bullet2s_to_remove = []

        for bullet2 in bullet2s[:]:
            by = bullet2_speed * bullet2['direction']  
            bullet2['rect'].y += by

            # Render bullet2s
            pygame.draw.rect(display, bullet2_color, pygame.Rect(bullet2['rect'].x - scroll[0], bullet2['rect'].y - scroll[1], 5,16))

            # bullet2 collision with player (only if cooldown is 0)
            if player.obj.rect.colliderect(bullet2['rect']) and hit_cooldown == 0:
                bullet2s_to_remove.append(bullet2)
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

                if not bullet2['sound']:
                    hit_sound.play()
                    bullet2['sound'] = True
                
            # Remove bullet2s that go off-screen
            if bullet2['rect'].y > WINDOW_SIZE[1]+40:
                bullet2s_to_remove.append(bullet2)

        # Remove bullet2s marked for removal
        for bullet2 in bullet2s_to_remove:
            bullet2s.remove(bullet2)
        if not mouse_clicked:
            mouse_released = True
'''