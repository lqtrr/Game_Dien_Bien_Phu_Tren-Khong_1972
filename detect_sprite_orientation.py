# -*- coding: utf-8 -*-
"""
detect_sprite_orientation.py
Doc sprite -> tinh huong mu may bay (UP/DOWN/LEFT/RIGHT)
bang cach phan tich trong tam cua cac pixel toi mau.
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image
import numpy as np

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

SPRITES = [
    ('player_ship.png',    'MiG-21 (player)'),
    ('dfs_ship.png',       'F-4 Phantom (DFS)'),
    ('bfs_ship.png',       'F-105 Thunderchief (BFS)'),
    ('astar_ship.png',     'F-111 Aardvark (A*)'),
    ('heuristic_ship.png', 'MiG-17 (Heuristic)'),
]

def detect_nose_direction(filename):
    """
    Phan tich trong tam cua pixel toi (aircraft body) va so sanh
    voi trong tam anh -> tim phuong huong mu may bay.
    Tra ve: 'up' | 'down' | 'left' | 'right' va do lech goc (offset)
    """
    path = os.path.join(ASSETS, filename)
    img = Image.open(path).convert('RGBA')
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]

    alpha = arr[:, :, 3]
    # Lay nhung pixel co alpha > 50 (la phan than may bay)
    mask = alpha > 50

    if mask.sum() < 10:
        return 'unknown', 0, 'not enough pixels'

    ys, xs = np.where(mask)
    cy_all = ys.mean()
    cx_all = xs.mean()

    img_cy = h / 2.0
    img_cx = w / 2.0

    dy = cy_all - img_cy   # + = trong tam thap hon giua anh
    dx = cx_all - img_cx   # + = trong tam sang phai giua anh

    # Trong tam may bay lech ve phia nao thi phan muoi may bay o phia nguoc lai
    # (vi mu thuong mong/nho hon than -> trong tam nghieng ve phia duoi)
    # => mu o phia nguoc voi trong tam

    # Phan tich phan tu ve phia trong tam (cuoi) va phia nguoc (mu)
    # Chia anh lam 4 phan, dem pixel moi phan
    top    = mask[:h//3,  :].sum()
    bottom = mask[2*h//3:, :].sum()
    left   = mask[:, :w//3].sum()
    right  = mask[:, 2*w//3:].sum()

    # Phan co it pixel hon la phia mu may bay (mu nho/mong)
    parts = {'up': top, 'down': bottom, 'left': left, 'right': right}
    nose_dir = min(parts, key=parts.get)

    # Offset can them vao cong thuc: -math.degrees(angle) + offset
    # De sprite quay dung huong khi bay
    # Gia su angle=0 (bay sang phai), pygame.rotate(img, 0) = khong xoay
    # Neu mu huong len (up):   can xoay them -90  -> offset = -90
    # Neu mu huong xuong (down): can xoay +90  -> offset = +90
    # Neu mu huong trai (left): can xoay 180  -> offset = 180
    # Neu mu huong phai (right): khong them -> offset = 0
    offset_map = {
        'up':    -90,
        'down':  +90,
        'left':  180,
        'right':  0,
    }
    offset = offset_map[nose_dir]

    detail = f"nose:{nose_dir}  top={top} bot={bottom} L={left} R={right}  cx_all={cx_all:.1f}/{img_cx:.1f}  cy_all={cy_all:.1f}/{img_cy:.1f}"
    return nose_dir, offset, detail

print("=" * 65)
print("  Sprite nose-direction detection")
print("=" * 65)
for filename, label in SPRITES:
    path = os.path.join(ASSETS, filename)
    if not os.path.exists(path):
        print(f"  MISSING: {filename}")
        continue
    direction, offset, detail = detect_nose_direction(filename)
    print(f"\n  {label}")
    print(f"    file   : {filename}")
    print(f"    nose   : {direction}")
    print(f"    offset : {offset:+d}  (use in rotate formula)")
    print(f"    detail : {detail}")

print("\n" + "=" * 65)
print("  Cong thuc xoay DUNG:")
print("    pygame.transform.rotate(img, -math.degrees(angle) + OFFSET)")
print("=" * 65)
