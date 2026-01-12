import pygame
import random
import time

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
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
