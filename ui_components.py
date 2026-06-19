# ui_components.py
import pygame
import random
from constants import *

class MenuButton:
    """Komponen Tombol Reusable dengan deteksi tabrakan koordinat kursor"""
    def __init__(self, label, x, y, width=300, height=38, group=None, value=None):
        self.label = label
        self.rect = pygame.Rect(x, y, width, height)
        self.group = group
        self.value = value
        self.active = False
    
    def contains_point(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, screen, font_header, color_active, color_inactive, color_border):
        bg_color = color_active if self.active else color_inactive
        UIRenderer.draw_glow_rect(screen, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), bg_color, bg_color, border_radius=8)
        pygame.draw.rect(screen, color_border if self.active else COLOR_MUTED, self.rect, width=2, border_radius=8)
        
        text_surface = font_header.render(self.label, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MenuScreen:
    """Sistem Manajemen Layout Menu Utama"""
    def __init__(self):
        self.buttons = []
        self.selections = {"map_mode": "CLASSIC", "difficulty": "MEDIUM", "control_mode": "MANUAL"}
        self._setup_buttons()
    
    def _setup_buttons(self):
        button_data = [
            ("Base Map (Classic)", 420, 220, "map_mode", "CLASSIC"),
            ("Cave Map (Forgotten)", 420, 270, "map_mode", "CAVE"),
            ("Volcano Map (Core)", 420, 320, "map_mode", "VOLCANO"),
            ("Easy Mode (Depth 1)", 420, 430, "difficulty", "EASY"),
            ("Medium Mode (Depth 3)", 420, 480, "difficulty", "MEDIUM"),
            ("Hard Mode (Depth 5)", 420, 530, "difficulty", "HARD"),
            ("Manual Player Control", 420, 610, "control_mode", "MANUAL"),
            ("Auto Simulation AI", 420, 660, "control_mode", "AUTO"),
        ]
        for label, x, y, group, value in button_data:
            btn = MenuButton(label, x, y, group=group, value=value)
            if self.selections[group] == value:
                btn.active = True
            self.buttons.append(btn)
        
        # Tombol aksi tunggal
        self.start_btn = MenuButton("START SIMULATION", 850, 610, width=220, height=88)
        self.buttons.append(self.start_btn)

    def handle_click(self, pos):
        if self.start_btn.contains_point(pos):
            return "START_GAME"
        for btn in self.buttons:
            if btn.contains_point(pos) and btn.group:
                for other in self.buttons:
                    if other.group == btn.group:
                        other.active = (other == btn)
                self.selections[btn.group] = btn.value
        return None

    def draw(self, screen, fonts):
        screen.fill(COLOR_BG)
        for x in range(0, WIDTH, 40):
            pygame.draw.line(screen, (22, 19, 44), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(screen, (22, 19, 44), (0, y), (WIDTH, y))

        UIRenderer.draw_neon_text(screen, "THE MAZE PURSUIT : ADVERSARIAL SYSTEM", fonts["title"], COLOR_JERRY, COLOR_WALL, (80, 50))
        
        screen.blit(fonts["header"].render("PILIH LINGKUNGAN / MAP", True, COLOR_MUTED), (80, 225))
        screen.blit(fonts["header"].render("TINGKAT KESULITAN TOM AI", True, COLOR_MUTED), (80, 435))
        screen.blit(fonts["header"].render("SIMULATION KONTROL MODE", True, COLOR_MUTED), (80, 615))

        for btn in self.buttons:
            if btn == self.start_btn:
                btn.draw(screen, fonts["header"], COLOR_TOM, COLOR_PANEL, COLOR_TOM)
            else:
                btn.draw(screen, fonts["header"], COLOR_WALL, COLOR_PANEL, COLOR_PANEL_BORDER)

class PauseMenu:
    """Tampilan Overlay Jendela Jeda Game"""
    def __init__(self, font_title, font_header):
        self.font_title = font_title
        self.font_header = font_header
        self.buttons = [
            MenuButton("CONTINUE GAME", 425, 280, width=300, height=45),
            MenuButton("QUIT TO MAIN MENU", 425, 360, width=300, height=45)
        ]

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn.contains_point(pos):
                if btn.label == "CONTINUE GAME": return "RESUME"
                if btn.label == "QUIT TO MAIN MENU": return "MENU"
        return None

    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((5, 4, 10))
        overlay.set_alpha(210)
        screen.blit(overlay, (0, 0))
        
        UIRenderer.draw_neon_text(screen, "SYSTEM PAUSED", self.font_title, COLOR_JERRY, COLOR_WALL, (WIDTH // 2 - 160, 150))
        for btn in self.buttons:
            btn.draw(screen, self.font_header, COLOR_WALL, COLOR_PANEL, COLOR_PANEL_BORDER)

class ParticleSystem:
    """Edukasi visual ledakan partikel pendar saat penyerapan objek"""
    def __init__(self):
        self.particles = []

    def emit(self, cx, cy, color):
        if len(self.particles) > 400: return # Batas kapasitas tumpukan memori
        for _ in range(20):
            self.particles.append({
                "pos": [cx, cy],
                "vel": [random.uniform(-3.5, 3.5), random.uniform(-3.5, 3.5)],
                "radius": random.randint(3, 6),
                "lifetime": 1.0,
                "color": color
            })

    def update_and_draw(self, screen):
        for p in self.particles[:]:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["lifetime"] -= 0.04
            p["radius"] = max(0, p["radius"] - 0.15)
            if p["lifetime"] <= 0 or p["radius"] <= 0:
                self.particles.remove(p)
            else:
                alpha = int(p["lifetime"] * 255)
                s = pygame.Surface((int(p["radius"]*2), int(p["radius"]*2)), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["color"], alpha), (int(p["radius"]), int(p["radius"])), int(p["radius"]))
                screen.blit(s, (int(p["pos"][0] - p["radius"]), int(p["pos"][1] - p["radius"])))

class UIRenderer:
    @staticmethod
    def draw_glow_rect(screen, rect, color, glow_color, width=0, border_radius=6):
        for i in range(3, 0, -1):
            alpha = 45 // i
            overlay = pygame.Surface((rect[2] + i*2, rect[3] + i*2), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (*glow_color, alpha), (0, 0, rect[2]+i*2, rect[3]+i*2), width=width+i, border_radius=border_radius+i)
            screen.blit(overlay, (rect[0]-i, rect[1]-i))
        pygame.draw.rect(screen, color, rect, width=width, border_radius=border_radius)

    @staticmethod
    def draw_neon_text(screen, text, font, color, glow_color, pos):
        txt_glow = font.render(text, True, glow_color)
        txt_main = font.render(text, True, color)
        screen.blit(txt_glow, (pos[0]-1, pos[1]-1))
        screen.blit(txt_glow, (pos[0]+1, pos[1]+1))
        screen.blit(txt_main, pos)