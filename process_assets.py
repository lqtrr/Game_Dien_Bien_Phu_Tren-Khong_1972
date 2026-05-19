# -*- coding: utf-8 -*-
"""
process_assets.py - Remove background from all game sprites using flood-fill BFS.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image
import numpy as np
from collections import deque

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# (filename, bg_type): 'white' | 'black' | 'auto'
SPRITES = [
    ('player_ship.png',    'auto'),   # MiG-21
    ('dfs_ship.png',       'auto'),   # F-4 Phantom
    ('bfs_ship.png',       'auto'),   # F-105 Thunderchief
    ('astar_ship.png',     'auto'),   # F-111 Aardvark
    ('heuristic_ship.png', 'auto'),   # MiG-17
    ('sam_site.png',       'auto'),   # SAM site
    ('mountain.png',       'auto'),   # Mountain obstacle
    ('airbase.png',        'auto'),   # Airbase exit
]

def detect_bg_type(arr):
    """Auto-detect background type based on border pixels brightness."""
    h, w = arr.shape[:2]
    border = np.concatenate([
        arr[0, :, :3],
        arr[-1, :, :3],
        arr[:, 0, :3],
        arr[:, -1, :3],
    ])
    mean_lum = border.mean()
    return 'black' if mean_lum < 128 else 'white'

def remove_bg_floodfill(path_in, path_out, bg_type='auto', tolerance=45):
    """Flood-fill BFS from border pixels to find and remove background."""
    img = Image.open(path_in).convert('RGBA')
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]

    if bg_type == 'auto':
        bg_type = detect_bg_type(arr)

    print(f"  [{bg_type.upper()} BG] {os.path.basename(path_in)}", flush=True)

    # Background reference color
    bg_rgb = np.array([0, 0, 0], dtype=int) if bg_type == 'black' else np.array([255, 255, 255], dtype=int)

    # Boolean mask for background pixels
    mask = np.zeros((h, w), dtype=bool)

    def is_bg_pixel(y, x):
        if mask[y, x]:
            return False
        pixel = arr[y, x, :3].astype(int)
        dist = float(np.sqrt(np.sum((pixel - bg_rgb) ** 2)))
        return dist < (tolerance * 2.8)

    # Seed the BFS from all border pixels
    queue = deque()
    for x in range(w):
        if is_bg_pixel(0, x):       mask[0, x] = True;   queue.append((0, x))
        if is_bg_pixel(h-1, x):     mask[h-1, x] = True; queue.append((h-1, x))
    for y in range(1, h-1):
        if is_bg_pixel(y, 0):       mask[y, 0] = True;   queue.append((y, 0))
        if is_bg_pixel(y, w-1):     mask[y, w-1] = True; queue.append((y, w-1))

    # 8-directional BFS expansion
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in dirs:
            ny, nx = cy+dy, cx+dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx]:
                if is_bg_pixel(ny, nx):
                    mask[ny, nx] = True
                    queue.append((ny, nx))

    # Apply mask: set alpha=0 for background
    result = arr.copy()
    result[mask, 3] = 0

    # Soft edge: dilate mask and reduce alpha on edge pixels for anti-alias
    try:
        from scipy.ndimage import binary_dilation
        edge_mask = binary_dilation(mask, iterations=1) & ~mask
        edge_alpha = result[edge_mask, 3].astype(int) - 100
        result[edge_mask, 3] = np.clip(edge_alpha, 0, 255).astype(np.uint8)
    except ImportError:
        pass  # Skip soft edge if scipy not available

    out_img = Image.fromarray(result, 'RGBA')
    out_img.save(path_out, 'PNG')
    print(f"  OK -> {os.path.basename(path_out)}", flush=True)

def process_all():
    print("=" * 50, flush=True)
    print("  Sprite background removal - processing all...", flush=True)
    print("=" * 50, flush=True)

    for filename, bg_type in SPRITES:
        path = os.path.join(ASSETS, filename)
        if not os.path.exists(path):
            print(f"  MISSING: {filename}", flush=True)
            continue
        try:
            remove_bg_floodfill(path, path, bg_type=bg_type, tolerance=42)
        except Exception as e:
            print(f"  ERROR {filename}: {e}", flush=True)

    print("", flush=True)
    print("DONE! All sprites processed.", flush=True)

if __name__ == '__main__':
    process_all()
