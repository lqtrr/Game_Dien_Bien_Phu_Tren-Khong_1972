import sys

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('def main():')
if idx == -1:
    print("Cannot find def main():")
    sys.exit(1)

top_content = content[:idx]

new_main = """def main():
    running = True
    app_state = "MAIN_MENU" # "MAIN_MENU", "UPGRADE", "PLAYING"
    game_state = "PLAYING"  # "PLAYING", "GAME_OVER", "WIN"
    
    level = None
    player = None
    enemies = []
    data_list = []
    bullets = []
    item_drops = []
    score = 0
    show_visualizer = False

    AI_UPDATE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(AI_UPDATE_EVENT, 500)

    while running:
        if app_state == "MAIN_MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Bắt đầu game
                        level = Level()
                        player = Player(0, 0)
                        level.init_level(0, 0)
                        
                        enemies = []
                        for _ in range(4):
                            dx, dy = get_random_pixel_offset(600, 1500)
                            enemies.append(DFSEnemy(dx, dy))
                            dx, dy = get_random_pixel_offset(600, 1500)
                            enemies.append(BFSEnemy(dx, dy))
                            dx, dy = get_random_pixel_offset(600, 1500)
                            enemies.append(AStarEnemy(dx, dy))
                            dx, dy = get_random_pixel_offset(600, 1500)
                            enemies.append(HeuristicEnemy(dx, dy))
                            
                        data_list = []
                        for _ in range(15):
                            dx, dy = get_random_pixel_offset(200, 1000)
                            data_list.append(DataCollectible(player.pixel_x + dx, player.pixel_y + dy))
                            
                        bullets = []
                        item_drops = []
                        score = 0
                        show_visualizer = False
                        game_state = "PLAYING"
                        app_state = "PLAYING"
                        
                        for enemy in enemies:
                            enemy.update_path(player.r, player.c, level)
                            
                    elif event.key == pygame.K_u:
                        app_state = "UPGRADE"
            
            # Vẽ Sảnh chờ
            screen.fill((10, 20, 10))
            title = large_font.render("✈ SẢNH CHỜ: ĐIỆN BIÊN PHỦ TRÊN KHÔNG ✈", True, (180, 255, 100))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            money_txt = font.render(f"Tiền (Nhiên liệu): {global_profile.money}", True, DATA_COLOR)
            screen.blit(money_txt, (WIDTH//2 - money_txt.get_width()//2, 200))
            
            stats_txt = font.render(f"Máu: {global_profile.get_max_hp()} | Đạn: {global_profile.get_max_ammo()} | Độ bền: {global_profile.get_armor()} | Tốc độ bắn: Lv.{global_profile.upgrade_fire_rate}", True, (200, 200, 200))
            screen.blit(stats_txt, (WIDTH//2 - stats_txt.get_width()//2, 250))
            
            help_txt = font.render("Nhấn [ENTER] để Xuất Kích | Nhấn [U] để Mở Bảng Nâng Cấp", True, (255, 255, 255))
            screen.blit(help_txt, (WIDTH//2 - help_txt.get_width()//2, 400))
            
        elif app_state == "UPGRADE":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        app_state = "MAIN_MENU"
                    # Mua nâng cấp: 1 = Máu, 2 = Giáp, 3 = Đạn, 4 = Tốc độ bắn (Giá 50 tiền mỗi cấp)
                    elif event.key == pygame.K_1:
                        if global_profile.money >= 50:
                            global_profile.money -= 50
                            global_profile.upgrade_hp += 1
                    elif event.key == pygame.K_2:
                        if global_profile.money >= 50:
                            global_profile.money -= 50
                            global_profile.upgrade_armor += 1
                    elif event.key == pygame.K_3:
                        if global_profile.money >= 50:
                            global_profile.money -= 50
                            global_profile.upgrade_ammo += 1
                    elif event.key == pygame.K_4:
                        if global_profile.money >= 50:
                            global_profile.money -= 50
                            global_profile.upgrade_fire_rate += 1
                            
            screen.fill((10, 20, 10))
            title = large_font.render("XƯỞNG BẢO DƯỠNG & NÂNG CẤP", True, (255, 200, 50))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            money_txt = font.render(f"Tiền hiện có: {global_profile.money}", True, DATA_COLOR)
            screen.blit(money_txt, (WIDTH//2 - money_txt.get_width()//2, 120))
            
            opts = [
                f"[1] Nâng Máu tối đa (Lv.{global_profile.upgrade_hp}) - 50 Tiền",
                f"[2] Nâng Độ bền/Giáp (Lv.{global_profile.upgrade_armor}) - 50 Tiền",
                f"[3] Nâng Lượng đạn (Lv.{global_profile.upgrade_ammo}) - 50 Tiền",
                f"[4] Nâng Tốc độ bắn (Lv.{global_profile.upgrade_fire_rate}) - 50 Tiền",
            ]
            for i, opt in enumerate(opts):
                txt = font.render(opt, True, (255, 255, 255))
                screen.blit(txt, (WIDTH//2 - 200, 200 + i * 50))
                
            esc_txt = font.render("Nhấn [ESC] để Quay lại Sảnh chờ", True, (150, 150, 150))
            screen.blit(esc_txt, (WIDTH//2 - esc_txt.get_width()//2, 500))
            
        elif app_state == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if game_state == "PLAYING":
                        if event.key == pygame.K_SPACE:
                            show_visualizer = not show_visualizer
                        elif event.key == pygame.K_ESCAPE:
                            app_state = "MAIN_MENU" # Thoát nhanh về sảnh
                    else:
                        if event.key in [pygame.K_r, pygame.K_RETURN, pygame.K_SPACE]:
                            app_state = "MAIN_MENU" # Về sảnh sau khi chết
                if game_state == "PLAYING":
                    if event.type == AI_UPDATE_EVENT and not show_visualizer:
                        for enemy in enemies:
                            enemy.update_path(player.r, player.c, level)
            
            if game_state == "PLAYING" and not show_visualizer:
                keys = pygame.key.get_pressed()
                player.update_movement(keys)
                
                # Bắn đạn
                if (keys[pygame.K_z] or pygame.mouse.get_pressed()[0]) and player.fire_cooldown <= 0 and player.ammo > 0:
                    player.ammo -= 1
                    player.fire_cooldown = global_profile.get_fire_cooldown()
                    bullets.append(Bullet(player.pixel_x, player.pixel_y, player.angle, speed=15, damage=global_profile.get_damage(), is_player=True))
                
                level.update(player.pixel_x, player.pixel_y)
                
                # Cập nhật đạn
                for b in bullets[:]:
                    b.update()
                    if b.life <= 0:
                        bullets.remove(b)
                        continue
                    # Check va chạm đạn vs địch
                    if b.is_player:
                        hit = False
                        for enemy in enemies[:]:
                            if math.hypot(b.pixel_x - enemy.pixel_x, b.pixel_y - enemy.pixel_y) < TILE_SIZE:
                                enemy.take_damage(b.damage)
                                if enemy.hp <= 0:
                                    enemies.remove(enemy)
                                    global_profile.money += 10 # Thưởng tiền giết địch
                                    # Rớt đồ (30% máu, 50% đạn)
                                    r = random.random()
                                    if r < 0.3: item_drops.append(ItemDrop(enemy.pixel_x, enemy.pixel_y, 'health'))
                                    elif r < 0.8: item_drops.append(ItemDrop(enemy.pixel_x, enemy.pixel_y, 'ammo'))
                                hit = True
                                break
                        if hit: bullets.remove(b)
                
                for enemy in enemies:
                    enemy.move_smoothly()
                    
                # Thu thập nhiên liệu / Tiền
                for data in data_list[:]:
                    dist = math.hypot(player.pixel_x - data.pixel_x, player.pixel_y - data.pixel_y)
                    if dist < TILE_SIZE:
                        data_list.remove(data)
                        global_profile.money += 10
                        score += 10
                        play_sound(coin_sound)
                        ndx, ndy = get_random_pixel_offset(400, 1200)
                        data_list.append(DataCollectible(player.pixel_x + ndx, player.pixel_y + ndy))
                        
                # Thu thập vật phẩm rớt ra
                for item in item_drops[:]:
                    if item.life <= 0:
                        item_drops.remove(item)
                        continue
                    if math.hypot(player.pixel_x - item.pixel_x, player.pixel_y - item.pixel_y) < TILE_SIZE:
                        if item.item_type == 'health':
                            player.hp = min(player.max_hp, player.hp + 50)
                        elif item.item_type == 'ammo':
                            player.ammo = min(player.max_ammo, player.ammo + 20)
                        item_drops.remove(item)
                        play_sound(coin_sound)

                # Va chạm người chơi với địch (Gây sát thương)
                for enemy in enemies[:]:
                    if math.hypot(enemy.pixel_x - player.pixel_x, enemy.pixel_y - player.pixel_y) < TILE_SIZE * 1.1:
                        player.take_damage(20)
                        enemies.remove(enemy) # Địch nổ luôn khi đâm
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)

                # Va chạm với địa hình khổng lồ (Trừ máu)
                for p in level.planets:
                    if math.hypot(player.pixel_x - p.pixel_x, player.pixel_y - p.pixel_y) < p.radius * 0.8 + TILE_SIZE / 2:
                        player.take_damage(50)
                        player.pixel_x -= math.cos(player.angle) * 20 # Bật ra
                        player.pixel_y -= math.sin(player.angle) * 20
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)

                # Va chạm SAM/AAA (Trừ máu)
                for s in level.stakes:
                    if math.hypot(player.pixel_x - s.pixel_x, player.pixel_y - s.pixel_y) < s.radius + TILE_SIZE / 2:
                        player.take_damage(2) # Trừ máu liên tục nếu kẹt trong lưới SAM
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)

            # CAMERA
            camera_x = player.pixel_x + TILE_SIZE // 2 - WIDTH // 2
            camera_y = player.pixel_y + TILE_SIZE // 2 - HEIGHT // 2

            # VẼ
            draw_map_background(screen, camera_x, camera_y)
            level.draw(screen, camera_x, camera_y)
            for data in data_list: data.draw(screen, camera_x, camera_y)
            for item in item_drops: item.draw(screen, camera_x, camera_y)
            
            if show_visualizer and game_state == "PLAYING":
                for enemy in enemies:
                    if enemy.algo_func == dfs_path: color = DFS_COLOR
                    elif enemy.algo_func == bfs_path: color = BFS_COLOR
                    elif enemy.algo_func == astar_path: color = ASTAR_COLOR
                    elif enemy.algo_func == heuristic_path: color = HEURISTIC_COLOR
                    else: color = (255, 255, 255)
                    draw_explored(screen, enemy.explored, color, camera_x, camera_y)
                    draw_enemy_path(screen, enemy.path, color, camera_x, camera_y)

            for b in bullets: b.draw(screen, camera_x, camera_y)
            player.draw(screen, camera_x, camera_y)
            for enemy in enemies: enemy.draw(screen, camera_x, camera_y)

            # HUD Bắn Súng Sinh Tồn
            draw_hud_panel(screen, score, show_visualizer)
            
            # Thanh máu & Đạn
            hp_ratio = player.hp / player.max_hp
            pygame.draw.rect(screen, (255, 0, 0), (10, 60, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (10, 60, int(200 * hp_ratio), 20))
            hp_txt = font.render(f"HP: {int(player.hp)}/{player.max_hp}", True, (255, 255, 255))
            screen.blit(hp_txt, (15, 60))
            
            ammo_txt = font.render(f"Đạn: {player.ammo}/{player.max_ammo}", True, (255, 255, 0))
            screen.blit(ammo_txt, (220, 60))
            
            money_hud = font.render(f"Tiền: {global_profile.money}", True, (50, 255, 50))
            screen.blit(money_hud, (WIDTH - money_hud.get_width() - 10, 60))

            if game_state != "PLAYING":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))
                if game_state == "GAME_OVER":
                    msg = large_font.render("✈ BẠN ĐÃ TỬ TRẬN!", True, (255, 60, 60))
                    sub = font.render(f"Bạn kiếm được {score} Tiền. Nhấn ENTER để về Sảnh chờ.", True, (200, 150, 100))
                else:
                    msg = large_font.render("★ CHIẾN THẮNG! ★", True, (80, 255, 100))
                    sub = font.render(f"Bạn sống sót và mang về {score} Tiền. Nhấn ENTER để về Sảnh chờ.", True, (255, 220, 60))
                screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 70))
                screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
"""

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(top_content + new_main)

print("Patched main.py successfully.")
