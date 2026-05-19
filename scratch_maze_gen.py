import random
rows, cols = 30, 60
maze = [['0' for _ in range(cols)] for _ in range(rows)]
for r in range(rows):
    maze[r][0] = '1'
    maze[r][cols-1] = '1'
for c in range(cols):
    maze[0][c] = '1'
    maze[rows-1][c] = '1'

# Thêm một vài cụm thiên thạch
for _ in range(18):
    cr, cc = random.randint(3, rows-4), random.randint(3, cols-4)
    for _ in range(random.randint(5, 12)):
        dr, dc = random.randint(-2, 2), random.randint(-2, 2)
        if 1 < cr+dr < rows-2 and 1 < cc+dc < cols-2:
            maze[cr+dr][cc+dc] = '1'

maze[1][1] = 'P'
maze[rows-2][cols-2] = 'E'
maze[1][2] = '0'
maze[2][1] = '0'

with open('level.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_map = False
for line in lines:
    if line.startswith('STATIC_MAP = ['):
        in_map = True
        new_lines.append(line)
        for row in maze:
            new_lines.append(f'    \"{"".join(row)}\",\n')
    elif in_map and line.strip() == ']':
        in_map = False
        new_lines.append(line)
    elif not in_map:
        new_lines.append(line)

with open('level.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Updated map in level.py")
