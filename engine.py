
# engine.py
import random
from constants import GRID_WIDTH, GRID_HEIGHT

class MazeEngine:
    @staticmethod
    def generate_base_maze():
        w, h = GRID_WIDTH, GRID_HEIGHT
        maze = [["wall" for _ in range(w)] for _ in range(h)]
        
        start_x, start_y = 1, 1
        maze[start_y][start_x] = "floor"
        walls = []
        
        def add_walls(cx, cy):
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < w - 1 and 0 < ny < h - 1 and maze[ny][nx] == "wall":
                    walls.append((cx + dx // 2, cy + dy // 2, nx, ny))
                    
        add_walls(start_x, start_y)
        while walls:
            wx, wy, nx, ny = random.choice(walls)
            walls.remove((wx, wy, nx, ny))
            if maze[ny][nx] == "wall":
                maze[wy][wx] = "floor"
                maze[ny][nx] = "floor"
                add_walls(nx, ny)
                
        # Membuka persimpangan labirin secara acak agar jalur pelarian dinamis
        for _ in range((w * h) // 22):
            rx, ry = random.randint(1, w - 2), random.randint(1, h - 2)
            if maze[ry][rx] == "wall":
                neighbors = sum(1 for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)] if maze[ry + dy][rx + dx] == "floor")
                if neighbors >= 2: 
                    maze[ry][rx] = "floor"
                    
        return maze

    @staticmethod
    def deploy_environment(map_type):
        w, h = GRID_WIDTH, GRID_HEIGHT
        maze = MazeEngine.generate_base_maze()
        items = [[None for _ in range(w)] for _ in range(h)]
        
        if map_type == "CAVE":
            for _ in range(9):
                cx, cy = random.randint(2, w-3), random.randint(2, h-3)
                if maze[cy][cx] == "floor" and (cx, cy) != (1, 1):
                    maze[cy][cx] = "chasm"
        elif map_type == "VOLCANO":
            for y in range(h):
                for x in range(w):
                    if (x == y or x == w - y - 1) and maze[y][x] == "floor" and (x != 1 or y != 1):
                        if random.random() < 0.28: 
                            maze[y][x] = "fire_zone"

        floors = [(x, y) for y in range(h) for x in range(w) if maze[y][x] == "floor"]
        jerry_pos = (1, 1)
        if jerry_pos in floors: 
            floors.remove(jerry_pos)
        
        floors.sort(key=lambda p: abs(p[0] - jerry_pos[0]) + abs(p[1] - jerry_pos[1]), reverse=True)
        exit_pos = floors[0]
        maze[exit_pos[1]][exit_pos[0]] = "exit"
        floors.remove(exit_pos)
        
        tom_pos = floors[int(len(floors) * 0.15)]
        floors.remove(tom_pos)
        
        random.shuffle(floors)
        for i in range(min(5, len(floors))):
            items[floors[i][1]][floors[i][0]] = "cheese"
        if len(floors) > 5:
            items[floors[5][1]][floors[5][0]] = "radar"
            
        return maze, items, jerry_pos, tom_pos, exit_pos