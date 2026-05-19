import pygame
import os
import random
import math
from settings import *

def load_transparent_image(filename, size=None):
    path = os.path.join(os.path.dirname(__file__), 'assets', filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                return pygame.transform.scale(img, (size, size))
            return img
        except:
            pass
    return None

class MountainObstacle:
    """Núi / địa hình hiểm trở — tương đương Thiên thạch cũ"""
    def __init__(self, x, y, vx, vy, img, radius):
        self.pixel_x = x
        self.pixel_y = y
        self.vx = vx
        self.vy = vy
        self.img = img
        self.radius = radius

class TerrainBlock:
    """Khối địa hình bờ + đồi núi hai bên hành lang bay — tương đương Hành tinh cũ"""
    def __init__(self, x, y, img, radius):
        self.pixel_x = x
        self.pixel_y = y
        self.img = img
        self.radius = radius

class AAAPosition:
    """Trận địa pháo cao xạ / tên lửa SAM — tương đương Cọc Lượng Tử cũ"""
    def __init__(self, x, y):
        self.pixel_x = x
        self.pixel_y = y
        self.radius = TILE_SIZE * 2.0
        self.pulse_offset = random.uniform(0, math.pi * 2)

class Level:
    def __init__(self):
        self.meteors = []    # Dùng lại tên biến để không đổi code AI (thực ra là núi/mảnh đạn)
        self.planets = []    # Khối địa hình bờ (dùng lại tên)
        self.stakes = []     # Trận địa AAA/SAM (dùng lại tên)
        self.occupied_cells = set()
        self.loaded_chunks = set()

        self.chunk_size = 1000

        self.spawn_radius = max(WIDTH, HEIGHT) + 500
        # Đích: Sân bay Gia Lâm / căn cứ an toàn ở cuối hành lang
        self.exit_pos_pixel = (0, 8000)

        # Tải ảnh địa hình
        self.mountain_base_img = load_transparent_image('mountain.png')
        self.terrain_block_img = load_transparent_image('mountain.png')
        self.airbase_img = load_transparent_image('airbase.png', int(TILE_SIZE * 3.5))
        self.sam_img = load_transparent_image('sam_site.png')

    def get_scaled_img(self, base_img, radius):
        if base_img:
            return pygame.transform.scale(base_img, (int(radius * 2), int(radius * 2)))
        return None

    def init_level(self, player_x, player_y):
        self.meteors.clear()
        self.planets.clear()
        self.stakes.clear()
        self.loaded_chunks.clear()

    def generate_chunk(self, cx, cy):
        """Sinh ra địa hình theo khu vực địa lý (Biome) dựa vào tọa độ X (Đông/Tây)"""
        base_x = cx * self.chunk_size
        base_y = cy * self.chunk_size

        # BIOMES CỦA VIỆT NAM THỜI CHIẾN
        # 1. PHÍA TÂY (cx < 0): Dãy Trường Sơn / Tây Bắc -> Nhiều núi, ít SAM
        if cx < 0:
            # Sinh 3-5 khối núi khổng lồ, đảm bảo không díu vào nhau
            for _ in range(random.randint(3, 5)):
                for _attempt in range(15):  # Thử tối đa 15 lần để tìm chỗ trống
                    pradius = random.uniform(500, 1000)
                    x = random.uniform(base_x, base_x + self.chunk_size)
                    y = random.uniform(base_y, base_y + self.chunk_size)
                    
                    # Khu vực an toàn (Safe Zone) quanh điểm hồi sinh (0, 0)
                    if math.hypot(x, y) < 1500:
                        continue
                        
                    # Kiểm tra khoảng cách với các núi đã có
                    overlap = False
                    for p in self.planets:
                        if math.hypot(p.pixel_x - x, p.pixel_y - y) < (p.radius + pradius) * 0.75:
                            overlap = True
                            break
                            
                    if not overlap:
                        pimg = self.get_scaled_img(self.terrain_block_img, pradius)
                        self.planets.append(TerrainBlock(x, y, pimg, pradius))
                        break
            # Sinh 0-1 SAM (Giảm bớt SAM)
            for _ in range(random.randint(0, 1)):
                x = random.uniform(base_x + 100, base_x + self.chunk_size - 100)
                y = random.uniform(base_y + 100, base_y + self.chunk_size - 100)
                if math.hypot(x, y) < 1500:
                    continue
                self.stakes.append(AAAPosition(x, y))

        # 2. TRUNG TÂM (0 <= cx <= 2): Đồng Bằng Bắc Bộ -> Không núi to, mật độ SAM vừa phải
        elif 0 <= cx <= 2:
            # Sinh 2-5 SAM (Giảm bớt)
            for _ in range(random.randint(2, 5)):
                x = random.uniform(base_x + 50, base_x + self.chunk_size - 50)
                y = random.uniform(base_y + 50, base_y + self.chunk_size - 50)
                if math.hypot(x, y) < 1500:
                    continue
                self.stakes.append(AAAPosition(x, y))

        # 3. PHÍA ĐÔNG (cx > 2): Vịnh Bắc Bộ (Biển) -> Trống trải, không có gì
        else:
            # Có thể thêm tàu chiến Mỹ ở đây sau này, tạm thời để trống
            pass

    def spawn_mountain(self, px, py):
        """Mảnh núi / địa hình hiểm trở trôi dọc theo hành lang bay"""
        angle = random.uniform(0, math.pi)
        dist = random.uniform(800, self.spawn_radius)
        mx = px + math.cos(angle) * dist
        my = py + math.sin(angle) * dist

        # Bắt buộc nằm trong khu vực đất liền (Trường Sơn hoặc Đồng Bằng, cx <= 2)
        # Giới hạn mây núi không trôi ra biển
        mx = min(2800, mx)

        speed = random.uniform(METEOR_SPEED_MIN, METEOR_SPEED_MAX)
        vx = random.uniform(-0.5, 0.5)
        vy = speed

        mradius = random.uniform(TILE_SIZE / 2, TILE_SIZE * 1.5)
        mimg = self.get_scaled_img(self.mountain_base_img, mradius)
        self.meteors.append(MountainObstacle(mx, my, vx, vy, mimg, mradius))

    def _mark_occupied(self, pixel_x, pixel_y, radius):
        min_c = int((pixel_x - radius) // TILE_SIZE)
        max_c = int((pixel_x + radius) // TILE_SIZE)
        min_r = int((pixel_y - radius) // TILE_SIZE)
        max_r = int((pixel_y + radius) // TILE_SIZE)
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                self.occupied_cells.add((r, c))

    def update(self, player_x, player_y):
        # 1. Hệ thống Chunk (Sinh địa hình vô tận 2D lưới 5x5)
        current_cx = int(player_x // self.chunk_size)
        current_cy = int(player_y // self.chunk_size)
        for cx in range(current_cx - 2, current_cx + 3):
            for cy in range(current_cy - 2, current_cy + 3):
                if (cx, cy) not in self.loaded_chunks:
                    self.loaded_chunks.add((cx, cy))
                    self.generate_chunk(cx, cy)

        active_meteors = []
        active_planets = []
        active_stakes = []
        self.occupied_cells.clear()

        # 2. Cập nhật và thu dọn trận địa AAA/SAM (culling 2D)
        for s in self.stakes:
            if math.hypot(s.pixel_x - player_x, s.pixel_y - player_y) < 3500:
                active_stakes.append(s)
                self._mark_occupied(s.pixel_x, s.pixel_y, s.radius * 0.8)
        self.stakes = active_stakes

        # 3. Cập nhật khối địa hình bờ núi (culling 2D)
        for p in self.planets:
            if math.hypot(p.pixel_x - player_x, p.pixel_y - player_y) < 4500:
                active_planets.append(p)
                self._mark_occupied(p.pixel_x, p.pixel_y, p.radius * 0.8)
        self.planets = active_planets

        # 4. Cập nhật địa hình hiểm trở trôi (núi nhỏ / mảnh đạn)
        for m in self.meteors:
            m.pixel_x += m.vx
            m.pixel_y += m.vy
            dist = math.hypot(m.pixel_x - player_x, m.pixel_y - player_y)
            if dist < self.spawn_radius * 1.5:
                active_meteors.append(m)
                self._mark_occupied(m.pixel_x, m.pixel_y, m.radius * 0.8)
        self.meteors = active_meteors

        # Duy trì khoảng 30 chướng ngại vật địa hình
        while len(self.meteors) < 30:
            self.spawn_mountain(player_x, player_y)

    def is_obstacle(self, r, c):
        return (r, c) in self.occupied_cells

    def is_valid_pos(self, r, c):
        return not self.is_obstacle(r, c)

    def draw(self, screen, camera_x, camera_y):
        # (Đã loại bỏ màn sương mù vách núi vì bản đồ nay là vô tận)

        # 2. Vẽ khối địa hình bờ / vách núi
        for p in self.planets:
            x = p.pixel_x - camera_x
            y = p.pixel_y - camera_y
            if -p.radius * 2 <= x <= WIDTH + p.radius * 2 and -p.radius * 2 <= y <= HEIGHT + p.radius * 2:
                if p.img:
                    rect = p.img.get_rect(center=(int(x), int(y)))
                    screen.blit(p.img, rect.topleft)
                else:
                    pygame.draw.circle(screen, (40, 80, 30), (int(x), int(y)), int(p.radius))

        # 3. Vẽ địa hình hiểm trở / mảnh núi nhỏ trôi
        for m in self.meteors:
            x = m.pixel_x - camera_x
            y = m.pixel_y - camera_y
            if -m.radius * 2 <= x <= WIDTH + m.radius * 2 and -m.radius * 2 <= y <= HEIGHT + m.radius * 2:
                if m.img:
                    rect = m.img.get_rect(center=(int(x), int(y)))
                    screen.blit(m.img, rect.topleft)
                else:
                    pygame.draw.circle(screen, WALL_COLOR, (int(x), int(y)), int(m.radius))

        # 4. Vẽ Trận địa AAA / SAM (nhấp nháy đỏ cam như đạn pháo)
        t = pygame.time.get_ticks()
        for s in self.stakes:
            x = int(s.pixel_x - camera_x)
            y = int(s.pixel_y - camera_y)
            if -s.radius <= x <= WIDTH + s.radius and -s.radius <= y <= HEIGHT + s.radius:
                glow = abs(math.sin(t * 0.006 + s.pulse_offset))
                if self.sam_img:
                    sam_scaled = pygame.transform.scale(
                        self.sam_img, (int(s.radius * 2.2), int(s.radius * 2.2))
                    )
                    sam_rect = sam_scaled.get_rect(center=(x, y))
                    screen.blit(sam_scaled, sam_rect.topleft)
                    # Vòng sáng cảnh báo
                    warn_color = (int(255 * glow), int(80 * glow), 0, 120)
                    warn_surf = pygame.Surface((int(s.radius * 2.5), int(s.radius * 2.5)), pygame.SRCALPHA)
                    pygame.draw.circle(
                        warn_surf,
                        (int(255 * glow), int(80 * glow), 0, int(100 * glow)),
                        (int(s.radius * 1.25), int(s.radius * 1.25)),
                        int(s.radius * 1.25)
                    )
                    screen.blit(warn_surf, (x - int(s.radius * 1.25), y - int(s.radius * 1.25)))
                else:
                    # Fallback: tam giác cảnh báo đỏ-cam
                    core_color = (255, int(100 * glow), 0)
                    pygame.draw.polygon(screen, core_color, [
                        (x, y - s.radius),
                        (x - s.radius / 2, y + s.radius),
                        (x + s.radius / 2, y + s.radius)
                    ])
                    pygame.draw.polygon(screen, (255, 150, 0), [
                        (x, y - s.radius),
                        (x - s.radius / 2, y + s.radius),
                        (x + s.radius / 2, y + s.radius)
                    ], 2)

        # 5. Vẽ Sân bay Gia Lâm / Căn cứ an toàn (Đích)
        ex = self.exit_pos_pixel[0] - camera_x
        ey = self.exit_pos_pixel[1] - camera_y
        if -TILE_SIZE * 4 <= ex <= WIDTH and -TILE_SIZE * 4 <= ey <= HEIGHT:
            if self.airbase_img:
                angle = (t * 0.02) % 360
                rotated_ab = pygame.transform.rotate(self.airbase_img, angle)
                ab_rect = rotated_ab.get_rect(center=(int(ex), int(ey)))
                screen.blit(rotated_ab, ab_rect.topleft)
                # Vầng sáng vàng đỏ (đèn hiệu sân bay)
                glow2 = abs(math.sin(t * 0.003))
                beacon_surf = pygame.Surface((TILE_SIZE * 8, TILE_SIZE * 8), pygame.SRCALPHA)
                pygame.draw.circle(
                    beacon_surf,
                    (220, 50, 50, int(60 * glow2)),
                    (TILE_SIZE * 4, TILE_SIZE * 4),
                    TILE_SIZE * 4
                )
                screen.blit(beacon_surf, (int(ex) - TILE_SIZE * 4, int(ey) - TILE_SIZE * 4))
            else:
                pygame.draw.circle(screen, EXIT_COLOR, (int(ex), int(ey)), int(TILE_SIZE * 1.5))
                pygame.draw.circle(screen, (255, 255, 255), (int(ex), int(ey)), int(TILE_SIZE * 1.5), 2)
