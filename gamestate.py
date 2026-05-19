"""
Formal State Machine cho Game States
Giải quyết string magic states và cung cấp type-safe state management
"""
from enum import Enum, auto


class AppState(Enum):
    """Trạng thái toàn ứng dụng"""
    MAIN_MENU = auto()      # Sảnh chờ chính
    UPGRADE = auto()         # Xưởng nâng cấp
    SETTINGS = auto()        # Menu cài đặt
    PLAYING = auto()         # Đang chơi game


class GameState(Enum):
    """Trạng thái trong lúc chơi game"""
    PLAYING = auto()      # Game đang chạy
    PAUSED = auto()       # Game bị tạm dừng (future)
    GAME_OVER = auto()    # Thua cuộc
    WIN = auto()          # Thắng cuộc


class StateManager:
    """Quản lý trạng thái an toàn"""

    def __init__(self, initial_app_state=AppState.MAIN_MENU, initial_game_state=GameState.PLAYING):
        self.app_state = initial_app_state
        self.game_state = initial_game_state
        self.state_changed = False  # Flag để track khi state thay đổi
        self.prev_app_state = None
        self.prev_game_state = None

    def set_app_state(self, new_state):
        """Đặt app state mới"""
        if not isinstance(new_state, AppState):
            raise ValueError(f"Invalid app state: {new_state}")

        if new_state != self.app_state:
            self.prev_app_state = self.app_state
            self.app_state = new_state
            self.state_changed = True

    def set_game_state(self, new_state):
        """Đặt game state mới"""
        if not isinstance(new_state, GameState):
            raise ValueError(f"Invalid game state: {new_state}")

        if new_state != self.game_state:
            self.prev_game_state = self.game_state
            self.game_state = new_state
            self.state_changed = True

    def is_app_state(self, state):
        """Check nếu app state là state đã cho"""
        return self.app_state == state

    def is_game_state(self, state):
        """Check nếu game state là state đã cho"""
        return self.game_state == state

    def clear_state_changed_flag(self):
        """Clear state changed flag sau khi xử lý"""
        self.state_changed = False

    def __str__(self):
        return f"AppState: {self.app_state.name}, GameState: {self.game_state.name}"


# Hàm helper để convert từ old string-based states sang new enum
def string_to_app_state(state_str):
    """Convert string state sang AppState enum (compatibility)"""
    mapping = {
        "MAIN_MENU": AppState.MAIN_MENU,
        "UPGRADE": AppState.UPGRADE,
        "SETTINGS": AppState.SETTINGS,
        "PLAYING": AppState.PLAYING,
    }
    return mapping.get(state_str, AppState.MAIN_MENU)


def string_to_game_state(state_str):
    """Convert string state sang GameState enum (compatibility)"""
    mapping = {
        "PLAYING": GameState.PLAYING,
        "GAME_OVER": GameState.GAME_OVER,
        "WIN": GameState.WIN,
    }
    return mapping.get(state_str, GameState.PLAYING)
