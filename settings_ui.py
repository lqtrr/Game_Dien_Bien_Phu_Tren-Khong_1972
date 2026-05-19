"""
Giao diện cài đặt game - Settings Menu UI
"""
import pygame
from game_settings import settings_manager


def draw_settings_menu(screen, font, large_font, small_font, WIDTH, HEIGHT, lobby_bg):
    """Vẽ menu cài đặt"""
    
    # Vẽ nền
    if lobby_bg:
        screen.blit(lobby_bg, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((10, 20, 10))
    
    # Tiêu đề
    title = large_font.render("CÀI ĐẶT TRÒ CHƠI", True, (255, 200, 100))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    # Các tuỳ chỉnh
    y_offset = 150
    line_height = 70
    
    settings = settings_manager.settings
    
    # ── 1. Âm thanh nhạc nền ──
    music_vol_percent = int(settings.music_volume * 100)
    music_txt = font.render(
        f"[1] Âm thanh Nhạc nền: {music_vol_percent}%",
        True,
        (255, 255, 100)
    )
    screen.blit(music_txt, (WIDTH // 2 - 300, y_offset))
    # Vẽ thanh tiến độ
    bar_width = 200
    pygame.draw.rect(screen, (60, 60, 60), (WIDTH // 2 + 50, y_offset + 5, bar_width, 20))
    pygame.draw.rect(screen, (100, 200, 100), (WIDTH // 2 + 50, y_offset + 5, int(bar_width * settings.music_volume), 20))
    
    hint1 = small_font.render("← → để điều chỉnh", True, (150, 150, 150))
    screen.blit(hint1, (WIDTH // 2 + 50 + bar_width + 20, y_offset + 5))
    
    y_offset += line_height
    
    # ── 2. Âm thanh hiệu ứng ──
    sfx_vol_percent = int(settings.sfx_volume * 100)
    sfx_txt = font.render(
        f"[2] Âm thanh Hiệu ứng: {sfx_vol_percent}%",
        True,
        (255, 255, 100)
    )
    screen.blit(sfx_txt, (WIDTH // 2 - 300, y_offset))
    # Vẽ thanh tiến độ
    pygame.draw.rect(screen, (60, 60, 60), (WIDTH // 2 + 50, y_offset + 5, bar_width, 20))
    pygame.draw.rect(screen, (100, 150, 255), (WIDTH // 2 + 50, y_offset + 5, int(bar_width * settings.sfx_volume), 20))
    
    hint2 = small_font.render("← → để điều chỉnh", True, (150, 150, 150))
    screen.blit(hint2, (WIDTH // 2 + 50 + bar_width + 20, y_offset + 5))
    
    y_offset += line_height
    
    # ── 3. Độ khó ──
    difficulty_colors = {
        "easy": (100, 255, 100),
        "medium": (255, 255, 100),
        "hard": (255, 100, 100)
    }
    difficulty_names = {
        "easy": "Dễ",
        "medium": "Vừa",
        "hard": "Khó"
    }
    
    diff_color = difficulty_colors[settings.difficulty]
    diff_name = difficulty_names[settings.difficulty]
    diff_txt = font.render(
        f"[3] Độ khó: {diff_name}",
        True,
        diff_color
    )
    screen.blit(diff_txt, (WIDTH // 2 - 300, y_offset))
    hint3 = small_font.render("← → để chọn", True, (150, 150, 150))
    screen.blit(hint3, (WIDTH // 2 + 200, y_offset + 5))
    
    y_offset += line_height
    
    # ── 4. Hiệu ứng đồ họa ──
    graphics_status = "BẬT" if settings.graphics_effects else "TẮT"
    graphics_color = (100, 255, 100) if settings.graphics_effects else (255, 100, 100)
    graphics_txt = font.render(
        f"[4] Hiệu ứng Đồ họa: {graphics_status}",
        True,
        graphics_color
    )
    screen.blit(graphics_txt, (WIDTH // 2 - 300, y_offset))
    hint4 = small_font.render("Nhấn SPACE để bật/tắt", True, (150, 150, 150))
    screen.blit(hint4, (WIDTH // 2 + 200, y_offset + 5))
    
    y_offset += line_height
    
    # ── 5. Hiển thị lưới ──
    grid_status = "BẬT" if settings.show_grid else "TẮT"
    grid_color = (100, 255, 100) if settings.show_grid else (255, 100, 100)
    grid_txt = font.render(
        f"[5] Hiển thị Lưới: {grid_status}",
        True,
        grid_color
    )
    screen.blit(grid_txt, (WIDTH // 2 - 300, y_offset))
    hint5 = small_font.render("Nhấn SPACE để bật/tắt", True, (150, 150, 150))
    screen.blit(hint5, (WIDTH // 2 + 200, y_offset + 5))
    
    # Thoát
    esc_txt = font.render("Nhấn [ESC] để Lưu & Quay lại", True, (150, 220, 150))
    screen.blit(esc_txt, (WIDTH // 2 - esc_txt.get_width() // 2, HEIGHT - 80))
    
    # Thông báo lưu
    save_txt = small_font.render("(Cài đặt sẽ được lưu tự động)", True, (100, 200, 100))
    screen.blit(save_txt, (WIDTH // 2 - save_txt.get_width() // 2, HEIGHT - 35))


def handle_settings_input(event, current_menu_item=None):
    """Xử lý input từ menu cài đặt
    
    Trả về: (action, new_menu_item)
    action: "continue" để giữ nguyên, "save_and_exit" để lưu & thoát
    """
    
    if event.type == pygame.KEYDOWN:
        # Nhấn ESC để lưu và thoát
        if event.key == pygame.K_ESCAPE:
            settings_manager.save_settings()
            return "save_and_exit", None
        
        # ── Điều chỉnh âm thanh và độ khó ──
        if event.key == pygame.K_1:
            # Âm thanh nhạc nền
            return "menu_item_1", 1
        elif event.key == pygame.K_2:
            # Âm thanh hiệu ứng
            return "menu_item_2", 2
        elif event.key == pygame.K_3:
            # Độ khó
            return "menu_item_3", 3
        elif event.key == pygame.K_4:
            # Hiệu ứng đồ họa
            current = settings_manager.get_graphics_effects()
            settings_manager.set_graphics_effects(not current)
            return "toggle_graphics", None
        elif event.key == pygame.K_5:
            # Hiển thị lưới
            current = settings_manager.get_show_grid()
            settings_manager.set_show_grid(not current)
            return "toggle_grid", None
        
        # ← → để điều chỉnh giá trị
        elif event.key == pygame.K_LEFT:
            if current_menu_item == 1:
                # Giảm âm thanh nhạc nền
                vol = settings_manager.get_music_volume()
                settings_manager.set_music_volume(vol - 0.1)
                return "adjust_music_down", 1
            elif current_menu_item == 2:
                # Giảm âm thanh hiệu ứng
                vol = settings_manager.get_sfx_volume()
                settings_manager.set_sfx_volume(vol - 0.1)
                return "adjust_sfx_down", 2
            elif current_menu_item == 3:
                # Giảm độ khó
                diff = settings_manager.get_difficulty()
                difficulties = ["easy", "medium", "hard"]
                idx = difficulties.index(diff)
                if idx > 0:
                    settings_manager.set_difficulty(difficulties[idx - 1])
                return "adjust_difficulty_down", 3
        
        elif event.key == pygame.K_RIGHT:
            if current_menu_item == 1:
                # Tăng âm thanh nhạc nền
                vol = settings_manager.get_music_volume()
                settings_manager.set_music_volume(vol + 0.1)
                return "adjust_music_up", 1
            elif current_menu_item == 2:
                # Tăng âm thanh hiệu ứng
                vol = settings_manager.get_sfx_volume()
                settings_manager.set_sfx_volume(vol + 0.1)
                return "adjust_sfx_up", 2
            elif current_menu_item == 3:
                # Tăng độ khó
                diff = settings_manager.get_difficulty()
                difficulties = ["easy", "medium", "hard"]
                idx = difficulties.index(diff)
                if idx < len(difficulties) - 1:
                    settings_manager.set_difficulty(difficulties[idx + 1])
                return "adjust_difficulty_up", 3
    
    return "continue", current_menu_item
