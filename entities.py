import pygame
import os
import math
import random
from settings import *
from algorithms import dfs_path, bfs_path, astar_path, heuristic_path

class CombatBase:
    """Cứ điểm chiến đấu trung tâm (Sân bay Gia Lâm)"""
    def __init__(self, x, y):
        self.pixel_x = x
        self.pixel_y = y
        self.max_hp = 5000
        self.hp = 5000
        self.radius = 150 # Kích thước va chạm
        self.img = load_image('airbase.png', (100, 255, 100), 300)
        
    def take_damage(self, amount):
        self.hp -= amount
        
    def draw(self, screen, cx=0, cy=0):
        screen_x = int(self.pixel_x - cx)
        screen_y = int(self.pixel_y - cy)
        
        # Chỉ vẽ nếu nằm trong màn hình
        if -300 <= screen_x <= WIDTH + 300 and -300 <= screen_y <= HEIGHT + 300:
            if self.img:
                rect = self.img.get_rect(center=(screen_x, screen_y))
                screen.blit(self.img, rect.topleft)
            else:
                pygame.draw.circle(screen, (100, 255, 100), (screen_x, screen_y), self.radius)
                
            # Thanh máu trên cứ điểm
            hp_ratio = max(0, self.hp / self.max_hp)
            bar_w = 200
            bar_h = 10
            bx = screen_x - bar_w // 2
            by = screen_y - self.radius - 20
            pygame.draw.rect(screen, (255, 0, 0), (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, int(bar_w * hp_ratio), bar_h))
            
            # Viền nhấp nháy báo động nếu máu thấp
            if hp_ratio < 0.3 and (pygame.time.get_ticks() // 200) % 2 == 0:
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), self.radius, 5)

class PlayerProfile:
    def __init__(self):
        self.money = 0
        self.upgrade_hp = 0        # Cấp độ nâng cấp máu
        self.upgrade_armor = 0     # Cấp độ nâng cấp độ bền (giảm sát thương)
        self.upgrade_ammo = 0      # Cấp độ nâng cấp đạn tối đa
        self.upgrade_fire_rate = 0 # Cấp độ nâng cấp tốc độ bắn

    def get_max_hp(self): return 100 + self.upgrade_hp * 50
    def get_armor(self): return self.upgrade_armor * 10
    def get_max_ammo(self): return 100 + self.upgrade_ammo * 50
    def get_fire_cooldown(self): return max(10, 25 - self.upgrade_fire_rate * 3) # Tính bằng số frame (1 frame = 1/60s)
    def get_damage(self): return 35 + self.upgrade_fire_rate * 5

global_profile = PlayerProfile()

# ◆ CACHE cho scaled images (tối ưu memory & performance)
_image_cache = {}

def load_image(filename, fallback_color, size):
    """Load image với caching — tránh rescale mỗi lần"""
    cache_key = (filename, size)

    # Nếu đã cached, return từ cache
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    path = os.path.join(os.path.dirname(__file__), 'assets', filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            scaled_img = pygame.transform.scale(img, (size, size))
            _image_cache[cache_key] = scaled_img  # Lưu vào cache
            return scaled_img
        except Exception as e:
            print(f"Lỗi load image {filename}: {e}")
            pass

    # Fallback: tạo surface màu
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill(fallback_color)
    _image_cache[cache_key] = surface
    return surface

class Entity:
    def __init__(self, x, y, image_name, fallback_color):
        self.pixel_x = x
        self.pixel_y = y
        self.fallback_color = fallback_color
        self.render_size = int(TILE_SIZE * 2.8)
        self.image = load_image(image_name, fallback_color, self.render_size)
        self.angle = 0
        self.speed = 0
        self.max_speed = 5.0

    @property
    def r(self):
        """Lấy tọa độ Lưới R hiện tại"""
        return int((self.pixel_y + TILE_SIZE / 2) // TILE_SIZE)

    @property
    def c(self):
        """Lấy tọa độ Lưới C hiện tại"""
        return int((self.pixel_x + TILE_SIZE / 2) // TILE_SIZE)

    def draw(self, screen, cx=0, cy=0):
        screen_x = self.pixel_x - cx
        screen_y = self.pixel_y - cy

        if -self.render_size <= screen_x <= WIDTH and -self.render_size <= screen_y <= HEIGHT:
            # Xoay máy bay theo hướng di chuyển
            img_to_draw = pygame.transform.rotate(self.image, -math.degrees(self.angle) - 90)
            img_rect = img_to_draw.get_rect(center=(screen_x + TILE_SIZE / 2, screen_y + TILE_SIZE / 2))
            screen.blit(img_to_draw, img_rect.topleft)

class Player(Entity):
    """MiG-21 Fishbed — tiêm kích chủ công phòng thủ Hà Nội"""
    def __init__(self, x, y):
        super().__init__(x, y, 'player_ship.png', PLAYER_COLOR)
        self.max_speed = 6.5
        
        self.max_hp = global_profile.get_max_hp()
        self.hp = self.max_hp
        self.armor = global_profile.get_armor()
        self.max_ammo = global_profile.get_max_ammo()
        self.ammo = self.max_ammo
        
        self.fire_cooldown = 0

    def take_damage(self, amount):
        # Trừ đi lượng giáp (armor), nhưng tối thiểu vẫn nhận 5 sát thương
        actual_damage = max(5, amount - self.armor)
        self.hp -= actual_damage
        if self.hp < 0: self.hp = 0

    def update_movement(self, keys):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
            
        dx, dy = 0, 0
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1

        if dx != 0 or dy != 0:
            self.angle = math.atan2(dy, dx)
            self.pixel_x += math.cos(self.angle) * self.max_speed
            self.pixel_y += math.sin(self.angle) * self.max_speed
            return True
        return False

class Enemy(Entity):
    def __init__(self, x, y, image_name, fallback_color, algo_func):
        super().__init__(x, y, image_name, fallback_color)
        self.algo_func = algo_func
        self.path = []
        self.explored = set()
        self.max_speed = 4.2  # Máy bay Mỹ nhanh nhưng bị địa hình cản
        self.hp = 100         # Máu của máy bay địch
        self.fire_cooldown = random.randint(60, 180) # Tránh bắn cùng lúc
        self.is_boss = False

        # ◆ Memory management
        self.max_path_length = 100  # Chỉ giữ 100 steps tiếp theo (giảm memory)
        self.explored_clear_counter = 0  # Counter để clear explored sets

    def take_damage(self, amount):
        self.hp -= amount

    def update_path(self, target_r, target_c, level):
        """Update path với memory management"""
        self.path, self.explored = self.algo_func((self.r, self.c), (target_r, target_c), level)

        # ◆ Limit path length - chỉ giữ first N steps (tối ưu memory)
        if len(self.path) > self.max_path_length:
            self.path = self.path[:self.max_path_length]

        # ◆ Clear explored set theo định kỳ để tránh memory leak
        self.explored_clear_counter += 1
        if self.explored_clear_counter > 10:  # Clear mỗi 10 lần update
            self.explored.clear()
            self.explored_clear_counter = 0

    def move_smoothly(self):
        if self.path:
            target_r, target_c = self.path[0]
            target_px = target_c * TILE_SIZE
            target_py = target_r * TILE_SIZE

            dx = target_px - self.pixel_x
            dy = target_py - self.pixel_y
            dist = math.hypot(dx, dy)

            if dist > self.max_speed:
                self.angle = math.atan2(dy, dx)
                self.pixel_x += math.cos(self.angle) * self.max_speed
                self.pixel_y += math.sin(self.angle) * self.max_speed
            else:
                self.pixel_x = target_px
                self.pixel_y = target_py
                self.path.pop(0)

class DFSEnemy(Enemy):
    """F-4 Phantom II — Con ma Mỹ (DFS: quét kiểu mò mẫm sâu)"""
    def __init__(self, x, y):
        super().__init__(x, y, 'dfs_ship.png', DFS_COLOR, dfs_path)

class BFSEnemy(Enemy):
    """F-105 Thunderchief — Thần Sấm (BFS: quét rộng đồng đều)"""
    def __init__(self, x, y):
        super().__init__(x, y, 'bfs_ship.png', BFS_COLOR, bfs_path)

class AStarEnemy(Enemy):
    """F-111 Aardvark — Con thú đào đất (A*: tìm đường tối ưu)"""
    def __init__(self, x, y):
        super().__init__(x, y, 'astar_ship.png', ASTAR_COLOR, astar_path)

class HeuristicEnemy(Enemy):
    """MiG-17 (lệ thuộc ước lượng heuristic — đồng đội lạc hướng)"""
    def __init__(self, x, y):
        super().__init__(x, y, 'heuristic_ship.png', HEURISTIC_COLOR, heuristic_path)

class BossB52(Enemy):
    """Siêu Pháo Đài Bay B-52 Stratofortress - Trùm Cuối"""
    def __init__(self, x, y):
        super().__init__(x, y, 'b52_boss.png', (255, 0, 0), astar_path)
        self.max_speed = 2.0 # Boss di chuyển chậm
        self.hp = 2000
        self.max_hp = 2000
        self.is_boss = True
        self.render_size = (int(TILE_SIZE * 3.5), int(TILE_SIZE * 3.5)) # Rất to

    def draw(self, screen, cx=0, cy=0):
        # Boss bự hơn, vẽ thanh máu bự trên đầu
        super().draw(screen, cx, cy)
        
        # Vẽ thanh máu Boss
        screen_x = int(self.pixel_x - cx)
        screen_y = int(self.pixel_y - cy)
        if -50 <= screen_x <= WIDTH + 50 and -50 <= screen_y <= HEIGHT + 50:
            hp_ratio = max(0, self.hp / self.max_hp)
            bar_w = 80
            bar_h = 8
            bx = screen_x - bar_w // 2
            by = screen_y - 45
            pygame.draw.rect(screen, (255, 0, 0), (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, int(bar_w * hp_ratio), bar_h))

class DataCollectible:
    """Nhiên liệu phản lực — thu thập để duy trì nhiệm vụ"""
    def __init__(self, x, y):
        self.pixel_x = x
        self.pixel_y = y
        self.radius = int(TILE_SIZE * 0.8)
        self._t = 0

    def draw(self, screen, cx=0, cy=0):
        self._t += 1
        center_x = self.pixel_x + TILE_SIZE // 2 - cx
        center_y = self.pixel_y + TILE_SIZE // 2 - cy

        if -self.radius * 2 <= center_x <= WIDTH and -self.radius * 2 <= center_y <= HEIGHT:
            # Hiệu ứng glow vàng nhấp nháy
            glow = abs(math.sin(self._t * 0.08))
            glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (255, 210, 0, int(80 * glow)),
                (self.radius * 2, self.radius * 2),
                self.radius * 2
            )
            screen.blit(glow_surf, (int(center_x) - self.radius * 2, int(center_y) - self.radius * 2))
            # Hình tròn nhiên liệu
            pygame.draw.circle(screen, DATA_COLOR, (int(center_x), int(center_y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 180), (int(center_x), int(center_y)), self.radius, 2)

class Bullet:
    """Viên đạn bắn ra từ máy bay"""
    def __init__(self, x, y, angle, speed, damage, is_player=True):
        self.pixel_x = x
        self.pixel_y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.is_player = is_player
        self.radius = 4
        self.life = 120 # Sống trong tối đa 120 frames (2 giây)

    def update(self):
        self.pixel_x += math.cos(self.angle) * self.speed
        self.pixel_y += math.sin(self.angle) * self.speed
        self.life -= 1

    def draw(self, screen, cx=0, cy=0):
        screen_x = int(self.pixel_x - cx)
        screen_y = int(self.pixel_y - cy)
        
        # Chiều dài của tia laze
        laser_length = 40
        tail_x = int(screen_x - math.cos(self.angle) * laser_length)
        tail_y = int(screen_y - math.sin(self.angle) * laser_length)
        
        if -50 <= screen_x <= WIDTH + 50 and -50 <= screen_y <= HEIGHT + 50:
            color = (255, 255, 100) if self.is_player else (255, 50, 50)
            core_color = (255, 255, 255)
            
            # Vẽ viền laze (phát sáng mờ)
            pygame.draw.line(screen, color, (screen_x, screen_y), (tail_x, tail_y), 6)
            # Vẽ lõi laze (trắng sáng)
            pygame.draw.line(screen, core_color, (screen_x, screen_y), (tail_x, tail_y), 2)

class ItemDrop:
    """Vật phẩm rơi ra (Máu, Đạn) khi tiêu diệt địch"""
    def __init__(self, x, y, item_type):
        self.pixel_x = x
        self.pixel_y = y
        self.item_type = item_type # 'health' or 'ammo'
        self.radius = 12
        self.life = 600 # Tồn tại 10 giây
        
    def draw(self, screen, cx=0, cy=0):
        self.life -= 1
        screen_x = int(self.pixel_x - cx)
        screen_y = int(self.pixel_y - cy)
        
        if -self.radius <= screen_x <= WIDTH + self.radius and -self.radius <= screen_y <= HEIGHT + self.radius:
            # Nhấp nháy khi sắp biến mất
            if self.life < 120 and self.life % 10 < 5:
                return
                
            color = (50, 255, 50) if self.item_type == 'health' else (100, 150, 255)
            pygame.draw.rect(screen, color, (screen_x - self.radius, screen_y - self.radius, self.radius*2, self.radius*2))
            pygame.draw.rect(screen, (255, 255, 255), (screen_x - self.radius, screen_y - self.radius, self.radius*2, self.radius*2), 2)
            
            # Kí hiệu trên hộp
            font = pygame.font.SysFont('tahoma', 14, bold=True)
            text = "+" if self.item_type == 'health' else "="
            lbl = font.render(text, True, (255, 255, 255))
            screen.blit(lbl, (screen_x - lbl.get_width()//2, screen_y - lbl.get_height()//2))
