# constants.py
import pygame

# Konfigurasi Window & Grid Matriks
WIDTH, HEIGHT = 1150, 780
GRID_WIDTH, GRID_HEIGHT = 23, 15
TILE_SIZE = 38
OFFSET_X, OFFSET_Y = 40, 110

# Palet Warna Neo-Dark Cyberpunk (RGB)
COLOR_BG = (10, 9, 18)             # Ultra Dark Violet
COLOR_PANEL = (19, 17, 36)         # Deep Slate Indigo
COLOR_PANEL_BORDER = (59, 130, 246) # Cyber Blue
COLOR_FLOOR = (16, 14, 28)         # Dark Floor Matrix

# Warna Neon Emisi (Glow Effects)
COLOR_WALL = (124, 58, 237)        # Neon Violet Wall
COLOR_WALL_GLOW = (76, 29, 149)    # Deep Violet Glow
COLOR_JERRY = (6, 182, 212)        # Electric Cyan
COLOR_TOM = (244, 63, 94)          # Radiant Crimson
COLOR_EXIT = (16, 185, 129)        # Emerald Neon
COLOR_CHEESE = (245, 158, 11)      # Cyber Amber Gold
COLOR_RADAR = (139, 92, 246)       # Plasma Purple

# Hambatan Lingkungan (Hazards)
COLOR_CHASM = (31, 29, 43)         # Deep Pit Abyss
COLOR_CHASM_BORDER = (239, 68, 68) # Warning Red
COLOR_FIRE = (249, 115, 22)        # Lava Orange

# Teks UI
COLOR_TEXT = (243, 244, 246)
COLOR_MUTED = (107, 114, 128)

# Balancing System & Aturan Power-up
POWERUP_CONFIG = {
    "CHEESE": {
        "duration": 3,
        "movement_bonus": 1,
        "ai_penalty": 1        # Mengurangi depth search Tom sebesar 1 tingkat (Handicap)
    },
    "RADAR": {
        "duration": 2,
        "radius": 7,           # Membuka Fog of War lokal sebesar 7x7 grid area
        "ai_awareness": True   # Tom mengetahui posisi Jerry secara instan saat aktif
    }
}