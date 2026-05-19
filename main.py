import pygame
import sys
import random
import math
import os
from settings import *
from level import Level
from entities import Player, DFSEnemy, BFSEnemy, AStarEnemy, HeuristicEnemy, DataCollectible, global_profile, Bullet, ItemDrop, BossB52, CombatBase
from algorithms import dfs_path, bfs_path, astar_path, heuristic_path
from collision import SpatialHash, get_distance
from difficulty import difficulty_manager, Difficulty

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dien Bien Phu Tren Khong 1972 - Bao Ve Bau Troi")
clock = pygame.time.Clock()

try:
    pygame.mixer.init()
    base_dir = os.path.dirname(__file__)
    coin_sound = pygame.mixer.Sound(os.path.join(base_dir, "assets", "coin.wav"))
    game_over_sound = pygame.mixer.Sound(os.path.join(base_dir, "assets", "game_over.wav"))
    win_sound = pygame.mixer.Sound(os.path.join(base_dir, "assets", "win.wav"))
    shoot_sound = pygame.mixer.Sound(os.path.join(base_dir, "assets", "shoot_sound.wav"))
    shoot_sound.set_volume(0.3)
except Exception as e:
    print("❌ Không thể tải âm thanh:", e)
    coin_sound = game_over_sound = win_sound = shoot_sound = None

# ◆ Load nhạc nền
background_music_loaded = False
try:
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, "assets")

    # Tìm file nhạc nền (tên file rất dài)
    music_filename = "(477) Nhạc Hiệu Không Lời - Chiến Thắng Điện Biên - Nhạc Hiệu Đài Tiếng Nói Việt Nam. - YouTube.mp3"
    music_path = os.path.join(assets_dir, music_filename)

    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)  # Volume 40% để không quá to
        background_music_loaded = True
        print(f"✅ Đã load nhạc nền: {music_filename}")
    else:
        print(f"⚠️  Không tìm thấy nhạc nền: {music_filename}")
except Exception as e:
    print(f"⚠️  Lỗi load nhạc nền: {e}")
    background_music_loaded = False

# ── Bảng màu địa hình (topo map quân sự) ─────────────────────────
_TERRAIN_COLORS = [
    (18, 45, 18),   # thung lũng sâu
    (22, 55, 22),   # đồng bằng thấp
    (28, 68, 28),   # đồng bằng
    (32, 78, 30),   # đồi thấp
    (38, 88, 32),   # đồi cao
    (46, 98, 36),   # núi trung bình
    (54, 108, 40),  # núi cao
    (62, 118, 44),  # đỉnh núi
]

_OCEAN_COLORS = [
    (10, 25, 45),   # rãnh sâu
    (15, 35, 60),   # biển sâu
    (20, 45, 75),   # biển giữa
    (25, 55, 90),   # biển nông
    (30, 65, 105),  # thềm lục địa
    (35, 75, 115),  # ven bờ
    (40, 85, 125),  # sóng biển
    (45, 95, 135),  # bọt biển
]

# Bộ nhớ cache surface địa hình để tránh vẽ lại toàn bộ mỗi frame
_terrain_cache = {}

def play_sound(sound):
    if sound:
        sound.play()

def _load_font(size, bold=True):
    """Try a chain of fonts that all support Vietnamese Unicode on Windows."""
    for name in ['segoeui', 'tahoma', 'arial', 'verdana']:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            # Quick sanity-check: render a Vietnamese glyph
            f.render('\u0110i\u1ec7n Bi\u00ean Ph\u1ee7', True, (255,255,255))
            return f
        except Exception:
            continue
    return pygame.font.Font(None, size + 8)  # pygame built-in fallback

def preload_assets():
    """Preload toàn bộ assets cần thiết — fail early nếu asset missing"""
    assets_to_check = [
        ('assets/coin.wav', 'sound'),
        ('assets/game_over.wav', 'sound'),
        ('assets/win.wav', 'sound'),
        ('assets/shoot_sound.wav', 'sound'),
        ('assets/player_ship.png', 'image'),
        ('assets/dfs_ship.png', 'image'),
        ('assets/bfs_ship.png', 'image'),
        ('assets/astar_ship.png', 'image'),
        ('assets/heuristic_ship.png', 'image'),
        ('assets/lobby_bg.png', 'image'),
    ]

    missing_assets = []
    for asset_path, asset_type in assets_to_check:
        full_path = os.path.join(os.path.dirname(__file__), asset_path)
        if not os.path.exists(full_path):
            missing_assets.append(f"  ❌ {asset_path} ({asset_type})")

    if missing_assets:
        print("⚠️  CẢNH BÁO: Các assets bị thiếu:")
        for msg in missing_assets:
            print(msg)
        print("\n💡 Gợi ý: Tạo thư mục 'assets/' và thêm các file trên.")
        print("   Game sẽ chạy nhưng sẽ dùng fallback colors thay vì hình ảnh.\n")
    else:
        print("✅ Tất cả assets đã preload thành công!\n")

font       = _load_font(22)
large_font = _load_font(38)
small_font = _load_font(17)
title_font = _load_font(14)

def _terrain_height(wx, wy):
    """Pseudo-height map dựa trên sine/cosine nhiều tần số — không lặp trong phạm vi game."""
    nx = wx / 600.0
    ny = wy / 600.0
    h  = (math.sin(nx * 1.3 + ny * 0.7) * 0.30
        + math.sin(nx * 0.5 - ny * 1.1) * 0.25
        + math.sin(nx * 2.1 + ny * 1.9) * 0.15
        + math.sin(nx * 0.8 + wy / 400.0) * 0.20
        + math.cos(nx * 1.7 - ny * 0.4) * 0.10)
    return (h + 1.0) / 2.0   # Chuẩn hoá về [0, 1]

# Kích thước ô địa hình vẽ trên màn hình (px)
_CELL = 40

def draw_map_background(screen, camera_x, camera_y):
    """
    Vẽ nền bản đồ địa hình kiểu quân sự (topographic map).
    Màu biến đổi theo độ cao giả — không tile ảnh → không bao giờ lặp.
    Thêm đường đồng mức (contour lines) và lưới toạ độ quân sự.
    """
    n_colors = len(_TERRAIN_COLORS)

    # ── 1. Vẽ các ô màu địa hình (Nền cơ sở cho vô tận) ─────────────
    # Tính offset sao cho lưới đồng bộ với camera (scroll mượt)
    off_x = int(camera_x) % _CELL
    off_y = int(camera_y) % _CELL

    cols = WIDTH  // _CELL + 2
    rows = HEIGHT // _CELL + 2

    for row in range(rows):
        for col in range(cols):
            sx = col * _CELL - off_x
            sy = row * _CELL - off_y
            # Toạ độ thế giới thực của góc trên-trái ô này
            wx = camera_x + sx
            wy = camera_y + sy
            h_val = _terrain_height(wx, wy)
            idx = min(int(h_val * n_colors), n_colors - 1)
            
            # Phía Đông (Biển / Vịnh Bắc Bộ)
            if wx > 3000:
                color = _OCEAN_COLORS[idx]
            else:
                color = _TERRAIN_COLORS[idx]
                
            pygame.draw.rect(screen, color, (sx, sy, _CELL + 1, _CELL + 1))

    # (Đã loại bỏ ảnh tĩnh bản đồ Việt Nam để dùng lại 100% bản đồ procedural)

    # ── 2. Đường đồng mức (contour lines) — vẽ theo ô, hiệu suất cao ─
    contour_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    CONTOUR_THRESHOLDS = (0.25, 0.50, 0.75)
    # Quét các ô, nếu 2 ô kề nhau vượt qua ngưỡng thì vẽ đường đồng mức
    for row in range(rows):
        for col in range(cols):
            sx = col * _CELL - off_x
            sy = row * _CELL - off_y
            wx = camera_x + sx;  wy = camera_y + sy
            h_tl = _terrain_height(wx,          wy)
            h_tr = _terrain_height(wx + _CELL,  wy)
            h_bl = _terrain_height(wx,          wy + _CELL)
            for thr in CONTOUR_THRESHOLDS:
                # Cạnh trên (ngang)
                if (h_tl < thr) != (h_tr < thr):
                    t = (thr - h_tl) / (h_tr - h_tl + 1e-9)
                    px = int(sx + t * _CELL)
                    pygame.draw.line(contour_surf, (65, 150, 65, 70),
                                     (px, sy), (px, sy + 2), 1)
                # Cạnh trái (dọc)
                if (h_tl < thr) != (h_bl < thr):
                    t = (thr - h_tl) / (h_bl - h_tl + 1e-9)
                    py = int(sy + t * _CELL)
                    pygame.draw.line(contour_surf, (65, 150, 65, 70),
                                     (sx, py), (sx + 2, py), 1)
    screen.blit(contour_surf, (0, 0))

    # ── 3. Lưới toạ độ quân sự (ô lớn) ─────────────────────────────
    grid_step = _CELL * 8   # Lưới lớn mỗi 8 ô = 320px
    grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    gx_off = int(camera_x) % grid_step
    line_x = -gx_off
    while line_x < WIDTH:
        pygame.draw.line(grid_surf, (70, 160, 70, 45),
                         (int(line_x), 0), (int(line_x), HEIGHT), 1)
        line_x += grid_step

    gy_off = int(camera_y) % grid_step
    line_y = -gy_off
    while line_y < HEIGHT:
        pygame.draw.line(grid_surf, (70, 160, 70, 45),
                         (0, int(line_y)), (WIDTH, int(line_y)), 1)
        line_y += grid_step

    screen.blit(grid_surf, (0, 0))

    # ── 4. Nhãn toạ độ quân sự ──────────────────────────────────────
    coord_font = pygame.font.SysFont('tahoma', 10)
    gx_off = int(camera_x) % grid_step
    lx = -gx_off
    while lx < WIDTH:
        coord_x = int((camera_x + lx) / grid_step)
        lbl = coord_font.render(f"{coord_x:+d}", True, (80, 160, 80))
        screen.blit(lbl, (int(lx) + 2, HEIGHT - 16))
        lx += grid_step

    gy_off = int(camera_y) % grid_step
    ly = -gy_off
    while ly < HEIGHT:
        coord_y = int((camera_y + ly) / grid_step)
        lbl = coord_font.render(f"{coord_y:+d}", True, (80, 160, 80))
        screen.blit(lbl, (2, int(ly) + 2))
        ly += grid_step

def draw_explored(screen, explored_set, color_rgb, cx=0, cy=0):
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fill_color = color_rgb + (130,)
    for (r, c) in explored_set:
        x = c * TILE_SIZE - cx
        y = r * TILE_SIZE - cy
        if -TILE_SIZE <= x <= WIDTH and -TILE_SIZE <= y <= HEIGHT:
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, fill_color, rect)
    screen.blit(surface, (0, 0))

def draw_enemy_path(screen, path, color_rgb, cx=0, cy=0):
    if not path or len(path) < 2:
        return
    
    points = []
    for (r, c) in path:
        # Tọa độ tâm của ô
        x = c * TILE_SIZE + TILE_SIZE // 2 - cx
        y = r * TILE_SIZE + TILE_SIZE // 2 - cy
        points.append((x, y))
        
    if len(points) >= 2:
        pygame.draw.lines(screen, color_rgb, False, points, 3)
        # Vẽ điểm nhắm mục tiêu ở cuối đường
        pygame.draw.circle(screen, (255, 0, 0), points[-1], 5)

def get_random_pixel_offset(radius_min, radius_max):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(radius_min, radius_max)
    return math.cos(angle) * dist, math.sin(angle) * dist

def spawn_level_enemies(level_num, current_level):
    """
    Spawn enemies dựa trên difficulty config
    Trả về (enemies_list, ai_update_interval_ms, config)
    """
    config = difficulty_manager.get_config(level_num)

    # Debug info
    print(f"🎮 Chế độ: {config.name}")
    print(f"   Kẻ địch: DFS×{config.dfs_count} BFS×{config.bfs_count} A*×{config.astar_count} Heuristic×{config.heuristic_count}")
    print(f"   Tốc độ AI: {config.ai_update_interval}ms")

    enemies = []

    # Spawn thường xuyên enemies
    for _ in range(config.dfs_count):
        enemies.append(DFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))

    for _ in range(config.bfs_count):
        enemies.append(BFSEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))

    for _ in range(config.astar_count):
        enemies.append(AStarEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))

    for _ in range(config.heuristic_count):
        enemies.append(HeuristicEnemy(get_random_pixel_offset(1000, 2500)[0], get_random_pixel_offset(1000, 2500)[1]))

    # Spawn boss nếu cần
    if config.boss_enabled:
        enemies.append(BossB52(1500, 0))

    # Áp dụng multipliers từ config
    for e in enemies:
        e.max_speed *= config.enemy_speed_multiplier

    # Adjust player HP
    if current_level:
        current_level.max_hp = int(current_level.max_hp * config.player_hp_multiplier)
        current_level.hp = current_level.max_hp

    return enemies, config.ai_update_interval, config

def draw_minimap(screen, level, player, enemies, data_list):
    scale = 0.05
    map_w = 200
    map_h = 200
    margin_top = 10
    margin_right = 10
    start_x = WIDTH - map_w - margin_right
    start_y = margin_top

    # Nền radar — màu xanh tối quân sự
    pygame.draw.rect(screen, (5, 20, 5), (start_x, start_y, map_w, map_h))
    pygame.draw.rect(screen, (60, 180, 60), (start_x, start_y, map_w, map_h), 2)

    # Tiêu đề radar
    radar_label = title_font.render("RADAR", True, (80, 220, 80))
    screen.blit(radar_label, (start_x + map_w // 2 - radar_label.get_width() // 2, start_y + 2))

    def to_minimap(px, py):
        rel_x = (px - player.pixel_x) * scale
        rel_y = (py - player.pixel_y) * scale
        return int(start_x + map_w / 2 + rel_x), int(start_y + map_h / 2 + rel_y)

    # (Đã loại bỏ vẽ 2 vách núi trên radar vì bản đồ vô tận)

    def is_in_minimap(px, py):
        """Check nhanh nếu object trong khu vực minimap"""
        x = int(start_x + map_w / 2 + (px - player.pixel_x) * scale)
        y = int(start_y + map_h / 2 + (py - player.pixel_y) * scale)
        return start_x - 10 <= x <= start_x + map_w + 10 and start_y - 10 <= y <= start_y + map_h + 10

    # Khoảng cách tối đa từ player trên minimap (để cull)
    minimap_range = int(map_w / scale / 2)

    # Vẽ vị trí địa hình (mountains) — chỉ vẽ những cái gần player
    for p in level.planets:
        if abs(p.pixel_x - player.pixel_x) < minimap_range and abs(p.pixel_y - player.pixel_y) < minimap_range:
            px, py = to_minimap(p.pixel_x, p.pixel_y)
            if is_in_minimap(p.pixel_x, p.pixel_y):
                pygame.draw.circle(screen, (40, 120, 40), (px, py), max(2, int(p.radius * scale)))

    # Vẽ mảnh núi trôi — chỉ vẽ những cái gần
    for m in level.meteors:
        if abs(m.pixel_x - player.pixel_x) < minimap_range and abs(m.pixel_y - player.pixel_y) < minimap_range:
            mx, my = to_minimap(m.pixel_x, m.pixel_y)
            if is_in_minimap(m.pixel_x, m.pixel_y):
                pygame.draw.circle(screen, WALL_COLOR, (mx, my), max(1, int(m.radius * scale)))

    # Vẽ vị trí SAM/AAA (màu đỏ cam nhấp nháy)
    t = pygame.time.get_ticks()
    for s in level.stakes:
        if abs(s.pixel_x - player.pixel_x) < minimap_range and abs(s.pixel_y - player.pixel_y) < minimap_range:
            sx, sy = to_minimap(s.pixel_x, s.pixel_y)
            if is_in_minimap(s.pixel_x, s.pixel_y):
                glow = abs(math.sin(t * 0.006 + s.pulse_offset))
                col = (int(255 * glow), int(80 * glow), 0)
                pygame.draw.circle(screen, col, (sx, sy), 3)

    # Vẽ nhiên liệu — chỉ vẽ những cái gần
    for d in data_list:
        if abs(d.pixel_x - player.pixel_x) < minimap_range and abs(d.pixel_y - player.pixel_y) < minimap_range:
            dx, dy = to_minimap(d.pixel_x, d.pixel_y)
            if is_in_minimap(d.pixel_x, d.pixel_y):
                pygame.draw.circle(screen, DATA_COLOR, (dx, dy), 2)

    # Vẽ sân bay đích
    if is_in_minimap(level.exit_pos_pixel[0], level.exit_pos_pixel[1]):
        ex, ey = to_minimap(level.exit_pos_pixel[0], level.exit_pos_pixel[1])
        pygame.draw.circle(screen, EXIT_COLOR, (ex, ey), 5)
        pygame.draw.circle(screen, (255, 255, 255), (ex, ey), 5, 1)

    # Vẽ máy bay địch
    for e in enemies:
        if abs(e.pixel_x - player.pixel_x) < minimap_range and abs(e.pixel_y - player.pixel_y) < minimap_range:
            ex, ey = to_minimap(e.pixel_x, e.pixel_y)
            if is_in_minimap(e.pixel_x, e.pixel_y):
                from algorithms import dfs_path, bfs_path, astar_path, heuristic_path
                color = (255, 0, 0)
                if e.algo_func == dfs_path: color = DFS_COLOR
                elif e.algo_func == bfs_path: color = BFS_COLOR
                elif e.algo_func == astar_path: color = ASTAR_COLOR
                elif e.algo_func == heuristic_path: color = HEURISTIC_COLOR
                pygame.draw.circle(screen, color, (ex, ey), 4)
                pygame.draw.circle(screen, (255, 255, 255), (ex, ey), 4, 1)

    # Vị trí MiG-21 người chơi (tâm radar — màu đỏ sao vàng)
    pygame.draw.circle(screen, PLAYER_COLOR, (int(start_x + map_w / 2), int(start_y + map_h / 2)), 5)
    pygame.draw.circle(screen, (255, 255, 0), (int(start_x + map_w / 2), int(start_y + map_h / 2)), 5, 2)

def draw_hud_panel(screen, score, show_visualizer):
    """HUD thanh thông tin trên cùng — phong cách bảng điều khiển buồng lái"""
    panel = pygame.Surface((WIDTH, 48), pygame.SRCALPHA)
    panel.fill((5, 20, 5, 200))
    screen.blit(panel, (0, 0))
    pygame.draw.line(screen, (60, 180, 60), (0, 47), (WIDTH, 47), 1)

    # Tiêu đề nhiệm vụ
    title = font.render("✈ ĐIỆN BIÊN PHỦ TRÊN KHÔNG 1972 — BẢO VỆ HÀ NỘI", True, (180, 255, 100))
    screen.blit(title, (10, 12))

    # Hiển thị nhiên liệu (score)
    fuel_text = font.render(f"⛽ Nhiên liệu: {score}", True, DATA_COLOR)
    screen.blit(fuel_text, (WIDTH - fuel_text.get_width() - 220, 12))

def update_spatial_hash(spatial_hash, player, enemies, data_list, level):
    """Cập nhật spatial hash với vị trí tất cả objects"""
    if not spatial_hash:
        return

    spatial_hash.clear()

    # Thêm player
    spatial_hash.insert(player, 'player', TILE_SIZE)

    # Thêm enemies
    for i, enemy in enumerate(enemies):
        spatial_hash.insert(enemy, f'enemy_{i}', TILE_SIZE * 2)

    # Thêm data collectibles
    for i, data in enumerate(data_list):
        spatial_hash.insert(data, f'data_{i}', TILE_SIZE)

    # Thêm level objects
    for i, planet in enumerate(level.planets):
        spatial_hash.insert(planet, f'planet_{i}', planet.radius)

    for i, meteor in enumerate(level.meteors):
        spatial_hash.insert(meteor, f'meteor_{i}', meteor.radius)

    for i, stake in enumerate(level.stakes):
        spatial_hash.insert(stake, f'stake_{i}', stake.radius)

def draw_hud_panel(screen, score, show_visualizer):
    """HUD thanh thông tin trên cùng — phong cách bảng điều khiển buồng lái"""
    panel = pygame.Surface((WIDTH, 48), pygame.SRCALPHA)
    panel.fill((5, 20, 5, 200))
    screen.blit(panel, (0, 0))
    pygame.draw.line(screen, (60, 180, 60), (0, 47), (WIDTH, 47), 1)

    # Tiêu đề nhiệm vụ
    title = font.render("✈ ĐIỆN BIÊN PHỦ TRÊN KHÔNG 1972 — BẢO VỆ HÀ NỘI", True, (180, 255, 100))
    screen.blit(title, (10, 12))

    # Hiển thị nhiên liệu (score)
    fuel_text = font.render(f"⛽ Nhiên liệu: {score}", True, DATA_COLOR)
    screen.blit(fuel_text, (WIDTH - fuel_text.get_width() - 220, 12))

def main():
    running = True
    app_state = "MAIN_MENU" # "MAIN_MENU", "UPGRADE", "PLAYING"
    game_state = "PLAYING"  # "PLAYING", "GAME_OVER", "WIN"
    current_level = 1

    # ◆ Preload assets - check early
    preload_assets()

    level = None
    player = None
    base = None
    enemies = []
    data_list = []
    bullets = []
    item_drops = []
    score = 0
    show_visualizer = False
    spatial_hash = None  # Sẽ được khởi tạo khi game bắt đầu
    current_difficulty_config = None  # Lưu difficulty config của màn chơi hiện tại

    lobby_bg = None
    bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'lobby_bg.png')
    if os.path.exists(bg_path):
        try:
            lobby_bg = pygame.image.load(bg_path).convert()
            lobby_bg = pygame.transform.scale(lobby_bg, (WIDTH, HEIGHT))
        except (pygame.error, IOError) as e:
            print(f"⚠️ Không thể load lobby background: {e}")

    player_ship_lobby = None
    ship_path = os.path.join(os.path.dirname(__file__), 'assets', 'player_ship.png')
    if os.path.exists(ship_path):
        try:
            player_ship_lobby = pygame.image.load(ship_path).convert_alpha()
            player_ship_lobby = pygame.transform.scale(player_ship_lobby, (300, 300))
            player_ship_lobby = pygame.transform.rotate(player_ship_lobby, -90) # Xoay ngang ra
        except (pygame.error, IOError) as e:
            print(f"⚠️ Không thể load player ship lobby: {e}")

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
                        spatial_hash = SpatialHash(cell_size=300)  # Khởi tạo spatial hash

                        # ◆ Spawn enemies dựa trên difficulty config (thay vì hardcoded)
                        enemies, ai_interval, current_difficulty_config = spawn_level_enemies(current_level, player)
                        pygame.time.set_timer(AI_UPDATE_EVENT, ai_interval)
                            
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

                        # ◆ Play background music khi game bắt đầu
                        if background_music_loaded:
                            pygame.mixer.music.play(-1)  # -1 = loop vô hạn

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

                # Địch bắn trả (dựa trên difficulty config)
                if current_difficulty_config and current_difficulty_config.enable_enemy_shooting:
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

                # ◆ CẬP NHẬT SPATIAL HASH (Tối ưu collision detection)
                update_spatial_hash(spatial_hash, player, enemies, data_list, level)

                # Thu thập nhiên liệu (dùng spatial hash để tìm nearby data)
                nearby_data = spatial_hash.get_nearby(player.pixel_x, player.pixel_y, TILE_SIZE * 2)
                for data in nearby_data[:]:
                    if data in data_list:
                        dist = get_distance(player, data)
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

                # Va chạm người chơi với địch (dùng spatial hash)
                nearby_enemies = spatial_hash.get_nearby(player.pixel_x, player.pixel_y, TILE_SIZE * 3)
                for enemy in nearby_enemies[:]:
                    if enemy in enemies:
                        hitbox_radius = TILE_SIZE * 2 if enemy.is_boss else TILE_SIZE * 1.1
                        if get_distance(player, enemy) < hitbox_radius:
                            player.take_damage(50 if enemy.is_boss else 20)
                            if not enemy.is_boss:
                                enemies.remove(enemy)
                            else:
                                player.pixel_x -= math.cos(player.angle) * 30
                                player.pixel_y -= math.sin(player.angle) * 30

                            if player.hp <= 0:
                                game_state = "GAME_OVER"
                                play_sound(game_over_sound)

                # Va chạm với địa hình khổng lồ (dùng spatial hash)
                nearby_planets = spatial_hash.get_nearby(player.pixel_x, player.pixel_y, TILE_SIZE * 3)
                for planet in nearby_planets:
                    if planet in level.planets:
                        if get_distance(player, planet) < planet.radius * 0.8 + TILE_SIZE / 2:
                            player.take_damage(50)
                            player.pixel_x -= math.cos(player.angle) * 20
                            player.pixel_y -= math.sin(player.angle) * 20
                            if player.hp <= 0:
                                game_state = "GAME_OVER"
                                play_sound(game_over_sound)

                # Va chạm SAM/AAA (dùng spatial hash)
                nearby_stakes = spatial_hash.get_nearby(player.pixel_x, player.pixel_y, TILE_SIZE * 3)
                for stake in nearby_stakes:
                    if stake in level.stakes:
                        if get_distance(player, stake) < stake.radius + TILE_SIZE / 2:
                            player.take_damage(2)
                            if player.hp <= 0:
                                game_state = "GAME_OVER"
                                play_sound(game_over_sound)
                            
                # Check Win/Lose Condition (dựa trên difficulty config)
                if base.hp <= 0:
                    game_state = "GAME_OVER"
                    play_sound(game_over_sound)
                elif current_difficulty_config:
                    win_cond = current_difficulty_config.win_condition
                    # Kiểm tra điều kiện thắng
                    conditions_met = True

                    if win_cond.destroy_all_enemies and len(enemies) > 0:
                        conditions_met = False

                    if win_cond.base_health_threshold > 1 and base.hp < win_cond.base_health_threshold:
                        conditions_met = False

                    if win_cond.min_score > 0 and score < win_cond.min_score:
                        conditions_met = False

                    if conditions_met and len(enemies) == 0:
                        game_state = "WIN"
                        # Tính thưởng dựa trên difficulty multiplier
                        reward = int(current_level * 100 * current_difficulty_config.reward_multiplier)
                        global_profile.money += reward
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
