# main.py
import pygame
import sys
from constants import *
from engine import MazeEngine
from algorithms import get_visible_cells, compute_bfs
from entities import AI_Agent_Tom, PowerUpManager
from ui_components import ParticleSystem, UIRenderer, MenuScreen, PauseMenu
from ui_renderer import GameRenderer

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("The Maze Pursuit: Cyber Adversarial Search")
        self.clock = pygame.time.Clock()
        
        self.fonts = {
            "title": pygame.font.SysFont("Impact", 42),
            "header": pygame.font.SysFont("Segoe UI", 20, bold=True),
            "body": pygame.font.SysFont("Segoe UI", 14, bold=True)
        }
        
        self.ps = ParticleSystem()
        self.gr = GameRenderer()
        self.menu_screen = MenuScreen()
        self.pause_menu = PauseMenu(self.fonts["title"], self.fonts["header"])
        self.game_state = "MENU"
        self.winner = None

    def main_loop(self):
        while True:
            if self.game_state == "MENU":
                self.process_menu_inputs()
                self.menu_screen.draw(self.screen, self.fonts)
            elif self.game_state == "RUNNING":
                self.process_game_logic()
                self.render_game()
            elif self.game_state == "PAUSED":
                self.process_pause_inputs()
                self.pause_menu.draw(self.screen)
            elif self.game_state == "OVER":
                self.process_over_inputs()
                self.render_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)

    def init_simulation(self):
        self.maze, self.items, self.jerry_pos, tom_pos, self.exit_pos = \
            MazeEngine.deploy_environment(self.map_mode)
        self.tom = AI_Agent_Tom(tom_pos)
        self.powerups = PowerUpManager()
        self.turn_count = 1
        self.max_turns = 35 # Diperketat dari 50 ke 35 untuk meningkatkan intensitas permainan
        self.active_turn = "JERRY"
        self.jerry_auto_path = []
        self.gr.needs_full_redraw = True
        self.last_tick = pygame.time.get_ticks()

    def process_menu_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = self.menu_screen.handle_click(event.pos)
                if action == "START_GAME":
                    self.map_mode = self.menu_screen.selections["map_mode"]
                    self.difficulty = self.menu_screen.selections["difficulty"]
                    self.control_mode = self.menu_screen.selections["control_mode"]
                    self.init_simulation()
                    self.game_state = "RUNNING"

    def process_pause_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.game_state = "RUNNING"
                self.gr.needs_full_redraw = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = self.pause_menu.handle_click(event.pos)
                if action == "RESUME":
                    self.game_state = "RUNNING"
                    self.gr.needs_full_redraw = True
                elif action == "MENU":
                    self.game_state = "MENU"

    def process_game_logic(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.game_state = "PAUSED"
                return

        now = pygame.time.get_ticks()
        if now - self.last_tick < 260: return 

        if self.jerry_pos == self.tom.pos:
            self.game_state = "OVER"; self.winner = "TOM AI"; return
        if self.maze[self.jerry_pos[1]][self.jerry_pos[0]] == "exit":
            self.game_state = "OVER"; self.winner = "JERRY"; return
        if self.turn_count >= self.max_turns:
            self.game_state = "OVER"; self.winner = "TOM (TIMEOUT)"; return

        self.last_tick = now
        if self.active_turn == "JERRY":
            self.run_jerry_turn()
        else:
            radar_active = self.powerups.is_active("RADAR")
            self.tom.update_fsm_and_move(self.jerry_pos, self.maze, self.difficulty, self.map_mode, self.turn_count, radar_active)
            self.powerups.update()
            self.turn_count += 1
            self.active_turn = "JERRY"
            self.jerry_auto_path = []

    def run_jerry_turn(self):
        mp = 3 if self.powerups.is_active("CHEESE") else 2
        if self.control_mode == "AUTO":
            if not self.jerry_auto_path:
                self.jerry_auto_path = compute_bfs(self.jerry_pos, self.exit_pos, self.maze, self.map_mode, self.turn_count)
            if self.jerry_auto_path:
                self.jerry_pos = self.jerry_auto_path.pop(0)
                self.check_items_pickup()
            self.active_turn = "TOM"
        else:
            mx, my = pygame.mouse.get_pos()
            gx = (mx - OFFSET_X) // TILE_SIZE
            gy = (my - OFFSET_Y) // TILE_SIZE
            visible = get_visible_cells(self.jerry_pos, 4, self.maze)
            
            if pygame.mouse.get_pressed()[0]:
                if (gx, gy) in visible:
                    path = compute_bfs(self.jerry_pos, (gx, gy), self.maze, self.map_mode, self.turn_count)
                    if path:
                        self.jerry_pos = path[:mp][-1]
                        self.check_items_pickup()
                        self.active_turn = "TOM"

    def check_items_pickup(self):
        jx, jy = self.jerry_pos
        cell_center = (OFFSET_X + jx*TILE_SIZE + TILE_SIZE//2, OFFSET_Y + jy*TILE_SIZE + TILE_SIZE//2)
        if self.items[jy][jx] == "cheese":
            self.powerups.apply_powerup("CHEESE")
            self.items[jy][jx] = None
            self.ps.emit(*cell_center, COLOR_CHEESE)
        elif self.items[jy][jx] == "radar":
            self.powerups.apply_powerup("RADAR")
            self.items[jy][jx] = None
            self.ps.emit(*cell_center, COLOR_RADAR)

    def render_game(self):
        r = POWERUP_CONFIG["RADAR"]["radius"] if self.powerups.is_active("RADAR") else 4
        visible_cells = get_visible_cells(self.jerry_pos, r, self.maze)
        
        self.gr.render_maze_optimized(self.screen, self.maze, self.items, visible_cells, self.powerups.is_active("RADAR"))
        
        # Menggambar Agen Jerry
        jx, jy = self.jerry_pos
        j_cx, j_cy = OFFSET_X + jx*TILE_SIZE + TILE_SIZE//2, OFFSET_Y + jy*TILE_SIZE + TILE_SIZE//2
        UIRenderer.draw_glow_rect(self.screen, (j_cx-12, j_cy-12, 24, 24), COLOR_JERRY, COLOR_JERRY, border_radius=12)

        # Menggambar Agen Tom jika masuk jangkauan pandang
        if (self.tom.pos in visible_cells) or self.powerups.is_active("RADAR"):
            tx, ty = self.tom.pos
            t_cx, t_cy = OFFSET_X + tx*TILE_SIZE + TILE_SIZE//2, OFFSET_Y + ty*TILE_SIZE + TILE_SIZE//2
            UIRenderer.draw_glow_rect(self.screen, (t_cx-12, t_cy-12, 24, 24), COLOR_TOM, COLOR_TOM, border_radius=12)

        self.ps.update_and_draw(self.screen)
        self.draw_hud()

    def draw_hud(self):
        px, py = 930, 110
        UIRenderer.draw_glow_rect(self.screen, (px, py, 180, 560), COLOR_PANEL, COLOR_PANEL_BORDER, border_radius=14, width=2)
        
        def render_stat(lbl, val, offset_y, color=COLOR_TEXT):
            self.screen.blit(self.fonts["body"].render(lbl, True, COLOR_MUTED), (px+15, py+offset_y))
            self.screen.blit(self.fonts["header"].render(str(val), True, color), (px+15, py+offset_y+16))

        render_stat("TURN STEP", f"{self.turn_count} / {self.max_turns}", 20, COLOR_JERRY)
        render_stat("ACTIVE TURN", self.active_turn, 85, COLOR_JERRY if self.active_turn == "JERRY" else COLOR_TOM)
        render_stat("TOM STATE FSM", self.tom.state, 155, COLOR_TOM)
        render_stat("MAP LABYRINTH", self.map_mode, 225, COLOR_EXIT)
        render_stat("AI DIFFICULTY", self.difficulty, 295, COLOR_FIRE)

        if self.powerups.is_active("RADAR"):
            render_stat("RADAR INFRARED", f"{self.powerups.get_remaining('RADAR')} Turns", 370, COLOR_RADAR)
        if self.powerups.is_active("CHEESE"):
            render_stat("SPEED BURST", f"{self.powerups.get_remaining('CHEESE')} Turns", 440, COLOR_CHEESE)

    def process_over_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                self.game_state = "MENU"

    def render_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((5, 4, 10))
        overlay.set_alpha(225)
        self.screen.blit(overlay, (0, 0))
        
        msg = f"SIMULATION OVER: {self.winner} WINS"
        UIRenderer.draw_neon_text(self.screen, msg, self.fonts["title"], COLOR_EXIT if "JERRY" in self.winner else COLOR_TOM, COLOR_WALL, (WIDTH//2 - 290, HEIGHT//2 - 60))
        self.screen.blit(self.fonts["header"].render("Pencet tombol keyboard atau klik mouse untuk kembali", True, COLOR_TEXT), (WIDTH//2 - 240, HEIGHT//2 + 15))

if __name__ == "__main__":
    game = GameController()
    game.main_loop()