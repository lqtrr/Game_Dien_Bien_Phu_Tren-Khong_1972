import sys

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure to import CombatBase
if "CombatBase" not in content:
    content = content.replace("ItemDrop, BossB52\n", "ItemDrop, BossB52, CombatBase\n")

idx = content.find('def main():')
if idx == -1:
    sys.exit(1)

top_content = content[:idx]

new_main = """def main():
    running = True
    app_state = "MAIN_MENU" # "MAIN_MENU", "UPGRADE", "PLAYING"
    game_state = "PLAYING"  # "PLAYING", "GAME_OVER", "WIN"
    current_level = 1
    
    level = None
    player = None
    base = None
    enemies = []
    data_list = []
    bullets = []
    item_drops = []
    score = 0
    show_visualizer = False

    lobby_bg = None
    bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'lobby_bg.png')
    if os.path.exists(bg_path):
        try:
            lobby_bg = pygame.image.load(bg_path).convert()
            lobby_bg = pygame.transform.scale(lobby_bg, (WIDTH, HEIGHT))
        except: pass
        
    player_ship_lobby = None
    ship_path = os.path.join(os.path.dirname(__file__), 'assets', 'player_ship.png')
    if os.path.exists(ship_path):
        try:
            player_ship_lobby = pygame.image.load(ship_path).convert_alpha()
            player_ship_lobby = pygame.transform.scale(player_ship_lobby, (300, 300))
            player_ship_lobby = pygame.transform.rotate(player_ship_lobby, -90) # Xoay ngang ra
        except: pass

    AI_UPDATE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(AI_UPDATE_EVENT, 500)

    while running:
        if app_state == "MAIN_MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: current_level = 1
                    elif event.key == pygame.K_2: current_level = 2
                    elif event.key == pygame.K_3: current_level = 3
                    elif event.key == pygame.K_4: current_level = 4
                    elif event.key == pygame.K_u: app_state = "UPGRADE"
                    elif event.key == pygame.K_RETURN:
                        # Bắt đầu game theo màn
                        level = Level()
                        player = Player(0, 0)
                        base = CombatBase(0, 0) # Khởi tạo cứ điểm
                        level.init_level(0, 0)
                        enemies = []
                        
                        if current_level == 1:
                            # 8 địch, chậm
                            for _ in range(2):
                                enemies.append(DFSEnemy(get_random_pixel_offset(1000, 2000)[0], get_random_pixel_offset(1000, 2000)[1]))
                                enemies.append(BFSEnemy(get_random_pixel_offset(1000, 2000)[0], get_random_pixel_offset(1000, 2000)[1]))
                                enemies.append(AStarEnemy(get_random_pixel_offset(1000, 2000)[0], get_random_pixel_offset(1000, 2000)[1]))
                                enemies.append(HeuristicEnemy(get_random_pixel_offset(1000, 2000)[0], get_random_pixel_offset(1000, 2000)[1]))
                            for e in enemies: e.max_speed *= 0.7
                            pygame.time.set_timer(AI_UPDATE_EVENT, 500)
                        elif current_level == 2:
                            # 16 địch, update nhanh hơn
                            for _ in range(4):
                                enemies.append(DFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(BFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(AStarEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(HeuristicEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                            pygame.time.set_timer(AI_UPDATE_EVENT, 200)
                        elif current_level == 3:
                            # 16 địch, biết bắn đạn
                            for _ in range(4):
                                enemies.append(DFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(BFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(AStarEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                                enemies.append(HeuristicEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))
                            pygame.time.set_timer(AI_UPDATE_EVENT, 300)
                        elif current_level == 4:
                            # Boss B52 + 4 cận vệ
                            enemies.append(BossB52(1500, 0))
                            enemies.append(AStarEnemy(1500, 200))
                            enemies.append(AStarEnemy(1500, -200))
                            enemies.append(HeuristicEnemy(1700, 100))
                            enemies.append(HeuristicEnemy(1700, -100))
                            pygame.time.set_timer(AI_UPDATE_EVENT, 300)
                            
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
                            enemy.update_path(0, 0, level) # Mặc định ngắm vào base
            
            # Vẽ Sảnh chờ
            if lobby_bg:
                screen.blit(lobby_bg, (0, 0))
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))
            else:
                screen.fill((10, 20, 10))
                
            if player_ship_lobby:
                screen.blit(player_ship_lobby, (50, HEIGHT//2 - 150))
            
            # Tiêu đề
            main_title = "ĐIỆN BIÊN PHỦ TRÊN KHÔNG"
            t_shadow = large_font.render(main_title, True, (0, 0, 0))
            screen.blit(t_shadow, (WIDTH//2 - t_shadow.get_width()//2 + 5, 85))
            t_glow = large_font.render(main_title, True, (255, 50, 50))
            screen.blit(t_glow, (WIDTH//2 - t_glow.get_width()//2, 80))
            title = large_font.render(main_title, True, (255, 255, 150))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            
            subtitle = font.render(f"SẢNH CHỜ XUẤT KÍCH - CHỌN MÀN CHƠI", True, (200, 255, 200))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 130))
            
            money_txt = font.render(f"Tiền (Nhiên liệu): {global_profile.money}", True, DATA_COLOR)
            screen.blit(money_txt, (WIDTH//2 - money_txt.get_width()//2, 180))
            
            lvl_names = ["Màn 1: Tân Binh (Dễ)", "Màn 2: Không Chiến (Vừa)", "Màn 3: Bão Lửa (Khó)", "Màn 4: Boss B-52 (Cực Khó)"]
            
            for i in range(1, 5):
                color = (255, 255, 50) if current_level == i else (150, 150, 150)
                txt = font.render(f"[{i}] {lvl_names[i-1]}", True, color)
                screen.blit(txt, (WIDTH//2 - 100, 230 + i*40))
            
            help_txt = font.render("Nhấn Phím số [1-4] để Chọn Màn | [ENTER] để Bay | [U] Nâng Cấp", True, (255, 255, 255))
            screen.blit(help_txt, (WIDTH//2 - help_txt.get_width()//2, 450))
            
        elif app_state == "UPGRADE":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        app_state = "MAIN_MENU"
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
                            
            if lobby_bg:
                screen.blit(lobby_bg, (0, 0))
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
            else:
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
                            app_state = "MAIN_MENU" # Về sảnh sau khi chết/thắng
                if game_state == "PLAYING":
                    if event.type == AI_UPDATE_EVENT and not show_visualizer:
                        for enemy in enemies:
                            dist = math.hypot(enemy.pixel_x - player.pixel_x, enemy.pixel_y - player.pixel_y)
                            if dist < 800:
                                # Bay gần player thì truy sát player
                                enemy.update_path(player.r, player.c, level)
                            else:
                                # Không thì đâm thẳng vào Cứ điểm (0, 0)
                                enemy.update_path(0, 0, level)
            
            if game_state == "PLAYING" and not show_visualizer:
                keys = pygame.key.get_pressed()
                player.update_movement(keys)
                
                # Bắn đạn laze đôi từ 2 cánh (Player)
                if (keys[pygame.K_z] or pygame.mouse.get_pressed()[0]) and player.fire_cooldown <= 0 and player.ammo > 0:
                    player.ammo -= 1
                    player.fire_cooldown = global_profile.get_fire_cooldown()
                    wing_offset = TILE_SIZE * 0.7
                    dx = math.cos(player.angle + math.pi/2) * wing_offset
                    dy = math.sin(player.angle + math.pi/2) * wing_offset
                    bullets.append(Bullet(player.pixel_x + dx, player.pixel_y + dy, player.angle, speed=25, damage=global_profile.get_damage(), is_player=True))
                    bullets.append(Bullet(player.pixel_x - dx, player.pixel_y - dy, player.angle, speed=25, damage=global_profile.get_damage(), is_player=True))
                    play_sound(shoot_sound)
                
                level.update(player.pixel_x, player.pixel_y)
                
                # Địch bắn trả (Level 3 & 4)
                if current_level >= 3:
                    for enemy in enemies:
                        if enemy.fire_cooldown > 0:
                            enemy.fire_cooldown -= 1
                        else:
                            # Khoảng cách < 800 thì bắn
                            dist_to_player = math.hypot(player.pixel_x - enemy.pixel_x, player.pixel_y - enemy.pixel_y)
                            if dist_to_player < 800:
                                enemy.fire_cooldown = 120 # 2 giây bắn 1 lần
                                if enemy.is_boss:
                                    enemy.fire_cooldown = 60 # Boss bắn nhanh hơn
                                    for ang_offset in [-0.2, 0, 0.2]:
                                        bullets.append(Bullet(enemy.pixel_x, enemy.pixel_y, enemy.angle + ang_offset, speed=12, damage=15, is_player=False))
                                else:
                                    bullets.append(Bullet(enemy.pixel_x, enemy.pixel_y, enemy.angle, speed=10, damage=10, is_player=False))
                                play_sound(shoot_sound)
                
                # Cập nhật đạn
                for b in bullets[:]:
                    b.update()
                    if b.life <= 0:
                        bullets.remove(b)
                        continue
                    
                    if b.is_player:
                        hit = False
                        for enemy in enemies[:]:
                            hitbox_radius = TILE_SIZE * 2 if enemy.is_boss else TILE_SIZE
                            if math.hypot(b.pixel_x - enemy.pixel_x, b.pixel_y - enemy.pixel_y) < hitbox_radius:
                                enemy.take_damage(b.damage)
                                if enemy.hp <= 0:
                                    enemies.remove(enemy)
                                    global_profile.money += (100 if enemy.is_boss else 10)
                                    r = random.random()
                                    if r < 0.3: item_drops.append(ItemDrop(enemy.pixel_x, enemy.pixel_y, 'health'))
                                    elif r < 0.8: item_drops.append(ItemDrop(enemy.pixel_x, enemy.pixel_y, 'ammo'))
                                hit = True
                                break
                        if hit: bullets.remove(b)
                    else:
                        # Đạn địch trúng người chơi
                        if math.hypot(b.pixel_x - player.pixel_x, b.pixel_y - player.pixel_y) < TILE_SIZE:
                            player.take_damage(b.damage)
                            bullets.remove(b)
                            if player.hp <= 0:
                                game_state = "GAME_OVER"
                                play_sound(game_over_sound)
                        # Đạn địch trúng Cứ điểm
                        elif math.hypot(b.pixel_x - base.pixel_x, b.pixel_y - base.pixel_y) < base.radius:
                            base.take_damage(b.damage)
                            bullets.remove(b)
                
                for enemy in enemies[:]:
                    enemy.move_smoothly()
                    # Kẻ địch đâm vào cứ điểm
                    if math.hypot(enemy.pixel_x - base.pixel_x, enemy.pixel_y - base.pixel_y) < base.radius + TILE_SIZE:
                        base.take_damage(200 if enemy.is_boss else 50)
                        enemies.remove(enemy) # Địch nổ luôn khi đâm
                    
                # Thu thập nhiên liệu
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

                # Va chạm người chơi với địch
                for enemy in enemies[:]:
                    hitbox_radius = TILE_SIZE * 2 if enemy.is_boss else TILE_SIZE * 1.1
                    if math.hypot(enemy.pixel_x - player.pixel_x, enemy.pixel_y - player.pixel_y) < hitbox_radius:
                        player.take_damage(50 if enemy.is_boss else 20)
                        if not enemy.is_boss:
                            enemies.remove(enemy)
                        else:
                            player.pixel_x -= math.cos(player.angle) * 30
                            player.pixel_y -= math.sin(player.angle) * 30
                            
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)

                # Va chạm với địa hình khổng lồ
                for p in level.planets:
                    if math.hypot(player.pixel_x - p.pixel_x, player.pixel_y - p.pixel_y) < p.radius * 0.8 + TILE_SIZE / 2:
                        player.take_damage(50)
                        player.pixel_x -= math.cos(player.angle) * 20
                        player.pixel_y -= math.sin(player.angle) * 20
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)

                # Va chạm SAM/AAA
                for s in level.stakes:
                    if math.hypot(player.pixel_x - s.pixel_x, player.pixel_y - s.pixel_y) < s.radius + TILE_SIZE / 2:
                        player.take_damage(2)
                        if player.hp <= 0:
                            game_state = "GAME_OVER"
                            play_sound(game_over_sound)
                            
                # Check Win/Lose Condition
                if base.hp <= 0:
                    game_state = "GAME_OVER"
                    play_sound(game_over_sound)
                elif len(enemies) == 0:
                    game_state = "WIN"
                    global_profile.money += current_level * 100
                    play_sound(win_sound)

            # CAMERA
            camera_x = player.pixel_x + TILE_SIZE // 2 - WIDTH // 2
            camera_y = player.pixel_y + TILE_SIZE // 2 - HEIGHT // 2

            # VẼ
            draw_map_background(screen, camera_x, camera_y)
            level.draw(screen, camera_x, camera_y)
            
            # VẼ CỨ ĐIỂM
            base.draw(screen, camera_x, camera_y)
            
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
            
            if game_state == "PLAYING":
                for enemy in enemies:
                    if enemy.algo_func == dfs_path: color = DFS_COLOR
                    elif enemy.algo_func == bfs_path: color = BFS_COLOR
                    elif enemy.algo_func == astar_path: color = ASTAR_COLOR
                    elif enemy.algo_func == heuristic_path: color = HEURISTIC_COLOR
                    else: color = (255, 255, 255)
                    draw_enemy_path(screen, enemy.path, color, camera_x, camera_y)

            for b in bullets: b.draw(screen, camera_x, camera_y)
            player.draw(screen, camera_x, camera_y)
            for enemy in enemies: enemy.draw(screen, camera_x, camera_y)

            # HUD
            draw_hud_panel(screen, score, show_visualizer)
            
            hp_ratio = player.hp / player.max_hp
            pygame.draw.rect(screen, (255, 0, 0), (10, 60, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (10, 60, int(200 * hp_ratio), 20))
            hp_txt = font.render(f"HP MiG-21: {int(player.hp)}/{player.max_hp}", True, (255, 255, 255))
            screen.blit(hp_txt, (15, 60))
            
            # HUD Cứ điểm
            base_hp_ratio = base.hp / base.max_hp
            pygame.draw.rect(screen, (255, 0, 0), (10, 85, 200, 15))
            pygame.draw.rect(screen, (100, 255, 100), (10, 85, int(200 * base_hp_ratio), 15))
            base_hp_txt = small_font.render(f"HP Cứ Điểm: {int(base.hp)}/{base.max_hp}", True, (255, 255, 255))
            screen.blit(base_hp_txt, (15, 83))
            
            ammo_txt = font.render(f"Đạn: {player.ammo}/{player.max_ammo}", True, (255, 255, 0))
            screen.blit(ammo_txt, (220, 60))
            
            money_hud = font.render(f"Tiền: {global_profile.money}", True, (50, 255, 50))
            screen.blit(money_hud, (WIDTH - money_hud.get_width() - 10, 60))

            draw_minimap(screen, level, player, enemies, data_list)

            ctrl_text = small_font.render("Z / Click chuột: Bắn  |  SPACE: Radar AI  |  Mũi tên: Lái", True, (160, 220, 120))
            ctrl_bg = pygame.Surface((ctrl_text.get_width() + 16, ctrl_text.get_height() + 6), pygame.SRCALPHA)
            ctrl_bg.fill((5, 20, 5, 180))
            screen.blit(ctrl_bg, (6, HEIGHT - ctrl_text.get_height() - 10))
            screen.blit(ctrl_text, (14, HEIGHT - ctrl_text.get_height() - 7))

            if game_state != "PLAYING":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))
                if game_state == "GAME_OVER":
                    if base.hp <= 0:
                        msg = large_font.render("✈ CỨ ĐIỂM BỊ PHÁ HỦY — THẤT BẠI!", True, (255, 60, 60))
                    else:
                        msg = large_font.render("✈ BẠN ĐÃ TỬ TRẬN!", True, (255, 60, 60))
                    sub = font.render(f"Thử lại Màn {current_level}. Nhấn ENTER để về Sảnh chờ.", True, (200, 150, 100))
                else:
                    msg = large_font.render(f"★ HOÀN THÀNH MÀN {current_level}! ★", True, (80, 255, 100))
                    sub = font.render(f"Thưởng {current_level * 100} Tiền. Nhấn ENTER để về Sảnh chờ.", True, (255, 220, 60))
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

print("Patched main.py successfully for Base Defense.")
