"""
Spatial Hashing System - Tối ưu collision detection
Chia bản đồ thành các grid cells để tránh O(n²) checks
"""
import math

class SpatialHash:
    """Quản lý collision detection hiệu quả với spatial hashing"""

    def __init__(self, cell_size=200):
        """
        cell_size: Kích thước mỗi cell (pixels)
        Khuyến cáo: 200-300 pixels để balance giữa memory và performance
        """
        self.cell_size = cell_size
        self.grid = {}  # {(grid_x, grid_y): [objects]}
        self.object_cells = {}  # {object_id: [(grid_x, grid_y), ...]}

    def get_cell_coords(self, pixel_x, pixel_y):
        """Chuyển đổi pixel coords thành grid cell"""
        grid_x = int(pixel_x // self.cell_size)
        grid_y = int(pixel_y // self.cell_size)
        return (grid_x, grid_y)

    def get_cells_for_radius(self, pixel_x, pixel_y, radius):
        """Lấy tất cả cells mà object occupies (dựa vào radius)"""
        cells = set()
        # Tính bounding box
        min_x = int((pixel_x - radius) // self.cell_size)
        max_x = int((pixel_x + radius) // self.cell_size)
        min_y = int((pixel_y - radius) // self.cell_size)
        max_y = int((pixel_y + radius) // self.cell_size)

        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                cells.add((gx, gy))
        return cells

    def insert(self, obj, obj_id, radius):
        """Thêm object vào spatial hash"""
        cells = self.get_cells_for_radius(obj.pixel_x, obj.pixel_y, radius)
        self.object_cells[obj_id] = cells

        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append((obj_id, obj))

    def update(self, obj, obj_id, radius):
        """Cập nhật vị trí object (gọi mỗi frame sau khi move)"""
        new_cells = self.get_cells_for_radius(obj.pixel_x, obj.pixel_y, radius)
        old_cells = self.object_cells.get(obj_id, set())

        # Xóa từ cells cũ
        for cell in old_cells - new_cells:
            if cell in self.grid:
                self.grid[cell] = [(oid, o) for oid, o in self.grid[cell] if oid != obj_id]

        # Thêm vào cells mới
        for cell in new_cells - old_cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append((obj_id, obj))

        self.object_cells[obj_id] = new_cells

    def remove(self, obj_id):
        """Xóa object khỏi spatial hash"""
        cells = self.object_cells.get(obj_id, set())
        for cell in cells:
            if cell in self.grid:
                self.grid[cell] = [(oid, o) for oid, o in self.grid[cell] if oid != obj_id]

        del self.object_cells[obj_id]

    def get_nearby(self, pixel_x, pixel_y, radius):
        """Lấy tất cả objects gần vị trí (thay vì check tất cả)"""
        nearby = []
        cells = self.get_cells_for_radius(pixel_x, pixel_y, radius * 2)

        seen = set()
        for cell in cells:
            if cell in self.grid:
                for obj_id, obj in self.grid[cell]:
                    if obj_id not in seen:
                        nearby.append(obj)
                        seen.add(obj_id)

        return nearby

    def clear(self):
        """Clear toàn bộ spatial hash"""
        self.grid.clear()
        self.object_cells.clear()


def check_circle_collision(obj1, obj2, dist_threshold):
    """
    Kiểm tra va chạm giữa 2 objects với bán kính
    Nhanh hơn so với tính toán khoảng cách chính xác nếu ko cần
    """
    dx = obj1.pixel_x - obj2.pixel_x
    dy = obj1.pixel_y - obj2.pixel_y
    dist_sq = dx*dx + dy*dy
    threshold_sq = dist_threshold * dist_threshold
    return dist_sq < threshold_sq


def get_distance(obj1, obj2):
    """Tính khoảng cách chính xác giữa 2 objects"""
    dx = obj1.pixel_x - obj2.pixel_x
    dy = obj1.pixel_y - obj2.pixel_y
    return math.hypot(dx, dy)
