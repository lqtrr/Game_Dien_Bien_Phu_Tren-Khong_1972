"""
Quản lý cài đặt game - Lưu/Tải từ JSON file
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class GameSettings:
    """Cài đặt game"""
    music_volume: float = 0.4       # Volume nhạc nền (0.0 - 1.0)
    sfx_volume: float = 0.5         # Volume hiệu ứng âm thanh (0.0 - 1.0)
    difficulty: str = "medium"      # Độ khó: "easy", "medium", "hard"
    graphics_effects: bool = True   # Bật/tắt hiệu ứng đồ họa
    show_grid: bool = False         # Hiển thị lưới
    
    def to_dict(self):
        """Convert thành dict"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        """Tạo từ dict"""
        return GameSettings(**{k: v for k, v in data.items() if k in GameSettings.__dataclass_fields__})


class SettingsManager:
    """Quản lý lưu/tải cài đặt"""
    
    def __init__(self, settings_file="game_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> GameSettings:
        """Tải cài đặt từ file, nếu không có thì dùng default"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return GameSettings.from_dict(data)
            except Exception as e:
                print(f"⚠️  Lỗi tải cài đặt: {e}. Dùng cài đặt mặc định.")
                return GameSettings()
        return GameSettings()
    
    def save_settings(self) -> bool:
        """Lưu cài đặt vào file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"✅ Đã lưu cài đặt vào {self.settings_file}")
            return True
        except Exception as e:
            print(f"❌ Lỗi lưu cài đặt: {e}")
            return False
    
    def get_music_volume(self) -> float:
        """Lấy volume nhạc nền"""
        return self.settings.music_volume
    
    def set_music_volume(self, volume: float):
        """Đặt volume nhạc nền"""
        self.settings.music_volume = max(0.0, min(1.0, volume))
    
    def get_sfx_volume(self) -> float:
        """Lấy volume hiệu ứng âm thanh"""
        return self.settings.sfx_volume
    
    def set_sfx_volume(self, volume: float):
        """Đặt volume hiệu ứng âm thanh"""
        self.settings.sfx_volume = max(0.0, min(1.0, volume))
    
    def get_difficulty(self) -> str:
        """Lấy độ khó"""
        return self.settings.difficulty
    
    def set_difficulty(self, difficulty: str):
        """Đặt độ khó"""
        if difficulty in ["easy", "medium", "hard"]:
            self.settings.difficulty = difficulty
    
    def get_graphics_effects(self) -> bool:
        """Kiểm tra xem hiệu ứng đồ họa có bật không"""
        return self.settings.graphics_effects
    
    def set_graphics_effects(self, enabled: bool):
        """Bật/tắt hiệu ứng đồ họa"""
        self.settings.graphics_effects = enabled
    
    def get_show_grid(self) -> bool:
        """Kiểm tra xem hiển thị lưới"""
        return self.settings.show_grid
    
    def set_show_grid(self, show: bool):
        """Bật/tắt hiển thị lưới"""
        self.settings.show_grid = show


# Instance toàn cầu để dùng xuyên suốt game
settings_manager = SettingsManager()
