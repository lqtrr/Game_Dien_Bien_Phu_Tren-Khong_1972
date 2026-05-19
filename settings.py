# settings.py - Điện Biên Phủ Trên Không (Linebacker II 1972)

# Kích thước cửa sổ
WIDTH = 1280
HEIGHT = 720
TILE_SIZE = 30

# Lưới (Grid) của toàn bộ bản đồ
COLS = 60
ROWS = 30

FPS = 60

# Cấu hình địa hình và chướng ngại vật
METEOR_COUNT = 80         # Số lượng chướng ngại vật (núi/SAM) xung quanh người chơi
METEOR_SPEED_MIN = 0.5    # Tốc độ trôi (gần như tĩnh — núi không bay!)
METEOR_SPEED_MAX = 1.2
LOCAL_GRID_RADIUS = 15    # AI sẽ chụp lại lưới 30x30 xung quanh nó để tìm đường

# Bảng Màu (R, G, B) - Phong cách chiến trường Điện Biên Phủ
BG_COLOR = (20, 35, 15)            # Nền (rừng núi tối)
WALL_COLOR = (60, 80, 40)          # Núi/SAM (chướng ngại vật)
GRID_COLOR = (25, 40, 20)          # Màu viền lưới
DATA_COLOR = (255, 210, 0)         # Nhiên liệu (màu vàng)
EXIT_COLOR = (220, 50, 50)         # Sân bay Gia Lâm (đích đến)

# Màu của nhân vật và AI (dùng làm block màu vẽ tạm nếu chưa có hình)
PLAYER_COLOR = (180, 30, 30)       # MiG-21 - Đỏ sao vàng Việt Nam
DFS_COLOR = (80, 140, 200)         # F-4 Phantom II - Xanh USAF
BFS_COLOR = (200, 180, 80)         # F-105 Thunderchief - Vàng camo
ASTAR_COLOR = (200, 100, 60)       # F-111 Aardvark - Cam tối
HEURISTIC_COLOR = (100, 60, 160)   # MiG-17 (heuristic) - Tím

# Màu Visualize (Phím Space)
VIS_DFS_COLOR = (30, 60, 100)
VIS_BFS_COLOR = (80, 70, 30)
VIS_ASTAR_COLOR = (100, 50, 20)
VIS_HEURISTIC_COLOR = (50, 30, 80)
