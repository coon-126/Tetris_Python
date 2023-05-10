import sys
import pygame
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
ROWS = SCREEN_HEIGHT // GRID_SIZE
COLS = SCREEN_WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Tetromino shapes
SHAPES = [
    [  # I shape
        [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
    ],
    [  # J shape
        [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    ],
    [  # L shape
        [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ]
    ],
    [  # O shape
        [
            [1, 1],
            [1, 1]
        ]
    ],
    [  # S shape
        [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ]
    ],
    [  # T shape
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    ],
    [  # Z shape
        [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ]
    ]
]

level = 1

def get_falling_speed(level):
    return max(1000 - (level - 1) * 100, 100)

def is_game_over(grid, tetromino):
    return not grid.can_move(tetromino, dx=0, dy=0)

def draw_game_over(screen):
    font = pygame.font.Font(None, 72)
    text = font.render("Game Over", 1, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

def clear_lines(grid):
    full_lines = []
    for i, row in enumerate(grid.cells):
        if all(cell == 1 for cell in row):
            full_lines.append(i)
    for line in full_lines:
        del grid.cells[line]
        grid.cells.insert(0, [0 for _ in range(COLS)])
    return len(full_lines)

def draw_score(screen, score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", 1, WHITE)
    screen.blit(text, (10, 10))

def rotate_tetromino(tetromino):
    return list(zip(*reversed(tetromino)))

def can_rotate(grid, tetromino):
    rotated_shape = rotate_tetromino(tetromino.shape)
    for y, row in enumerate(rotated_shape):
        for x, cell in enumerate(row):
            if cell:
                new_x, new_y = tetromino.x + x, tetromino.y + y
                if (new_x < 0 or new_x >= COLS or new_y >= ROWS
                        or grid.cells[new_y][new_x]):
                    return False
    return True

class Tetromino:
    def __init__(self, shape_index):
        self.shape = SHAPES[shape_index][0]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rotated_shape = list(zip(*reversed(self.shape)))
        self.shape = [list(row) for row in rotated_shape]

class Grid:
    def __init__(self):
        self.cells = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    def add_tetromino(self, tetromino):
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.cells[tetromino.y + y][tetromino.x + x] = 1

    def can_move(self, tetromino, dx, dy):
        for y, row in enumerate(tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x, new_y = tetromino.x + x + dx, tetromino.y + y + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or self.cells[new_y][new_x]:
                        return False
        return True

def draw_grid(screen, grid):
    for y, row in enumerate(grid.cells):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

def draw_tetromino(screen, tetromino):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, WHITE, (
                    (tetromino.x + x) * GRID_SIZE, (tetromino.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)


def main():
    clock = pygame.time.Clock()
    grid = Grid()
    tetromino = Tetromino(random.randint(0, len(SHAPES) - 1))  # Choose a random shape
    falling_time = 0
    elapsed_time = 0
    score = 0
    game_over = False


    key_repeat_interval = 100  # Key repeat interval in milliseconds
    key_repeat_delay_initial = 200
    key_repeat_timers = {
        pygame.K_LEFT: {'delay': key_repeat_delay_initial, 'interval': key_repeat_interval},
        pygame.K_RIGHT: {'delay': key_repeat_delay_initial, 'interval': key_repeat_interval},
        pygame.K_DOWN: {'delay': key_repeat_delay_initial, 'interval': key_repeat_interval},
    }

    while True:
        dt = clock.tick(30)
        falling_time += dt
        elapsed_time += dt
        level = elapsed_time // (60 * 1000) + 1  # Increase the level every minute

        keys = pygame.key.get_pressed()
        for key in key_repeat_timers:
            if keys[key]:
                key_repeat_timers[key]['delay'] -= dt
                if key_repeat_timers[key]['delay'] <= 0:
                    key_repeat_timers[key]['interval'] -= dt
                    if key_repeat_timers[key]['interval'] <= 0:
                        key_repeat_timers[key]['interval'] = key_repeat_interval
                        if key == pygame.K_LEFT:
                            if grid.can_move(tetromino, dx=-1, dy=0):
                                tetromino.x -= 1
                        if key == pygame.K_RIGHT:
                            if grid.can_move(tetromino, dx=1, dy=0):
                                tetromino.x += 1
                        if key == pygame.K_DOWN:
                            if grid.can_move(tetromino, dx=0, dy=1):
                                tetromino.y += 1
                                falling_time = 0
            else:
                key_repeat_timers[key]['delay'] = key_repeat_delay_initial
                key_repeat_timers[key]['interval'] = key_repeat_interval

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    tetromino.rotate()
                    if not grid.can_move(tetromino, dx=0, dy=0):
                        tetromino.rotate()
                        tetromino.rotate()
                        tetromino.rotate()

        if falling_time > get_falling_speed(level):
            if grid.can_move(tetromino, dx=0, dy=1):
                tetromino.y += 1
            else:
                grid.add_tetromino(tetromino)
                lines_cleared = clear_lines(grid)
                score += lines_cleared * 100
                tetromino = Tetromino(random.randint(0, len(SHAPES) - 1))  # Choose a new random shape
                if is_game_over(grid, tetromino):
                    game_over = True
            falling_time = 0

        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_tetromino(screen, tetromino)
        draw_score(screen, score)

        if game_over:
            draw_game_over(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()

