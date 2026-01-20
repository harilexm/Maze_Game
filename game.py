import pygame
import random
import time
import sys
from collections import deque

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
HUD_HEIGHT = 80  
MAZE_AREA_HEIGHT = WINDOW_HEIGHT - HUD_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 149, 237)
BUTTON_DANGER = (200, 60, 60) 

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Directions for maze carving (right, down, left, up)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Configuration
DIFFICULTY_SETTINGS = {
    'EASY':   {'rows': 15, 'cols': 15, 'seeds': 4,  'growth': 0, 'buffer': 3.0}, 
    'MEDIUM': {'rows': 21, 'cols': 21, 'seeds': 8,  'growth': 1, 'buffer': 6.0}, 
    'HARD':   {'rows': 31, 'cols': 31, 'seeds': 15, 'growth': 2, 'buffer': 12.0}
}

# PALETTES VISIBILITY 
PALETTES = [
    # Classic: Black Walls, White Path, Gold Seeds
    {'bg': BLACK, 'wall': (20, 20, 20), 'path': WHITE, 'player': GREEN, 'seed': GOLD},
    
    # Neon/Purple: Dark Indigo Walls, Light Cyan Path, HOT PINK Seeds
    {'bg': (20, 0, 30), 'wall': (75, 0, 130), 'path': (220, 255, 255), 'player': (255, 255, 0), 'seed': (255, 20, 147)},
    
    # Desert: Dark Brown Walls, Sand Path, Deep Red Seeds
    {'bg': (50, 20, 0), 'wall': (80, 40, 0), 'path': (255, 230, 200), 'player': BLUE, 'seed': (200, 0, 0)},
]

class Button:
    def __init__(self, text, x, y, width, height, action_key, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_key = action_key
        self.default_color = color
        self.is_hovered = False

    def draw(self, screen, font):
        if self.is_hovered:
            r = min(255, self.default_color[0] + 30)
            g = min(255, self.default_color[1] + 30)
            b = min(255, self.default_color[2] + 30)
            color = (r, g, b)
        else:
            color = self.default_color
            
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def generate_maze(rows, cols, difficulty):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    def carve(cx, cy):
        maze[cy][cx] = 0
        dirs = DIRECTIONS[:]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[cy + dy][cx + dx] = 0
                maze[ny][nx] = 0
                carve(nx, ny)
    carve(0, 0)
    maze[rows-1][cols-1] = 0 
    if difficulty in ['MEDIUM', 'HARD']:
        loops_to_add = (rows * cols) // 10
        for _ in range(loops_to_add):
            rx = random.randint(1, cols - 2)
            ry = random.randint(1, rows - 2)
            if maze[ry][rx] == 1:
                neighbors = 0
                for dx, dy in DIRECTIONS:
                    if maze[ry+dy][rx+dx] == 0:
                        neighbors += 1
                if neighbors >= 2:
                    maze[ry][rx] = 0
    return maze

def get_shortest_path_time(maze, start_pos, end_pos):
    rows = len(maze)
    cols = len(maze[0])
    queue = deque([(start_pos, 0)]) 
    visited = set()
    visited.add(start_pos)
    found = False
    steps = 0
    
    while queue:
        (cx, cy), s = queue.popleft()
        if (cx, cy) == end_pos:
            steps = s
            found = True
            break  
        for dx, dy in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), s + 1))
    
    if not found: return 10 
    return steps / 3.5

def find_start_node(maze, rows, cols, difficulty):
    candidates = []
    limit_y = max(2, int(rows * 0.4))
    limit_x = max(2, int(cols * 0.4))
    for y in range(0, limit_y):
        for x in range(0, limit_x):
            if maze[y][x] == 0:
                ways = 0
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                        ways += 1
                if difficulty == 'EASY' and ways >= 3:
                    candidates.append((x, y))
                elif difficulty != 'EASY' and ways >= 3:
                    if ways == 4: candidates.insert(0, (x,y)) 
                    else: candidates.append((x, y))
    if candidates: return candidates[0]
    return (0, 0)


def spawn_seeds(maze, rows, cols, count, player_pos, end_pos):
    seeds = []
    attempts = 0
    while len(seeds) < count and attempts < 1000:
        attempts += 1
        rx = random.randint(0, cols - 1)
        ry = random.randint(0, rows - 1)
        if maze[ry][rx] == 0 and (rx, ry) != player_pos and (rx, ry) != end_pos:
            if (rx, ry) not in seeds:
                seeds.append((rx, ry))
    return seeds

def menu_screen(screen):
    font_title = pygame.font.Font(None, 80)
    font_btn = pygame.font.Font(None, 50)
    
    btn_easy = Button("EASY", 250, 300, 300, 80, 'EASY')
    btn_med = Button("MEDIUM", 250, 400, 300, 80, 'MEDIUM')
    btn_hard = Button("HARD", 250, 500, 300, 80, 'HARD')
    buttons = [btn_easy, btn_med, btn_hard]

    while True:
        screen.fill((20, 20, 30))
        title = font_title.render("MAZE RUNNER", True, GREEN)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen, font_btn)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn.is_clicked(mouse_pos):
                            return btn.action_key
        pygame.display.flip()

def game_over_screen(screen, final_score):
    font_title = pygame.font.Font(None, 80)
    font_sub = pygame.font.Font(None, 50)
    font_btn = pygame.font.Font(None, 40)
    
    btn_retry = Button("Retry Level", 200, 350, 400, 60, 'RETRY')
    btn_restart = Button("Restart Game", 200, 430, 400, 60, 'RESTART')
    btn_menu = Button("Main Menu", 200, 510, 400, 60, 'MENU')
    btn_quit = Button("Quit", 200, 590, 400, 60, 'QUIT', color=BUTTON_DANGER)
    
    buttons = [btn_retry, btn_restart, btn_menu, btn_quit]

    while True:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(10) 
        screen.blit(overlay, (0,0))
        
        pygame.draw.rect(screen, (30, 30, 40), (100, 100, 600, 600), border_radius=20)
        pygame.draw.rect(screen, WHITE, (100, 100, 600, 600), 3, border_radius=20)
        
        txt_go = font_title.render("GAME OVER", True, RED)
        txt_sc = font_sub.render(f"Final Score: {final_score}", True, WHITE)
        
        screen.blit(txt_go, (WINDOW_WIDTH//2 - txt_go.get_width()//2, 150))
        screen.blit(txt_sc, (WINDOW_WIDTH//2 - txt_sc.get_width()//2, 230))
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen, font_btn)
            
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn.is_clicked(mouse_pos):
                            return btn.action_key

def draw_hud(screen, font, time_left, score, level, difficulty):
    pygame.draw.rect(screen, (40, 44, 52), (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, WHITE, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT), 3)
    
    lbl_mode = font.render(f"{difficulty}", True, (100, 200, 255))
    lbl_level = font.render(f"Lvl: {level + 1}", True, WHITE)
    time_str = f"{time_left:.1f}s" if time_left < 10 else f"{int(time_left)}s"
    lbl_time = font.render(f"Time: {time_str}", True, RED if time_left < 5 else GREEN)
    lbl_score = font.render(f"Score: {score}", True, GOLD)

    screen.blit(lbl_mode, (20, 25))
    screen.blit(lbl_level, (200, 25))
    screen.blit(lbl_time, (400, 25))
    screen.blit(lbl_score, (600, 25))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ultimate Maze Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)
    
    pygame.key.set_repeat(200, 100) 

    app_running = True
    
    while app_running:
        difficulty_key = menu_screen(screen)
        settings = DIFFICULTY_SETTINGS[difficulty_key]

        current_rows = settings['rows']
        current_cols = settings['cols']
        score = 0
        level = 0
        
        game_active = True
        
        while game_active:
            # SAVE STATE
            saved_score = score
            saved_rows = current_rows
            saved_cols = current_cols
            
            maze = generate_maze(current_rows, current_cols, difficulty_key)
            start_pos = find_start_node(maze, current_rows, current_cols, difficulty_key)
            end_pos = (current_cols - 1, current_rows - 1)
            px, py = start_pos
            
            base_time = get_shortest_path_time(maze, start_pos, end_pos)
            max_buffer = settings['buffer']
            reduction = level * 0.07
            current_buffer = max(0, max_buffer - reduction)
            current_time_limit = base_time + current_buffer
            
            seeds = spawn_seeds(maze, current_rows, current_cols, settings['seeds'], start_pos, end_pos)
            
            cell_w = WINDOW_WIDTH // current_cols
            cell_h = MAZE_AREA_HEIGHT // current_rows
            CELL_SIZE = min(cell_w, cell_h)
            
            draw_offset_x = (WINDOW_WIDTH - (current_cols * CELL_SIZE)) // 2
            draw_offset_y = HUD_HEIGHT + (MAZE_AREA_HEIGHT - (current_rows * CELL_SIZE)) // 2
            
            palette = PALETTES[(level // 5) % len(PALETTES)]
            start_ticks = pygame.time.get_ticks()
            
            level_result = None 
            
            while level_result is None:
                elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
                time_left = current_time_limit - elapsed
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        level_result = 'QUIT'
                    elif event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0
                        if event.key == pygame.K_UP: dy = -1
                        elif event.key == pygame.K_DOWN: dy = 1
                        elif event.key == pygame.K_LEFT: dx = -1
                        elif event.key == pygame.K_RIGHT: dx = 1
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < current_cols and 0 <= ny < current_rows and maze[ny][nx] == 0:
                            px, py = nx, ny

                if (px, py) in seeds:
                    seeds.remove((px, py))
                    score += 10 * (level + 1)
                if (px, py) == end_pos:
                    level_result = 'WIN'
                    score += int(time_left * 10)
                if time_left <= 0:
                    level_result = 'LOSE'

                screen.fill(palette['bg'])
                draw_hud(screen, font, max(0, time_left), score, level, difficulty_key)
                
                actual_rows = len(maze)
                actual_cols = len(maze[0])
                for r in range(actual_rows):
                    for c in range(actual_cols):
                        rect = (draw_offset_x + c * CELL_SIZE, 
                                draw_offset_y + r * CELL_SIZE, 
                                CELL_SIZE + 1, CELL_SIZE + 1)
                        color = palette['path'] if maze[r][c] == 0 else palette['wall']
                        pygame.draw.rect(screen, color, rect)

                for sx, sy in seeds:
                    cx = draw_offset_x + sx * CELL_SIZE + CELL_SIZE // 2
                    cy = draw_offset_y + sy * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(screen, palette['seed'], (cx, cy), CELL_SIZE // 4)

                ex = draw_offset_x + end_pos[0] * CELL_SIZE
                ey = draw_offset_y + end_pos[1] * CELL_SIZE
                pygame.draw.rect(screen, RED, (ex, ey, CELL_SIZE, CELL_SIZE))
                
                plx = draw_offset_x + px * CELL_SIZE + 2
                ply = draw_offset_y + py * CELL_SIZE + 2
                pygame.draw.rect(screen, palette['player'], (plx, ply, CELL_SIZE - 4, CELL_SIZE - 4))

                pygame.display.flip()
                clock.tick(30)
                
            if level_result == 'QUIT':
                game_active = False
                app_running = False
                
            elif level_result == 'WIN':
                level += 1
                current_rows += settings['growth']
                current_cols += settings['growth']
                msg_font = pygame.font.Font(None, 60)
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                screen.blit(overlay, (0,0))
                text = msg_font.render("Level Complete!", True, GREEN)
                screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2))
                pygame.display.flip()
                pygame.time.delay(1000)
                
            elif level_result == 'LOSE':
                action = game_over_screen(screen, score)
                if action == 'RETRY':
                    score = saved_score
                    current_rows = saved_rows
                    current_cols = saved_cols
                elif action == 'RESTART':
                    current_rows = settings['rows']
                    current_cols = settings['cols']
                    score = 0
                    level = 0
                elif action == 'MENU':
                    game_active = False
                elif action == 'QUIT':
                    game_active = False
                    app_running = False

    pygame.quit()

if __name__ == "__main__":
    main()