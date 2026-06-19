# algorithms.py
import math
from collections import deque
from constants import GRID_WIDTH, GRID_HEIGHT

def get_valid_neighbors(pos, maze, map_mode="CLASSIC", turn_count=0):
    x, y = pos
    neighbors = []
    # Hambatan periodik Stalagmit di peta gua setiap kelipatan turn tertentu
    stalagmite_block = (map_mode == "CAVE" and (turn_count // 4) % 2 == 0)
    
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            cell = maze[ny][nx]
            if cell == "wall" or cell == "chasm":
                continue
            if cell == "fire_zone" and map_mode == "VOLCANO":
                continue
            if stalagmite_block and (nx + ny) % 6 == 0:
                continue
            neighbors.append((nx, ny))
    return neighbors

def compute_bfs(start, target, maze, map_mode="CLASSIC", turn_count=0):
    if start == target:
        return []
    queue = deque([(start, [])])
    visited = {start}
    
    while queue:
        curr, path = queue.popleft()
        if curr == target:
            return path
        for nxt in get_valid_neighbors(curr, maze, map_mode, turn_count):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return []

def calculate_los(x0, y0, x1, y1, maze):
    """Algoritma Bresenham Line-of-Sight dengan batas pengaman array"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    max_steps = max(dx, dy) + 1
    step = 0
    
    while step < max_steps:
        step += 1
        if not (0 <= x0 < GRID_WIDTH and 0 <= y0 < GRID_HEIGHT):
            return False
        if x0 == x1 and y0 == y1:
            return True
            
        cell = maze[y0][x0]
        if cell == "wall" or cell == "chasm":
            return False
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return False

def get_visible_cells(agent_pos, radius, maze):
    visible = set()
    cx, cy = agent_pos
    for y in range(max(0, cy - radius), min(GRID_HEIGHT, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(GRID_WIDTH, cx + radius + 1)):
            if math.hypot(x - cx, y - cy) <= radius + 0.5:
                if calculate_los(cx, cy, x, y, maze):
                    visible.add((x, y))
    return visible