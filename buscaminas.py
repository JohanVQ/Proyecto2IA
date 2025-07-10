import pygame
import random
import time
import sys
import copy

pygame.init()

CELL_SIZE = 30
MARGIN = 5
MENU_HEIGHT = 0 
INFO_HEIGHT = 100 
BUTTON_HEIGHT = 45
BUTTON_WIDTH = 300

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
NAVY = (0, 0, 128)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

NUMBER_COLORS = {
    1: BLUE,
    2: GREEN,
    3: RED,
    4: PURPLE,
    5: BROWN,
    6: (0, 255, 255),
    7: BLACK,
    8: GRAY
}

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Sentence():

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def identified_mines(self):
        if self.count == len(self.cells):
            return self.cells.copy()
        return set()

    def identified_safes(self):
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_cell_as_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_cell_as_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width

        self.moves_made = set()

        self.mines = set()
        self.safes = set()

        self.knowledge = []

    def mark_cell_as_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_cell_as_mine(cell)

    def mark_cell_as_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_cell_as_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)

        self.mark_cell_as_safe(cell)

        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))

        cells = set()
        count_cpy = copy.deepcopy(count)

        for cl in neighbors:
            if cl in self.mines:
                count_cpy -= 1
            if cl not in self.mines | self.safes:
                cells.add(cl)

        new_sentence = Sentence(cells, count_cpy)
        if new_sentence not in self.knowledge and len(new_sentence.cells) > 0:
            self.knowledge.append(new_sentence)

        self.update_knowledge()

        self.create_derived_sentences()

    def create_derived_sentences(self):
        new_sentences = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 and s1.cells and s2.cells:
                    if s1.cells.issubset(s2.cells):
                        new_cells = s2.cells - s1.cells
                        new_count = s2.count - s1.count
                        if new_cells and new_count >= 0:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge:
                                new_sentences.append(new_sentence)

        self.knowledge.extend(new_sentences)

        self.update_knowledge()

    def update_knowledge(self):
        changed = True
        while changed:
            changed = False

            identified_mines = set()
            identified_safes = set()

            for sentence in self.knowledge:
                identified_mines |= sentence.identified_mines()
                identified_safes |= sentence.identified_safes()

            for mine in identified_mines:
                if mine not in self.mines:
                    self.mark_cell_as_mine(mine)
                    changed = True

            for safe in identified_safes:
                if safe not in self.safes:
                    self.mark_cell_as_safe(safe)
                    changed = True

            self.knowledge = [s for s in self.knowledge if s.cells]

    def get_next_safe_move(self):
        for move in self.safes - self.moves_made:
            return move
        return None

    def select_random_available_cell(self):
        options = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        if options:
            return random.choice(options)
        return None

class Minesweeper:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 28)  
        self.small_font = pygame.font.Font(None, 20)  

        self.ai = None
        self.ai_mode = False
        self.ai_speed = 1.0
        self.last_ai_move_time = 0
        self.ai_thinking = False
        
        self.show_menu = True
        self.custom_mode = False
        self.custom_rows = 9
        self.custom_cols = 9
        self.custom_mines = 10
        self.input_active = None
        self.selected_difficulty = 0
        
        self.reset_game()
        
    def reset_game(self):
        self.rows = 9
        self.cols = 9
        self.total_mines = 10
        self.grid = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.mines_flagged = 0
        self.cells_revealed = 0
        self.create_empty_grid()
        
        if self.ai:
            self.ai = MinesweeperAI(self.rows, self.cols)
        
    def create_empty_grid(self):
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        
    def create_game_grid(self):
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        
    def place_mines(self, first_click_row, first_click_col):
        mines_placed = 0
        while mines_placed < self.total_mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            if (row == first_click_row and col == first_click_col) or self.grid[row][col].is_mine:
                continue
                
            self.grid[row][col].is_mine = True
            mines_placed += 1
            
        self.calculate_adjacent_mines()
        
    def calculate_adjacent_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.grid[row][col].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            new_row, new_col = row + dr, col + dc
                            if (0 <= new_row < self.rows and 0 <= new_col < self.cols and 
                                self.grid[new_row][new_col].is_mine):
                                count += 1
                    self.grid[row][col].adjacent_mines = count
                    
    def reveal_cell(self, row, col):
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or 
            self.grid[row][col].is_revealed or self.grid[row][col].is_flagged):
            return
            
        self.grid[row][col].is_revealed = True
        self.cells_revealed += 1
        
        if self.ai and not self.grid[row][col].is_mine:
            self.ai.add_knowledge((row, col), self.grid[row][col].adjacent_mines)
        
        if self.grid[row][col].is_mine:
            self.game_over = True
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.grid[r][c].is_mine:
                        self.grid[r][c].is_revealed = True
            return
            
        if self.grid[row][col].adjacent_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal_cell(row + dr, col + dc)
                    
    def toggle_flag(self, row, col):
        if self.grid[row][col].is_revealed:
            return
            
        if self.grid[row][col].is_flagged:
            self.grid[row][col].is_flagged = False
            self.mines_flagged -= 1
        else:
            self.grid[row][col].is_flagged = True
            self.mines_flagged += 1
            
    def check_win(self):
        cells_to_reveal = self.rows * self.cols - self.total_mines
        if self.cells_revealed >= cells_to_reveal:
            self.game_won = True
            
    def handle_click(self, pos, right_click=False):
        if self.show_menu:
            return
            
        if self.ai_mode:
            return
            
        game_start_y = MENU_HEIGHT + INFO_HEIGHT + 10  
        game_start_x = (pygame.display.get_surface().get_width() - (self.cols * (CELL_SIZE + 1) - 1)) // 2
        
        if (pos[1] < game_start_y or pos[0] < game_start_x):
            return
            
        adjusted_x = pos[0] - game_start_x
        adjusted_y = pos[1] - game_start_y
        
        grid_width = self.cols * (CELL_SIZE + 1) - 1
        grid_height = self.rows * (CELL_SIZE + 1) - 1
        
        if adjusted_x < 0 or adjusted_x >= grid_width or adjusted_y < 0 or adjusted_y >= grid_height:
            return
            
        col = adjusted_x // (CELL_SIZE + 1)
        row = adjusted_y // (CELL_SIZE + 1)
        
        if row >= self.rows or col >= self.cols or row < 0 or col < 0 or self.game_over or self.game_won:
            return
            
        if right_click:
            self.toggle_flag(row, col)
        else:
            if self.first_click:
                self.create_game_grid()
                self.place_mines(row, col)
                self.first_click = False
                self.start_time = time.time()
                
            self.reveal_cell(row, col)
            
        self.check_win()
        
    def ai_make_move(self):
        if not self.ai or self.game_over or self.game_won:
            return
            
        current_time = time.time()
        
        if current_time - self.last_ai_move_time < (1.0 / self.ai_speed):
            return
            
        self.ai_thinking = True
        
        if self.first_click:
            row, col = self.rows // 2, self.cols // 2
            self.create_game_grid()
            self.place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()
            self.reveal_cell(row, col)
            self.last_ai_move_time = current_time
            self.ai_thinking = False
            return
            
        safe_move = self.ai.get_next_safe_move()
        if safe_move:
            row, col = safe_move
            self.reveal_cell(row, col)
        else:
            random_move = self.ai.select_random_available_cell()
            if random_move:
                row, col = random_move
                self.reveal_cell(row, col)
            else:
                self.ai_thinking = False
                return
                
        for mine_pos in self.ai.mines:
            mine_row, mine_col = mine_pos
            if (0 <= mine_row < self.rows and 0 <= mine_col < self.cols and 
                not self.grid[mine_row][mine_col].is_revealed):
                self.grid[mine_row][mine_col].is_flagged = True
                
        self.check_win()
        self.last_ai_move_time = current_time
        self.ai_thinking = False
        
    def toggle_ai_mode(self):
        self.ai_mode = not self.ai_mode
        if self.ai_mode:
            self.ai = MinesweeperAI(self.rows, self.cols)
        else:
            self.ai = None
            
    def draw_menu(self, screen):
        screen.fill(LIGHT_BLUE)
        
        title_shadow = self.title_font.render("BUSCAMINAS", True, DARK_GRAY)
        title = self.title_font.render("BUSCAMINAS", True, BLACK)
        title_rect = title.get_rect(center=(screen.get_width()//2, 50))
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title, title_rect)
        
        button_y = 120
        button_spacing = 60
        buttons = [
            ("Principiante (9×9, 10 minas)", self.set_beginner),
            ("Intermedio (16×16, 40 minas)", self.set_intermediate),
            ("Difícil (16×30, 99 minas)", self.set_expert),
            ("Personalizado", self.toggle_custom_mode)
        ]
        
        button_rects = []
        for i, (text, _) in enumerate(buttons):
            button_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            button_rect.center = (screen.get_width()//2, button_y + i * button_spacing)
            button_rects.append(button_rect)
            
            if i == self.selected_difficulty:
                color = YELLOW
                border_color = ORANGE
                border_width = 4
            elif i == 3 and self.custom_mode:
                color = LIGHT_GREEN
                border_color = GREEN
                border_width = 3
            else:
                color = WHITE
                border_color = BLACK
                border_width = 2
                
            shadow_rect = button_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, GRAY, shadow_rect)
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, border_width)
            
            text_surface = self.button_font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
            
        if self.custom_mode:
            custom_y = button_y + 4 * button_spacing + 20
            
            panel_rect = pygame.Rect(0, 0, 400, 150)
            panel_rect.center = (screen.get_width()//2, custom_y + 75)
            pygame.draw.rect(screen, WHITE, panel_rect)
            pygame.draw.rect(screen, BLACK, panel_rect, 3)
            
            panel_title = self.font.render("Configuración Personalizada", True, BLACK)
            title_rect = panel_title.get_rect(center=(panel_rect.centerx, panel_rect.y + 20))
            screen.blit(panel_title, title_rect)
            
            fields = [
                ("Filas (2-30):", self.custom_rows, "rows"),
                ("Columnas (2-30):", self.custom_cols, "cols"),
                ("Minas (1-{}):", self.custom_mines, "mines")
            ]
            
            for i, (label, value, field_type) in enumerate(fields):
                y_pos = panel_rect.y + 50 + i * 35
                
                if field_type == "mines":
                    max_mines = (self.custom_rows * self.custom_cols) - 1
                    label = label.format(max_mines)
                    
                label_surface = self.font.render(label, True, BLACK)
                screen.blit(label_surface, (panel_rect.x + 20, y_pos))
                
                input_rect = pygame.Rect(panel_rect.x + 200, y_pos - 2, 80, 30)
                
                if self.input_active == field_type:
                    color = YELLOW
                    border_color = ORANGE
                    border_width = 3
                else:
                    color = WHITE
                    border_color = BLACK
                    border_width = 2
                    
                pygame.draw.rect(screen, color, input_rect)
                pygame.draw.rect(screen, border_color, input_rect, border_width)
                
                value_surface = self.font.render(str(value), True, BLACK)
                value_rect = value_surface.get_rect(center=input_rect.center)
                screen.blit(value_surface, value_rect)
            
        start_y = screen.get_height() - 80
        start_button = pygame.Rect(0, 0, 200, 50)
        start_button.center = (screen.get_width()//2, start_y)
        
        shadow_rect = start_button.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect)
        
        pygame.draw.rect(screen, GREEN, start_button)
        pygame.draw.rect(screen, BLACK, start_button, 3)
        
        start_text = self.button_font.render("INICIAR JUEGO", True, BLACK)
        start_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_rect)
        
        return button_rects, start_button
        
    def set_beginner(self):
        self.rows, self.cols, self.total_mines = 9, 9, 10
        self.selected_difficulty = 0
        
    def set_intermediate(self):
        self.rows, self.cols, self.total_mines = 16, 16, 40
        self.selected_difficulty = 1
        
    def set_expert(self):
        self.rows, self.cols, self.total_mines = 16, 30, 99
        self.selected_difficulty = 2
        
    def toggle_custom_mode(self):
        self.custom_mode = not self.custom_mode
        if self.custom_mode:
            self.selected_difficulty = 3
        
    def apply_custom_settings(self):
        self.rows = max(2, min(30, self.custom_rows))
        self.cols = max(2, min(30, self.custom_cols))
        max_mines = (self.rows * self.cols) - 1
        self.total_mines = max(1, min(max_mines, self.custom_mines))
        
        self.custom_rows = self.rows
        self.custom_cols = self.cols
        self.custom_mines = self.total_mines
        
    def draw_info(self, screen):
        if self.start_time and not self.game_over and not self.game_won:
            self.elapsed_time = int(time.time() - self.start_time)
            
        info_rect = pygame.Rect(0, MENU_HEIGHT, screen.get_width(), INFO_HEIGHT)
        
        for y in range(INFO_HEIGHT):
            alpha = int(255 * (1 - y / INFO_HEIGHT * 0.3))
            color = (alpha, alpha, min(255, alpha + 20))
            pygame.draw.line(screen, color, (0, MENU_HEIGHT + y), (screen.get_width(), MENU_HEIGHT + y))
        
        pygame.draw.rect(screen, BLACK, info_rect, 3)
        pygame.draw.line(screen, WHITE, (5, MENU_HEIGHT + 5), (screen.get_width() - 5, MENU_HEIGHT + 5), 2)
        
        panel_width = screen.get_width()
        section_width = panel_width // 3
        
        left_x = 15
        info_y = MENU_HEIGHT + 10
        
        mines_left = self.total_mines - self.mines_flagged
        mines_color = RED if mines_left < 0 else (ORANGE if mines_left <= 3 else BLACK)
        mines_text = f"Minas: {mines_left}"
        mines_surface = self.info_font.render(mines_text, True, mines_color)
        screen.blit(mines_surface, (left_x, info_y))
        
        total_cells = self.rows * self.cols - self.total_mines
        progress = (self.cells_revealed / total_cells) * 100 if total_cells > 0 else 0
        progress_text = f"Progreso: {progress:.1f}%"
        progress_surface = self.font.render(progress_text, True, BLACK)
        screen.blit(progress_surface, (left_x, info_y + 25))
        
        bar_rect = pygame.Rect(left_x, info_y + 45, section_width - 30, 12)
        pygame.draw.rect(screen, WHITE, bar_rect)
        pygame.draw.rect(screen, BLACK, bar_rect, 2)
        if progress > 0:
            fill_width = int((bar_rect.width - 4) * progress / 100)
            fill_rect = pygame.Rect(bar_rect.x + 2, bar_rect.y + 2, fill_width, bar_rect.height - 4)
            bar_color = GREEN if progress > 75 else (YELLOW if progress > 50 else LIGHT_BLUE)
            pygame.draw.rect(screen, bar_color, fill_rect)
        
        revealed_text = f"Reveladas: {self.cells_revealed}/{total_cells}"
        revealed_surface = self.small_font.render(revealed_text, True, BLACK)
        screen.blit(revealed_surface, (left_x, info_y + 65))
        
        center_x = section_width
        
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        time_text = f"Tiempo: {minutes:02d}:{seconds:02d}"
        time_surface = self.info_font.render(time_text, True, BLACK)
        time_rect = time_surface.get_rect()
        time_rect.centerx = center_x + section_width // 2
        time_rect.y = info_y
        screen.blit(time_surface, time_rect)
        
        if self.ai_mode:
            if self.ai_thinking:
                status_text = "IA analizando..."
                color = ORANGE
            elif self.game_over:
                status_text = "IA perdió"
                color = RED
            elif self.game_won:
                status_text = "¡IA victoriosa!"
                color = GREEN
            else:
                status_text = "IA en acción"
                color = BLUE
        else:
            if self.game_over:
                status_text = "¡DERROTA!"
                color = RED
            elif self.game_won:
                status_text = "¡VICTORIA!"
                color = GREEN
            else:
                status_text = "Jugando..."
                color = BLUE
            
        status_surface = self.info_font.render(status_text, True, color)
        status_rect = status_surface.get_rect()
        status_rect.centerx = center_x + section_width // 2
        status_rect.y = info_y + 25
        screen.blit(status_surface, status_rect)
        
        right_x = section_width * 2
        button_width = 80
        button_height = 30
        button_spacing = 5
        
        menu_button = pygame.Rect(right_x + 10, info_y, button_width, button_height)
        self.draw_gradient_button(screen, menu_button, "MENÚ", ORANGE, BLACK)
        
        restart_button = pygame.Rect(right_x + 10, info_y + button_height + button_spacing, button_width, button_height)
        self.draw_gradient_button(screen, restart_button, "RESET", LIGHT_GREEN, BLACK)
        
        ai_button = pygame.Rect(right_x + 10 + button_width + button_spacing, info_y, button_width, button_height)
        ai_color = CYAN if self.ai_mode else LIGHT_GRAY
        self.draw_gradient_button(screen, ai_button, "IA", ai_color, BLACK)
        
        speed_buttons = []
        if self.ai_mode:
            speed_slow = pygame.Rect(right_x + 10 + button_width + button_spacing, info_y + button_height + button_spacing, 35, button_height)
            speed_fast = pygame.Rect(right_x + 50 + button_width + button_spacing, info_y + button_height + button_spacing, 35, button_height)
            
            self.draw_gradient_button(screen, speed_slow, "-", YELLOW, BLACK)
            self.draw_gradient_button(screen, speed_fast, "+", PINK, BLACK)
            
            speed_text = f"x{self.ai_speed:.1f}"
            speed_surface = self.small_font.render(speed_text, True, BLACK)
            screen.blit(speed_surface, (right_x + 10, info_y + 65))
            
            speed_buttons = [speed_slow, speed_fast]
        
        return menu_button, restart_button, ai_button, speed_buttons
        
    def draw_gradient_button(self, screen, rect, text, color, text_color):
        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect)
        
        for i in range(rect.height):
            alpha = 1 - (i / rect.height) * 0.3
            if isinstance(color, tuple) and len(color) == 3:
                gradient_color = tuple(int(c * alpha) for c in color)
            else:
                gradient_color = color
            pygame.draw.line(screen, gradient_color, 
                           (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
        
        pygame.draw.rect(screen, BLACK, rect, 2)
        
        text_surface = self.small_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        
    def draw_grid(self, screen):
        game_start_y = MENU_HEIGHT + INFO_HEIGHT + 10 
        game_start_x = (screen.get_width() - (self.cols * (CELL_SIZE + 1) - 1)) // 2
        
        board_rect = pygame.Rect(game_start_x - 10, game_start_y - 10, 
                                self.cols * (CELL_SIZE + 1) + 19, 
                                self.rows * (CELL_SIZE + 1) + 19)
        shadow_rect = board_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect)
        pygame.draw.rect(screen, WHITE, board_rect)
        pygame.draw.rect(screen, BLACK, board_rect, 3)
        
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                x = game_start_x + col * (CELL_SIZE + 1)
                y = game_start_y + row * (CELL_SIZE + 1)
                
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                if cell.is_revealed:
                    if cell.is_mine:
                        if self.game_over:
                            pygame.draw.rect(screen, RED, rect)
                            pygame.draw.circle(screen, YELLOW, rect.center, CELL_SIZE//4)
                        else:
                            pygame.draw.rect(screen, WHITE, rect)
                        pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE//3)
                        pygame.draw.circle(screen, WHITE, (rect.centerx - 3, rect.centery - 3), 3)
                    else:
                        pygame.draw.rect(screen, WHITE, rect)
                        if cell.adjacent_mines > 0:
                            color = NUMBER_COLORS.get(cell.adjacent_mines, BLACK)
                            number = self.font.render(str(cell.adjacent_mines), True, color)
                            number_rect = number.get_rect(center=rect.center)
                            screen.blit(number, number_rect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                    pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE - 1, y), 2)
                    pygame.draw.line(screen, WHITE, (x, y), (x, y + CELL_SIZE - 1), 2)
                    pygame.draw.line(screen, DARK_GRAY, (x + CELL_SIZE - 1, y), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 2)
                    pygame.draw.line(screen, DARK_GRAY, (x, y + CELL_SIZE - 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 2)
                    
                    if cell.is_flagged:
                        flag_points = [
                            (x + CELL_SIZE//4, y + CELL_SIZE//6),
                            (x + 3*CELL_SIZE//4, y + CELL_SIZE//3),
                            (x + 3*CELL_SIZE//4, y + 2*CELL_SIZE//3),
                            (x + CELL_SIZE//4, y + CELL_SIZE//2)
                        ]
                        pygame.draw.polygon(screen, RED, flag_points)
                        pygame.draw.line(screen, BLACK, 
                                       (x + CELL_SIZE//4, y + CELL_SIZE//6), 
                                       (x + CELL_SIZE//4, y + 5*CELL_SIZE//6), 3)
                        
                pygame.draw.rect(screen, BLACK, rect, 1)
        
        if self.ai_mode and self.ai:
            ai_info_y = game_start_y + self.rows * (CELL_SIZE + 1) + 20
            
            ai_panel_height = 50
            ai_panel = pygame.Rect(game_start_x, ai_info_y, 
                                  self.cols * (CELL_SIZE + 1) - 1, ai_panel_height)
            pygame.draw.rect(screen, (240, 248, 255), ai_panel)  
            pygame.draw.rect(screen, BLUE, ai_panel, 2)
            
            safe_count = len(self.ai.safes - self.ai.moves_made)
            mine_count = len(self.ai.mines)
            knowledge_count = len(self.ai.knowledge)
            
            ai_info = f"IA: {safe_count} seguras | {mine_count} minas | {knowledge_count} reglas"
            ai_info_surface = self.small_font.render(ai_info, True, NAVY)
            screen.blit(ai_info_surface, (ai_panel.x + 10, ai_panel.y + 8))
            
            # Velocidad y estado
            status_info = f"Velocidad: {self.ai_speed:.1f}x | Estado: {'Pensando...' if self.ai_thinking else 'Activa'}"
            status_surface = self.small_font.render(status_info, True, NAVY)
            screen.blit(status_surface, (ai_panel.x + 10, ai_panel.y + 25))
                
    def restart_game(self):
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.mines_flagged = 0
        self.cells_revealed = 0
        self.create_empty_grid()
        
        # Reset AI
        if self.ai:
            self.ai = MinesweeperAI(self.rows, self.cols)
                
    def handle_menu_click(self, pos, button_rects, start_button):
        for i, rect in enumerate(button_rects):
            if rect.collidepoint(pos):
                if i == 0:
                    self.set_beginner()
                elif i == 1:
                    self.set_intermediate()
                elif i == 2:
                    self.set_expert()
                elif i == 3:
                    self.toggle_custom_mode()
                return
                
        if start_button.collidepoint(pos):
            if self.custom_mode:
                self.apply_custom_settings()
            self.show_menu = False
            self.reset_game_state()
            if self.ai_mode:
                self.ai = MinesweeperAI(self.rows, self.cols)
            return
            
        if self.custom_mode:
            screen_width = pygame.display.get_surface().get_width()
            custom_y = 120 + 4 * 60 + 20 + 50
            
            for i, field_type in enumerate(["rows", "cols", "mines"]):
                input_rect = pygame.Rect(screen_width//2 - 200 + 200, custom_y + i * 35 - 2, 80, 30)
                if input_rect.collidepoint(pos):
                    self.input_active = field_type
                    return
                    
        self.input_active = None
        
    def handle_key_input(self, event):
        if not self.custom_mode or not self.input_active:
            return
            
        if event.key == pygame.K_BACKSPACE:
            if self.input_active == "rows" and self.custom_rows > 0:
                self.custom_rows = self.custom_rows // 10
            elif self.input_active == "cols" and self.custom_cols > 0:
                self.custom_cols = self.custom_cols // 10
            elif self.input_active == "mines" and self.custom_mines > 0:
                self.custom_mines = self.custom_mines // 10
        elif event.unicode.isdigit():
            digit = int(event.unicode)
            if self.input_active == "rows":
                new_value = self.custom_rows * 10 + digit
                if new_value <= 30:
                    self.custom_rows = new_value
            elif self.input_active == "cols":
                new_value = self.custom_cols * 10 + digit
                if new_value <= 30:
                    self.custom_cols = new_value
            elif self.input_active == "mines":
                max_mines = (max(2, self.custom_rows) * max(2, self.custom_cols)) - 1
                new_value = self.custom_mines * 10 + digit
                if new_value <= max_mines:
                    self.custom_mines = max(1, new_value)

                    
    def reset_game_state(self):
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.mines_flagged = 0
        self.cells_revealed = 0
        self.create_empty_grid()
        
    def calculate_window_size(self):
        min_width = 800
        min_height = 600
        
        board_width = self.cols * (CELL_SIZE + 1) + 100 
        board_height = self.rows * (CELL_SIZE + 1) + MENU_HEIGHT + INFO_HEIGHT + 120
        
        if self.ai_mode:
            board_height += 70
        
        window_width = max(min_width, board_width)
        window_height = max(min_height, board_height)
        
        return window_width, window_height
        
    def run(self):
        screen_width = 900
        screen_height = 700
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Buscaminas Pro con IA")
        clock = pygame.time.Clock()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_menu:
                        button_rects, start_button = self.draw_menu(screen)
                        self.handle_menu_click(event.pos, button_rects, start_button)
                    else:
                        menu_button, restart_button, ai_button, speed_buttons = self.draw_info(screen)
                        if menu_button.collidepoint(event.pos):
                            self.show_menu = True
                            screen = pygame.display.set_mode((900, 700))
                        elif restart_button.collidepoint(event.pos):
                            self.restart_game()
                        elif ai_button.collidepoint(event.pos):
                            self.toggle_ai_mode()
                        elif speed_buttons and len(speed_buttons) >= 2:
                            if speed_buttons[0].collidepoint(event.pos):  
                                self.ai_speed = max(0.1, self.ai_speed - 0.5)
                            elif speed_buttons[1].collidepoint(event.pos):  
                                self.ai_speed = min(5.0, self.ai_speed + 0.5)
                        else:
                            right_click = event.button == 3
                            self.handle_click(event.pos, right_click)
                            
                elif event.type == pygame.KEYDOWN:
                    if self.show_menu:
                        self.handle_key_input(event)
                    elif event.key == pygame.K_r:  
                        self.restart_game()
                    elif event.key == pygame.K_m:
                        self.show_menu = True
                        screen = pygame.display.set_mode((900, 700))
                        self.toggle_ai_mode()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: 
                        self.ai_speed = min(5.0, self.ai_speed + 0.5)
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:  
                        self.ai_speed = max(0.1, self.ai_speed - 0.5)
                        
            if self.ai_mode and not self.show_menu:
                self.ai_make_move()
                    
            if self.show_menu:
                button_rects, start_button = self.draw_menu(screen)
            else:
                needed_width, needed_height = self.calculate_window_size()
                current_size = (screen.get_width(), screen.get_height())
                needed_size = (needed_width, needed_height)
                
                if current_size != needed_size:
                    screen = pygame.display.set_mode(needed_size)
                    
                for y in range(screen.get_height()):
                    progress = y / screen.get_height()
                    color_value = int(200 + 55 * progress)
                    blue_value = int(255 - 50 * progress)
                    color = (color_value, color_value, blue_value)
                    pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))
                
                menu_button, restart_button, ai_button, speed_buttons = self.draw_info(screen)
                self.draw_grid(screen)
                    
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()