import collections
import heapq
from settings import LOCAL_GRID_RADIUS

def get_neighbors(r, c, level):
    """Lấy danh sách các ô hợp lệ xung quanh (Trên, Dưới, Trái, Phải)"""
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if level.is_valid_pos(nr, nc):
            neighbors.append((nr, nc))
    return neighbors

def is_within_radius(node, start):
    """Giới hạn vùng tìm kiếm để tránh vòng lặp vô hạn trong Không gian Vô tận"""
    return abs(node[0] - start[0]) <= LOCAL_GRID_RADIUS and abs(node[1] - start[1]) <= LOCAL_GRID_RADIUS

def dfs_path(start, target, level):
    if start == target: return [], set()
    stack = [(start, [start])]
    visited = set()
    explored = set()
    
    best_path = []
    best_dist = heuristic(start, target)

    while stack:
        current, path = stack.pop()
        
        if current in visited:
            continue
            
        visited.add(current)
        explored.add(current)
        
        d = heuristic(current, target)
        if d < best_dist:
            best_dist = d
            best_path = path
        
        if current == target:
            return path[1:], explored

        for neighbor in get_neighbors(current[0], current[1], level):
            if neighbor not in visited and is_within_radius(neighbor, start):
                stack.append((neighbor, path + [neighbor]))
                
        if len(visited) > 1000: # Cắt tỉa (Fallback an toàn)
            break
            
    return best_path[1:], explored

def bfs_path(start, target, level):
    if start == target: return [], set()
    queue = collections.deque([(start, [start])])
    visited = {start}
    explored = set()

    best_path = []
    best_dist = heuristic(start, target)

    while queue:
        current, path = queue.popleft()
        explored.add(current)
        
        d = heuristic(current, target)
        if d < best_dist:
            best_dist = d
            best_path = path
            
        if current == target:
            return path[1:], explored
            
        for neighbor in get_neighbors(current[0], current[1], level):
            if neighbor not in visited and is_within_radius(neighbor, start):
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
                
        if len(visited) > 1000: # Cắt tỉa
            break
                
    return best_path[1:], explored

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_path(start, target, level):
    if start == target: return [], set()
    pq = []
    heapq.heappush(pq, (0, start, [start]))
    g_score = {start: 0}
    explored = set()
    
    best_path = []
    best_dist = heuristic(start, target)
    
    while pq:
        f, current, path = heapq.heappop(pq)
        
        if current in explored:
            continue
        explored.add(current)
        
        d = heuristic(current, target)
        if d < best_dist:
            best_dist = d
            best_path = path
            
        if current == target:
            return path[1:], explored
            
        for neighbor in get_neighbors(current[0], current[1], level):
            if not is_within_radius(neighbor, start):
                continue
                
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, target)
                heapq.heappush(pq, (f_score, neighbor, path + [neighbor]))
                
        if len(explored) > 1000: # Cắt tỉa
            break
                
    return best_path[1:], explored

def heuristic_path(start, target, level):
    if start == target: return [], set()
    pq = []
    # Priority is just the heuristic h(n)
    heapq.heappush(pq, (heuristic(start, target), start, [start]))
    explored = set()
    
    best_path = []
    best_dist = heuristic(start, target)
    
    while pq:
        h, current, path = heapq.heappop(pq)
        
        if current in explored:
            continue
        explored.add(current)
        
        d = heuristic(current, target)
        if d < best_dist:
            best_dist = d
            best_path = path
            
        if current == target:
            return path[1:], explored
            
        for neighbor in get_neighbors(current[0], current[1], level):
            if not is_within_radius(neighbor, start):
                continue
                
            if neighbor not in explored:
                h_score = heuristic(neighbor, target)
                heapq.heappush(pq, (h_score, neighbor, path + [neighbor]))
                
        if len(explored) > 1000: # Cắt tỉa
            break
                
    return best_path[1:], explored
