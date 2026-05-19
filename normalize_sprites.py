# -*- coding: utf-8 -*-
"""
normalize_sprites.py
Xoay tat ca sprite ve huong len tren (up/north) va tach nen sach hon.
Sau khi chay script nay, tat ca sprite deu quy ve huong LEN TREN,
nen trong entities.py chi can dung offset -90 duy nhat (pygame coi 0deg = sang phai).
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image
import numpy as np
from collections import deque

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# (filename, huong_hien_tai)
# up=0 down=180 left=90 (xoay CW) right=270 (xoay CW)
# De chuan hoa ve UP, can xoay nguoc chieu: PIL.rotate(deg, expand=True)
# PIL.rotate la CCW. De xoay CW N do = rotate(-N)
SPRITES = [
    ('player_ship.png',     'left'),   # Mu sang trai -> xoay 90 CW = rotate(-90)
    ('dfs_ship.png',        'left'),   # F-4, mu trai -> rotate(-90)
    ('bfs_ship.png',        'up'),     # F-105, dung roi
    ('astar_ship.png',      'up'),     # F-111, thu them (sau khi tach nen)
    ('heuristic_ship.png',  'left'),   # MiG-17, mu trai -> rotate(-90)
]

# Goc xoay de dua ve UP (PIL CCW)
ROTATE_TO_UP = {
    'up':    0,
    'down':  180,
    'left':  -90,   # xoay 90 CW (= -90 CCW trong PIL)
    'right':  90,   # xoay 90 CCW
}

# ─────────────────────────────────────────────────────────────────────────────
# Tach nen nang cao
# ─────────────────────────────────────────────────────────────────────────────
def remove_bg_aggressive(arr):
    """
    2-pass flood-fill tu tat ca bien anh.
    Pass 1: tolerance cao cho nen trang/den goc.
    Pass 2: mo rong nhe de lay nen xam tran vien.
    """
    h, w = arr.shape[:2]

    # Phat hien loai nen
    border_pixels = np.concatenate([arr[0,:,:3], arr[-1,:,:3], arr[:,0,:3], arr[:,-1,:3]])
    mean_lum = border_pixels.mean()
    if mean_lum < 100:
        bg_ref = np.array([0, 0, 0], dtype=float)
        tol_sq = (75.0 ** 2) * 3
    else:
        bg_ref = np.array([255, 255, 255], dtype=float)
        tol_sq = (70.0 ** 2) * 3

    print(f"    bg={'black' if mean_lum<100 else 'white'} lum={mean_lum:.1f}", flush=True)

    mask = np.zeros((h, w), dtype=bool)

    def is_bg(y, x):
        if mask[y, x]: return False
        diff = arr[y, x, :3].astype(float) - bg_ref
        return float(np.dot(diff, diff)) < tol_sq

    queue = deque()
    for x in range(w):
        if is_bg(0, x):     mask[0, x]=True;   queue.append((0,x))
        if is_bg(h-1, x):   mask[h-1,x]=True;  queue.append((h-1,x))
    for y in range(1, h-1):
        if is_bg(y, 0):     mask[y,0]=True;    queue.append((y,0))
        if is_bg(y, w-1):   mask[y,w-1]=True;  queue.append((y,w-1))

    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    while queue:
        cy, cx = queue.popleft()
        for dy2, dx2 in dirs:
            ny, nx = cy+dy2, cx+dx2
            if 0<=ny<h and 0<=nx<w and not mask[ny,nx]:
                if is_bg(ny, nx):
                    mask[ny,nx] = True
                    queue.append((ny,nx))

    # Pass 2: mo rong them 1-2 pixel de xoa vien nen con sot
    from scipy.ndimage import binary_dilation
    expanded = binary_dilation(mask, iterations=2)
    # Nhung pixel mo rong moi: giam alpha dan (mo nhat)
    edge = expanded & ~mask
    result = arr.copy()
    result[mask,  3] = 0
    result[edge,  3] = np.clip(result[edge, 3].astype(int) - 180, 0, 255).astype(np.uint8)
    return result

# ─────────────────────────────────────────────────────────────────────────────
def process_sprite(filename, native_dir):
    path = os.path.join(ASSETS, filename)
    if not os.path.exists(path):
        print(f"  MISSING: {filename}", flush=True)
        return

    print(f"\n  {filename}  [native={native_dir}]", flush=True)

    # 1. Mo anh goc
    img = Image.open(path).convert('RGBA')
    arr = np.array(img, dtype=np.uint8)

    # 2. Tach nen manh
    arr = remove_bg_aggressive(arr)
    img = Image.fromarray(arr, 'RGBA')

    # 3. Xoay ve huong UP
    rot_deg = ROTATE_TO_UP.get(native_dir, 0)
    if rot_deg != 0:
        img = img.rotate(rot_deg, expand=True, resample=Image.BICUBIC)
        # Cat lai thanh vuong
        side = max(img.width, img.height)
        sq = Image.new('RGBA', (side, side), (0,0,0,0))
        sq.paste(img, ((side - img.width)//2, (side - img.height)//2))
        img = sq
        print(f"    rotated {rot_deg} deg CCW to face UP", flush=True)
    else:
        print(f"    already facing UP, no rotation", flush=True)

    # 4. Luu
    img.save(path, 'PNG')
    print(f"    OK -> {filename}", flush=True)

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 55, flush=True)
    print("  Normalize + remove-bg all aircraft sprites", flush=True)
    print("=" * 55, flush=True)

    for filename, native_dir in SPRITES:
        try:
            process_sprite(filename, native_dir)
        except Exception as e:
            print(f"  ERROR {filename}: {e}", flush=True)
            import traceback; traceback.print_exc()

    print("\nDONE!", flush=True)
