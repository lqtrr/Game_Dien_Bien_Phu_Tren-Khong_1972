"""
Hệ thống Difficulty Progression
Quản lý cấu hình khó độ một cách có cấu trúc
"""
from enum import Enum, auto
from dataclasses import dataclass


class Difficulty(Enum):
    """Các mức khó độ"""
    EASY = auto()          # Mức 1: Tân Binh
    NORMAL = auto()        # Mức 2: Không Chiến
    HARD = auto()          # Mức 3: Bão Lửa
    INSANE = auto()        # Mức 4: Boss B-52


@dataclass
class WinCondition:
    """Định nghĩa điều kiện thắng/thua"""
    destroy_all_enemies: bool = True    # Phải tiêu diệt hết kẻ địch
    base_health_threshold: int = 1      # Base phải có health >= này mới thắng (0 = không check)
    min_score: int = 0                  # Score tối thiểu để thắng
    time_limit: int = 0                 # Giới hạn thời gian (0 = vô hạn, tính bằng giây)

    def __str__(self):
        reqs = []
        if self.destroy_all_enemies:
            reqs.append("Tiêu diệt hết kẻ địch")
        if self.base_health_threshold > 1:
            reqs.append(f"Cứ điểm có HP ≥ {self.base_health_threshold}")
        if self.min_score > 0:
            reqs.append(f"Điểm ≥ {self.min_score}")
        return " + ".join(reqs) if reqs else "Chiến thắng!"


@dataclass
class DifficultyConfig:
    """Cấu hình mỗi mức khó độ"""
    level: int
    name: str
    dfs_count: int
    bfs_count: int
    astar_count: int
    heuristic_count: int
    ai_update_interval: int  # milliseconds (càng thấp, càng nhanh)
    enemy_speed_multiplier: float  # 1.0 = speed bình thường
    player_hp_multiplier: float  # Nhân với max HP để adjust độ khó
    enable_enemy_shooting: bool  # Địch có bắn hay không
    boss_enabled: bool  # Có boss hay không
    reward_multiplier: float  # Nhân với phần thưởng
    win_condition: WinCondition = None  # Điều kiện thắng

    def __post_init__(self):
        """Set default win condition nếu chưa set"""
        if self.win_condition is None:
            self.win_condition = WinCondition(destroy_all_enemies=True)

    def __str__(self):
        return f"[Level {self.level}] {self.name} - {self.dfs_count*4} enemies"


class DifficultyManager:
    """Quản lý hệ thống khó độ"""

    def __init__(self):
        # Cấu hình chi tiết cho mỗi mức khó độ
        self.configs = {
            Difficulty.EASY: DifficultyConfig(
                level=1,
                name="Tân Binh (Dễ)",
                dfs_count=2, bfs_count=2, astar_count=2, heuristic_count=2,
                ai_update_interval=500,
                enemy_speed_multiplier=0.7,
                player_hp_multiplier=1.5,
                enable_enemy_shooting=False,
                boss_enabled=False,
                reward_multiplier=1.0,
                win_condition=WinCondition(destroy_all_enemies=True, base_health_threshold=500),
            ),

            Difficulty.NORMAL: DifficultyConfig(
                level=2,
                name="Không Chiến (Vừa)",
                dfs_count=4, bfs_count=4, astar_count=4, heuristic_count=4,
                ai_update_interval=200,
                enemy_speed_multiplier=1.0,
                player_hp_multiplier=1.0,
                enable_enemy_shooting=False,
                boss_enabled=False,
                reward_multiplier=1.5,
                win_condition=WinCondition(destroy_all_enemies=True, base_health_threshold=2000),
            ),

            Difficulty.HARD: DifficultyConfig(
                level=3,
                name="Bão Lửa (Khó)",
                dfs_count=4, bfs_count=4, astar_count=4, heuristic_count=4,
                ai_update_interval=300,
                enemy_speed_multiplier=1.2,
                player_hp_multiplier=0.8,
                enable_enemy_shooting=True,
                boss_enabled=False,
                reward_multiplier=2.0,
                win_condition=WinCondition(destroy_all_enemies=True, base_health_threshold=2500),
            ),

            Difficulty.INSANE: DifficultyConfig(
                level=4,
                name="Boss B-52 (Cực Khó)",
                dfs_count=0, bfs_count=0, astar_count=0, heuristic_count=0,
                ai_update_interval=300,
                enemy_speed_multiplier=1.5,
                player_hp_multiplier=0.6,
                enable_enemy_shooting=True,
                boss_enabled=True,
                reward_multiplier=3.0,
                win_condition=WinCondition(destroy_all_enemies=True, base_health_threshold=3000),
            ),
        }

    def get_config(self, difficulty):
        """Lấy cấu hình cho mức khó độ"""
        if isinstance(difficulty, int):
            # Convert from level number (1-4) to Difficulty enum
            diff_map = {1: Difficulty.EASY, 2: Difficulty.NORMAL, 3: Difficulty.HARD, 4: Difficulty.INSANE}
            difficulty = diff_map.get(difficulty, Difficulty.EASY)

        return self.configs.get(difficulty, self.configs[Difficulty.EASY])

    def get_difficulty_name(self, difficulty):
        """Lấy tên mức khó độ"""
        config = self.get_config(difficulty)
        return config.name

    def get_total_enemies(self, difficulty):
        """Lấy tổng số kẻ địch cho mức khó độ"""
        config = self.get_config(difficulty)
        total = config.dfs_count + config.bfs_count + config.astar_count + config.heuristic_count
        return total


# Global difficulty manager instance
difficulty_manager = DifficultyManager()
