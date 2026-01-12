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

def generate_maze(rows, cols):
    # Create grid filled with walls (1 means wall, 0 means passage)
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def carve_passages(x, y):
        maze[y][x] = 0
        random.shuffle(DIRECTIONS)
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve_passages(nx, ny)
                
    carve_passages(0, 0)
    # Ensure the endpoint is reachable by forcing it to be open
    maze[rows - 1][cols - 1] = 0
    return maze

def draw_maze(screen, maze):
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            # Default color for passages is white; walls are black
            color = WHITE if maze[y][x] == 0 else BLACK
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Highlight the endpoint in red
    pygame.draw.rect(screen, RED, ((COLS - 1) * CELL_SIZE, (ROWS - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def show_message(screen, text, color):
    font = pygame.font.Font(None, 72)
    message = font.render(text, True, color)
    rect = message.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(message, rect)
    pygame.display.flip()
    # Pause for a few seconds to show the message
    pygame.time.delay(3000)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Online Maze Game for Learning")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    maze = generate_maze(ROWS, COLS)
    player_x, player_y = 0, 0  # starting position at top-left
    end_x, end_y = COLS - 1, ROWS - 1  # ending position at bottom-right
    
    start_ticks = pygame.time.get_ticks()  # start time
    
    running = True
    game_over = False
    win = False
    
    while running:
        # Calculate remaining time
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000  # in seconds
        remaining_time = max(0, TIME_LIMIT - elapsed_time)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game_over:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                new_x, new_y = player_x + dx, player_y + dy
                if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] == 0:
                    player_x, player_y = new_x, new_y

        # Check win condition: if player reaches the endpoint before time runs out
        if player_x == end_x and player_y == end_y:
            win = True
            game_over = True
        
        # Check loss condition: time ran out
        if remaining_time <= 0 and not win:
            game_over = True
        
        # Draw everything
        screen.fill(WHITE)
        draw_maze(screen, maze)
        # Draw the player as a green square
        pygame.draw.rect(screen, GREEN, (player_x * CELL_SIZE, player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the timer on the screen
        timer_text = font.render(f"Time: {int(remaining_time)}", True, BLACK)
        screen.blit(timer_text, (10, 10))
        pygame.display.flip()
        
        # End game if over: display win or game over message
        if game_over:
            if win:
                show_message(screen, "You Win!", BLUE)
            else:
                show_message(screen, "Game Over", RED)
            running = False
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
