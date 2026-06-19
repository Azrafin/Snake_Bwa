# # entities.py
# import random
# from collections import deque
# from constants import POWERUP_CONFIG
# from algorithms import get_valid_neighbors, get_visible_cells

# class MinimaxAI:
#     """Mesin Pencarian Adversarial dengan Memoization Transposition Table"""
#     def __init__(self):
#         self.transposition_table = {}

#     def _hash_position(self, t_pos, j_pos, depth, is_max):
#         return (t_pos, j_pos, depth, is_max)

#     def run_adversarial_minimax(self, tom_pos, jerry_pos, maze, depth, map_mode, turn):
#         self.transposition_table.clear()
#         best_val = -float('inf')
#         best_move = tom_pos
#         alpha = -float('inf')
#         beta = float('inf')
        
#         moves = get_valid_neighbors(tom_pos, maze, map_mode, turn)
#         for move in moves:
#             value = self._minimax_eval(move, jerry_pos, depth - 1, alpha, beta, False, maze, map_mode, turn)
#             if value > best_val:
#                 best_val = value
#                 best_move = move
#                 alpha = max(alpha, value)
#         return best_move

#     def _minimax_eval(self, t_pos, j_pos, depth, alpha, beta, is_max, maze, map_mode, turn):
#         key = self._hash_position(t_pos, j_pos, depth, is_max)
#         if key in self.transposition_table:
#             return self.transposition_table[key]

#         if depth == 0 or t_pos == j_pos:
#             dist = abs(t_pos[0] - j_pos[0]) + abs(t_pos[1] - j_pos[1])
#             jerry_moves = len(get_valid_neighbors(j_pos, maze, map_mode, turn))
#             value = -dist * 12 - jerry_moves * 6
#             self.transposition_table[key] = value
#             return value

#         if is_max:
#             max_eval = -float('inf')
#             for move in get_valid_neighbors(t_pos, maze, map_mode, turn):
#                 ev = self._minimax_eval(move, j_pos, depth - 1, alpha, beta, False, maze, map_mode, turn)
#                 max_eval = max(max_eval, ev)
#                 alpha = max(alpha, ev)
#                 if beta <= alpha:
#                     break
#             self.transposition_table[key] = max_eval
#             return max_eval
#         else:
#             min_eval = float('inf')
#             for move in get_valid_neighbors(j_pos, maze, map_mode, turn):
#                 ev = self._minimax_eval(t_pos, move, depth - 1, alpha, beta, True, maze, map_mode, turn)
#                 min_eval = min(min_eval, ev)
#                 beta = min(beta, ev)
#                 if beta <= alpha:
#                     break
#             self.transposition_table[key] = min_eval
#             return min_eval

# class PowerUpManager:
#     """Manajer siklus aktif item durasional"""
#     def __init__(self):
#         self.active_powerups = {}

#     def apply_powerup(self, ptype):
#         config = POWERUP_CONFIG.get(ptype)
#         if config:
#             self.active_powerups[ptype] = {"remaining": config["duration"]}

#     def update(self):
#         for ptype in list(self.active_powerups.keys()):
#             self.active_powerups[ptype]["remaining"] -= 1
#             if self.active_powerups[ptype]["remaining"] <= 0:
#                 del self.active_powerups[ptype]

#     def is_active(self, ptype):
#         return ptype in self.active_powerups

#     def get_remaining(self, ptype):
#         if self.is_active(ptype):
#             return self.active_powerups[ptype]["remaining"]
#         return 0

# class AI_Agent_Tom:
#     def __init__(self, start_pos):
#         self.pos = start_pos
#         self.state = "PATROL"
#         self.last_known_jerry = None
#         self.patrol_target = None
#         self.tom_ai = MinimaxAI()

#     def update_fsm_and_move(self, jerry_pos, maze, difficulty, map_mode, turn, radar_active):
#         depth_map = {"EASY": 1, "MEDIUM": 3, "HARD": 5}
#         depth = depth_map[difficulty]
        
#         visible_cells = get_visible_cells(self.pos, 5, maze)
#         can_see_jerry = jerry_pos in visible_cells or radar_active
#         dist_manhattan = abs(self.pos[0] - jerry_pos[0]) + abs(self.pos[1] - jerry_pos[1])
#         can_hear_jerry = dist_manhattan <= 7

#         if can_see_jerry:
#             self.state = "CHASE"
#             self.last_known_jerry = jerry_pos
#         elif can_hear_jerry:
#             if self.state != "CHASE": 
#                 self.state = "SEARCH"
#             self.last_known_jerry = jerry_pos
#         elif self.state == "CHASE":
#             self.state = "SEARCH"

#         next_step = self.pos
#         if self.state == "CHASE":
#             next_step = self.tom_ai.run_adversarial_minimax(self.pos, jerry_pos, maze, depth, map_mode, turn)
#         elif self.state == "SEARCH" and self.last_known_jerry:
#             if self.pos == self.last_known_jerry:
#                 self.last_known_jerry = None
#                 self.state = "PATROL"
#             else:
#                 from algorithms import compute_bfs
#                 path = compute_bfs(self.pos, self.last_known_jerry, maze, map_mode, turn)
#                 if path: 
#                     next_step = path[0]
                
#         if self.state == "PATROL" or next_step == self.pos:
#             if not self.patrol_target or self.pos == self.patrol_target:
#                 from constants import GRID_WIDTH, GRID_HEIGHT
#                 valid_floors = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if maze[y][x] == "floor"]
#                 self.patrol_target = random.choice(valid_floors)
#             from algorithms import compute_bfs
#             path = compute_bfs(self.pos, self.patrol_target, maze, map_mode, turn)
#             if path: 
#                 next_step = path[0]

#         if next_step:
#             self.pos = next_step




import random
from collections import deque
from constants import POWERUP_CONFIG
from algorithms import get_valid_neighbors, get_visible_cells

class MinimaxAI:
    """Mesin Pencarian Adversarial dengan Memoization Transposition Table yang Akurat"""
    def __init__(self):
        self.transposition_table = {}

    def _hash_position(self, t_pos, j_pos, depth, is_max):
        return (t_pos, j_pos, depth, is_max)

    def run_adversarial_minimax(self, tom_pos, jerry_pos, maze, depth, map_mode, turn):
        self.transposition_table.clear()
        best_val = -float('inf')
        best_move = tom_pos
        alpha = -float('inf')
        beta = float('inf')
        
        # Tom melangkah di turn saat ini
        moves = get_valid_neighbors(tom_pos, maze, map_mode, turn)
        for move in moves:
            # Di kedalaman berikutnya, asumsikan turn bertambah untuk prediksi hazard dinamis
            value = self._minimax_eval(move, jerry_pos, depth - 1, alpha, beta, False, maze, map_mode, turn + 1)
            if value > best_val:
                best_val = value
                best_move = move
                alpha = max(alpha, value)
        return best_move

    def _minimax_eval(self, t_pos, j_pos, depth, alpha, beta, is_max, maze, map_mode, turn):
        key = self._hash_position(t_pos, j_pos, depth, is_max)
        
        # REVISI: Pengecekan Transposition Table dengan Validasi Alpha-Beta Bounds
        if key in self.transposition_table:
            tt_val, flag = self.transposition_table[key]
            if flag == "EXACT":
                return tt_val
            elif flag == "LOWER" and tt_val >= beta:
                return tt_val
            elif flag == "UPPER" and tt_val <= alpha:
                return tt_val

        # Base Case: Target tertangkap atau batas kedalaman tercapai
        if depth == 0 or t_pos == j_pos:
            dist = abs(t_pos[0] - j_pos[0]) + abs(t_pos[1] - j_pos[1])
            jerry_moves = len(get_valid_neighbors(j_pos, maze, map_mode, turn))
            # Heuristik: Dekati Jerry (skor tinggi jika jarak kecil) dan kurangi ruang gerak Jerry
            value = -dist * 12 - jerry_moves * 6
            self.transposition_table[key] = (value, "EXACT")
            return value

        original_alpha = alpha
        original_beta = beta

        if is_max:
            max_eval = -float('inf')
            for move in get_valid_neighbors(t_pos, maze, map_mode, turn):
                ev = self._minimax_eval(move, j_pos, depth - 1, alpha, beta, False, maze, map_mode, turn + 1)
                max_eval = max(max_eval, ev)
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break  # Beta Cutoff
            
            # REVISI: Menentukan tipe flag data yang disimpan berdasarkan kondisi cutoff
            if max_eval <= original_alpha:
                self.transposition_table[key] = (max_eval, "UPPER")
            elif max_eval >= original_beta:
                self.transposition_table[key] = (max_eval, "LOWER")
            else:
                self.transposition_table[key] = (max_eval, "EXACT")
                
            return max_eval
        else:
            min_eval = float('inf')
            for move in get_valid_neighbors(j_pos, maze, map_mode, turn):
                ev = self._minimax_eval(t_pos, move, depth - 1, alpha, beta, True, maze, map_mode, turn + 1)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alpha:
                    break  # Alpha Cutoff
            
            # REVISI: Menentukan tipe flag data untuk langkah minimalisasi (Jerry)
            if min_eval <= original_alpha:
                self.transposition_table[key] = (min_eval, "UPPER")
            elif min_eval >= original_beta:
                self.transposition_table[key] = (min_eval, "LOWER")
            else:
                self.transposition_table[key] = (min_eval, "EXACT")
                
            return min_eval

class PowerUpManager:
    """Manajer siklus aktif item durasional"""
    def __init__(self):
        self.active_powerups = {}

    def apply_powerup(self, ptype):
        config = POWERUP_CONFIG.get(ptype)
        if config:
            self.active_powerups[ptype] = {"remaining": config["duration"]}

    def update(self):
        for ptype in list(self.active_powerups.keys()):
            self.active_powerups[ptype]["remaining"] -= 1
            if self.active_powerups[ptype]["remaining"] <= 0:
                del self.active_powerups[ptype]

    def is_active(self, ptype):
        return ptype in self.active_powerups

    def get_remaining(self, ptype):
        if self.is_active(ptype):
            return self.active_powerups[ptype]["remaining"]
        return 0

class AI_Agent_Tom:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.state = "PATROL"
        self.last_known_jerry = None
        self.patrol_target = None
        self.tom_ai = MinimaxAI()

    def update_fsm_and_move(self, jerry_pos, maze, difficulty, map_mode, turn, radar_active):
        depth_map = {"EASY": 1, "MEDIUM": 3, "HARD": 5}
        depth = depth_map.get(difficulty, 3)
        
        # Pengenalan Radius Pandang dan Suara (Manhattan)
        visible_cells = get_visible_cells(self.pos, 5, maze)
        can_see_jerry = jerry_pos in visible_cells or radar_active
        dist_manhattan = abs(self.pos[0] - jerry_pos[0]) + abs(self.pos[1] - jerry_pos[1])
        can_hear_jerry = dist_manhattan <= 7

        # Transisi State FSM
        if can_see_jerry:
            self.state = "CHASE"
            self.last_known_jerry = jerry_pos
        elif can_hear_jerry:
            if self.state != "CHASE": 
                self.state = "SEARCH"
            self.last_known_jerry = jerry_pos
        elif self.state == "CHASE":
            self.state = "SEARCH"

        next_step = self.pos
        
        # Eksekusi Langkah Berdasarkan State Perilaku
        if self.state == "CHASE":
            next_step = self.tom_ai.run_adversarial_minimax(self.pos, jerry_pos, maze, depth, map_mode, turn)
        elif self.state == "SEARCH" and self.last_known_jerry:
            if self.pos == self.last_known_jerry:
                self.last_known_jerry = None
                self.state = "PATROL"
            else:
                from algorithms import compute_bfs
                path = compute_bfs(self.pos, self.last_known_jerry, maze, map_mode, turn)
                if path: 
                    next_step = path[0]
                
        # Jika dalam keadaan Patroli atau jalan buntu, cari target koordinat lantai acak baru
        if self.state == "PATROL" or next_step == self.pos:
            if not self.patrol_target or self.pos == self.patrol_target:
                from constants import GRID_WIDTH, GRID_HEIGHT
                valid_floors = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if maze[y][x] == "floor"]
                if valid_floors:
                    self.patrol_target = random.choice(valid_floors)
            
            if self.patrol_target:
                from algorithms import compute_bfs
                path = compute_bfs(self.pos, self.patrol_target, maze, map_mode, turn)
                if path: 
                    next_step = path[0]

        if next_step:
            self.pos = next_step