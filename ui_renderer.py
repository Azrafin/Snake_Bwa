# ui_renderer.py
import pygame
from constants import *
from ui_components import UIRenderer

class GameRenderer:
    """Mengoptimalkan render grid ubin hanya jika terjadi perubahan visibilitas"""
    def __init__(self):
        self.last_visible_cells = set()
        self.needs_full_redraw = True

    def render_maze_optimized(self, screen, maze, items, visible_cells, radar_active):
        if self.needs_full_redraw:
            screen.fill(COLOR_BG)
            self._render_grid_subset(screen, maze, items, set((x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)), visible_cells, radar_active)
            self.needs_full_redraw = False
            self.last_visible_cells = visible_cells.copy()
            return

        changed_cells = visible_cells.symmetric_difference(self.last_visible_cells)
        self._render_grid_subset(screen, maze, items, changed_cells, visible_cells, radar_active)
        self.last_visible_cells = visible_cells.copy()

    def _render_grid_subset(self, screen, maze, items, subset, visible_cells, radar_active):
        for x, y in subset:
            rx, ry = OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE
            
            if (x, y) not in visible_cells and not radar_active:
                pygame.draw.rect(screen, COLOR_BG, (rx, ry, TILE_SIZE, TILE_SIZE))
                continue

            pygame.draw.rect(screen, COLOR_FLOOR, (rx, ry, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (28, 25, 48), (rx, ry, TILE_SIZE, TILE_SIZE), width=1)
            
            cell = maze[y][x]
            if cell == "wall":
                UIRenderer.draw_glow_rect(screen, (rx+2, ry+2, TILE_SIZE-4, TILE_SIZE-4), COLOR_WALL, COLOR_WALL_GLOW, border_radius=4)
            elif cell == "exit":
                UIRenderer.draw_glow_rect(screen, (rx+2, ry+2, TILE_SIZE-4, TILE_SIZE-4), COLOR_EXIT, COLOR_EXIT, width=2)
            elif cell == "chasm":
                pygame.draw.rect(screen, COLOR_CHASM, (rx+2, ry+2, TILE_SIZE-4, TILE_SIZE-4), border_radius=4)
                pygame.draw.rect(screen, COLOR_CHASM_BORDER, (rx+2, ry+2, TILE_SIZE-4, TILE_SIZE-4), width=1, border_radius=4)
            elif cell == "fire_zone":
                pygame.draw.rect(screen, COLOR_FIRE, (rx+2, ry+2, TILE_SIZE-4, TILE_SIZE-4), border_radius=4)

            it = items[y][x]
            if it == "cheese":
                pygame.draw.circle(screen, COLOR_CHEESE, (rx+TILE_SIZE//2, ry+TILE_SIZE//2), 7)
            elif it == "radar":
                pygame.draw.circle(screen, COLOR_RADAR, (rx+TILE_SIZE//2, ry+TILE_SIZE//2), 8, width=2)