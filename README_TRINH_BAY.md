# Maze Pursuit – Dien Bien Phu Tren Khong 1972 (Linebacker II)

> Tài liệu dùng cho **thuyết trình**: mô tả bối cảnh, kiến trúc hệ thống, luồng gameplay và phần AI (DFS/BFS/A\*/Heuristic) kèm cơ chế tối ưu.

---

## 1) Giới thiệu nhanh trò chơi

- Game mô phỏng bối cảnh phòng không “**Điện Biên Phủ Trên Không 1972**”.
- Người chơi điều khiển **MiG-21** để:
  - Thu thập **nhiên liệu** (DataCollectible) để kiếm điểm/điểm tiền (money).
  - Tránh bị bắn/va chạm với **địch** và địa hình hiểm trở.
  - Bắn hạ địch và/hoặc hoàn thành điều kiện thắng theo từng level.
- Tài nguyên và sức mạnh của người chơi có thể nâng cấp ở màn **UPGRADE**.

---

## 2) Kiến trúc dự án (theo file chính)

### `main.py` – Trung tâm vòng lặp game

Chứa:

- Khởi tạo Pygame, nạp assets, init nhạc và âm thanh.
- **State màn chơi**: `MAIN_MENU` → `UPGRADE` → `PLAYING`.
- Vòng lặp game 60 FPS:
  - Xử lý sự kiện (phím, timer AI update).
  - Update game objects: player, bullets, level (spawn/culling), enemy AI.
  - Render theo camera (camera follow player).

Các điểm nổi bật trong `main.py`:

- Timer `AI_UPDATE_EVENT` để cập nhật đường bay của địch theo cấu hình difficulty.
- Vẽ nền topo map procedural (`draw_map_background`).
- Tối ưu collision nhờ **SpatialHash**: thay vì check O(n²).
- Có **minimap** để quan sát vị trí tương đối của: hành tinh/địa hình, stakes, enemy, collectibles, exit.
- Toggle “visualizer radar AI” bằng `SPACE` (hiển thị explored/path).

### `entities.py` – Các thực thể

Chứa các class chính:

- `Player` (MiG-21):
  - Di chuyển theo phím, quay hướng theo vector di chuyển.
  - Đạn laser (Bullet) bắn khi có cooldown và đủ ammo.
  - Nhận sát thương có giảm trừ theo `armor`.
- `Enemy` và các biến thể:
  - `DFSEnemy`, `BFSEnemy`, `AStarEnemy`, `HeuristicEnemy`.
  - `BossB52` (HP lớn, boss chậm hơn, bắn theo nhịp riêng).
- `CombatBase`:
  - HP của cứ điểm trung tâm. Địch tiến đến gần sẽ gây sát thương.
- `DataCollectible`:
  - Nhiên liệu vàng nhấp nháy, thu thập để tăng money/score.
- `Bullet`:
  - Đạn laser dạng tia (vẽ line), có `life` theo frame.
- `ItemDrop`:
  - Rơi health/ammo khi tiêu diệt địch.

Ngoài ra, `entities.py` có:

- `PlayerProfile` quản lý nâng cấp (HP/armor/ammo/fire-rate) và công thức quy đổi.
- `load_image` có cache (giảm cost rescale).

### `level.py` – Sinh bản đồ theo chunk + biomes

Chứa `Level`:

- Quản lý:
  - `planets`: khối “địa hình 2D” (dùng ảnh mountain.png).
  - `meteors`: địa hình hiểm trở/“mảnh núi di chuyển” (spawn + culling).
  - `stakes`: vị trí AAA/SAM (AAAPosition) + hiệu ứng pulse.
- Chunking:
  - `chunk_size = 1000`.
  - `generate_chunk(cx, cy)` sinh nội dung dựa vào biome theo `cx` (từ trái sang phải).
  - `update(player_x, player_y)` chỉ active các đối tượng trong khoảng cách nhất định.
- `exit_pos_pixel`: vị trí đích bay qua để mô tả/sinh hiệu ứng sân bay (airbase.png).

### `algorithms.py` – AI đường đi trên lưới cục bộ

Các thuật toán:

- `dfs_path(start, target, level)`
- `bfs_path(start, target, level)`
- `astar_path(start, target, level)`
- `heuristic_path(start, target, level)` (chọn theo h(n) – greedy heuristic)

Đặc điểm quan trọng để phù hợp game:

- Thao tác trên **grid cục bộ** bằng giới hạn `LOCAL_GRID_RADIUS` (giảm chi phí tính toán).
- `get_neighbors` là 4 hướng (lên/xuống/trái/phải) và kiểm tra `level.is_valid_pos`.
- Có “fallback an toàn” cắt giới hạn số bước/visited (tránh treo game).
- Trả về `path` và `explored` để có thể visual hóa.

### `difficulty.py` – Cấu hình độ khó & điều kiện thắng

- Enum `Difficulty` (EASY/NORMAL/HARD/INSANE).
- `DifficultyConfig` lưu:
  - số lượng địch theo từng thuật toán
  - tốc độ địch (multiplier)
  - HP người chơi (multiplier)
  - `ai_update_interval` (ms)
  - bật/tắt bắn của địch
  - có boss hay không
  - thưởng/reward multiplier
  - `WinCondition` (điều kiện thắng)

Luật thắng trong `main.py` dựa vào `WinCondition` và (thường) “tiêu diệt hết địch”.

### `collision.py` – Spatial Hash

- `SpatialHash` chia không gian thành grid cell theo `cell_size`.
- `insert/get_nearby/clear` giúp:
  - chỉ kiểm tra va chạm trong tập đối tượng lân cận.
- `get_distance` dùng để xác định tương tác theo bán kính.

---

## 3) Luồng gameplay (flow)

1. **MAIN_MENU**
   - Chọn level 1..4.
   - `ENTER`: bắt đầu game.
   - `U`: vào UPGRADE.
2. **UPGRADE**
   - Mua nâng cấp HP / armor / ammo / fire-rate bằng tiền (money).
   - `ESC`: quay lại MAIN_MENU.
3. **PLAYING**
   - Player di chuyển (phím mũi tên hoặc WASD tùy bạn tùy code).
   - Bắn laser: `Z` hoặc click chuột (tùy code).
   - AI update theo timer `AI_UPDATE_EVENT`:
     - Nếu địch gần player → target = vị trí player.
     - Nếu xa → target = (0,0) / base zone (tùy logic hiện có trong code).
   - Thu thập nhiên liệu → tăng money/score.
   - Nhặt item drop → tăng HP hoặc ammo.
   - Va chạm:
     - Đạn player → trừ HP địch.
     - Đạn địch → trừ HP player.
     - Địch tiến đến gần base → base giảm HP.
     - Va chạm player với địa hình/AAA/SAM theo bán kính.
   - Win/Lose:
     - Lose nếu base.hp <= 0 hoặc player.hp <= 0.
     - Win nếu thỏa `WinCondition` (thường là tiêu diệt hết địch + base HP ngưỡng + min_score).

---

## 4) Phần AI: DFS/BFS/A\*/Heuristic (thuyết trình)

### Ý tưởng

- Chuyển vị trí pixel của đối tượng sang grid (`r`, `c`).
- Mỗi thuật toán tìm đường từ ô hiện tại của enemy đến target.
- Enemy nhận đường `path` và di chuyển “smoothly” theo từng bước grid.
- Mỗi lần cập nhật AI (theo `ai_update_interval`), enemy sẽ gọi thuật toán tương ứng.

### Thuật toán được dùng ở đâu (file/hàm/lớp)

Các thuật toán đường đi được triển khai trong `algorithms.py` và được gắn vào enemy tương ứng trong `entities.py`:

- **DFS**
  - Triển khai: `dfs_path(start, target, level)` (`algorithms.py`)
  - Enemy: `DFSEnemy` (`entities.py`), constructor gán `algo_func = dfs_path`

- **BFS**
  - Triển khai: `bfs_path(start, target, level)` (`algorithms.py`)
  - Enemy: `BFSEnemy` (`entities.py`), constructor gán `algo_func = bfs_path`

- **A\***
  - Triển khai: `astar_path(start, target, level)` (`algorithms.py`)
  - Enemy: `AStarEnemy` (`entities.py`), constructor gán `algo_func = astar_path`

- **Heuristic (Greedy)**
  - Triển khai: `heuristic_path(start, target, level)` (`algorithms.py`)
  - Enemy: `HeuristicEnemy` (`entities.py`), constructor gán `algo_func = heuristic_path`

Logic “enemy gọi thuật toán để tạo đường đi” nằm ở `Enemy.update_path(...)` trong `entities.py`:

- `self.path, self.explored = self.algo_func((self.r, self.c), (target_r, target_c), level)`

Còn việc kích hoạt cập nhật đường đi theo thời gian là trong `main.py` (timer `AI_UPDATE_EVENT`):

- Nếu enemy cách player < 800 ⇒ `enemy.update_path(player.r, player.c, level)`
- Nếu xa ⇒ `enemy.update_path(0, 0, level)`

### 4 thuật toán

- **DFS** (Depth-First Search):
  - Duyệt theo ngăn xếp, có thể đi sâu nhanh nhưng không tối ưu quãng đường.
- **BFS** (Breadth-First Search):
  - Duyệt theo lớp → nếu không giới hạn có thể tìm đường ngắn theo số bước.
- **A\***:
  - Dùng `f = g + h` với `h` = Manhattan distance → cân bằng tối ưu và hiệu quả.
- **Heuristic (Greedy)**:
  - Ưu tiên node có h(n) nhỏ nhất → thường nhanh nhưng có thể kém tối ưu.

### Tối ưu để chạy realtime

- `LOCAL_GRID_RADIUS` chỉ giới hạn vùng tìm kiếm để giảm bùng nổ state.
- Có “cắt ngưỡng visited/explored length” để tránh treo.
- Visualizer lấy `explored` để render radar/đường đi.

---

## 5) Sinh bản đồ & tối ưu hiệu năng

### Chunking + culling

- Bản đồ không sinh toàn bộ một lần mà chỉ sinh theo các chunk xung quanh player.
- `update()` giữ active các đối tượng trong khoảng cách nhất định và loại bớt đối tượng xa.

### SpatialHash cho va chạm

- Collision giữa player và các đối tượng (enemy, planets, stakes, data) thay vì check toàn bộ.
- Giảm độ phức tạp và giúp game mượt khi có nhiều entity.

---

## 6) Hướng dẫn chạy (để đưa vào slide)

1. Cài Pygame.
2. Chạy file `main.py`.

Ví dụ (Windows):

```bash
python main.py
```

---

## 7) Gợi ý nội dung slide

- Slide 1: Game concept + mục tiêu.
- Slide 2: Kiến trúc file (main/level/entities/algorithms/difficulty/collision).
- Slide 3: Gameplay loop.
- Slide 4: AI 4 thuật toán + cách enemy di chuyển theo path.
- Slide 5: Tối ưu realtime (LOCAL_GRID_RADIUS + SpatialHash + chunking).
- Slide 6: Difficulty & win condition.

---

## Ghi chú

- Nếu bạn cần, có thể chỉnh thêm phần mô tả control/phím cho khớp với bản bạn đã dùng (trong code đang dùng `Z/click` để bắn, `SPACE` bật visualizer radar AI, và chọn level 1-4 ở menu).
