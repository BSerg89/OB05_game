import pygame
import sys
import datetime

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Размеры клетки в лабиринте
TILE_SIZE = 40


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.level = 1
        self.score = 0
        self.name = ""
        self.state = "menu"  # Доступные состояния: menu, input_name, playing, game_over
        self.maze = None
        self.player = None
        self.enemies = []
        self.timer = 0
        self.start_time = None

    def run(self):
        while True:
            if self.state == "menu":
                self.show_menu()
            elif self.state == "input_name":
                self.get_name()
            elif self.state == "playing":
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            elif self.state == "game_over":
                self.show_game_over()
                self.handle_game_over()

    def show_menu(self):
        self.screen.fill(BLACK)
        menu_font = pygame.font.SysFont(None, 72)
        title_text = menu_font.render('Pacman Game', True, WHITE)
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 200, 50)
        achievements_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30, 200, 50)
        exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 50)

        pygame.draw.rect(self.screen, GREEN, start_button)
        pygame.draw.rect(self.screen, GREEN, achievements_button)
        pygame.draw.rect(self.screen, GREEN, exit_button)

        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
        self.screen.blit(self.font.render('Start Game', True, BLACK), (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 90))
        self.screen.blit(self.font.render('Achievements', True, BLACK),
                         (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(self.font.render('Exit', True, BLACK), (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        self.handle_menu_events(start_button, achievements_button, exit_button)

    def handle_menu_events(self, start_button, achievements_button, exit_button):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.collidepoint(mouse_pos):
                    self.state = "input_name"
                elif achievements_button.collidepoint(mouse_pos):
                    self.show_achievements()
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

    def get_name(self):
        self.screen.fill(BLACK)
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        text_surface = self.font.render(text, True, color)
        width = max(200, text_surface.get_width() + 10)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - width // 2, SCREEN_HEIGHT // 2 - 20, width, 40)

        pygame.draw.rect(self.screen, color, input_rect, 2)
        self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, GREEN, start_button)
        self.screen.blit(self.font.render('Start Game', True, BLACK), (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

        while self.state == "input_name":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos) and text:
                        self.name = text
                        self.state = "playing"
                        self.start_time = pygame.time.get_ticks()
                        self.maze = Maze(self.level)
                        self.player = self.maze.player_start
                        self.enemies = self.maze.enemy_starts
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            if text:
                                self.name = text
                                self.state = "playing"
                                self.start_time = pygame.time.get_ticks()
                                self.maze = Maze(self.level)
                                self.player = self.maze.player_start
                                self.enemies = self.maze.enemy_starts
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
                        text_surface = self.font.render(text, True, color)
                        width = max(200, text_surface.get_width() + 10)
                        input_rect.w = width
                    pygame.draw.rect(self.screen, BLACK, input_rect)
                    pygame.draw.rect(self.screen, color, input_rect, 2)
                    self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
                    pygame.display.flip()

    def show_achievements(self):
        self.screen.fill(BLACK)

        try:
            with open('highscores.txt', 'r') as file:
                scores = file.readlines()
        except FileNotFoundError:
            scores = []

        if scores:
            y_offset = 100  # Начальная вертикальная позиция для вывода текста
            header_text = self.font.render('Achievements:', True, WHITE)
            self.screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, y_offset))

            for score in scores:
                y_offset += 40  # Сдвиг для каждой новой строки
                score_text = self.font.render(score.strip(), True, WHITE)
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset))
        else:
            no_achievements_text = self.font.render('No achievements yet.', True, WHITE)
            self.screen.blit(no_achievements_text,
                             (SCREEN_WIDTH // 2 - no_achievements_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

        # Ожидание нажатия клавиши или мыши для возврата в меню
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = "menu"  # Возвращаемся в меню
                    return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        self.player.update(self.maze)
        for enemy in self.enemies:
            enemy.update(self.maze, self.player)
            if self.player.rect.colliderect(enemy.rect):
                self.state = "game_over"

        self.check_collisions()
        self.timer = (pygame.time.get_ticks() - self.start_time) // 1000

    def check_collisions(self):
        for point in self.maze.points[:]:
            if self.player.rect.colliderect(point):
                self.maze.points.remove(point)
                self.score += 10
        if not self.maze.points:
            self.level_up()

    def level_up(self):
        time_taken = (pygame.time.get_ticks() - self.start_time) // 1000
        self.save_result(time_taken)
        self.level += 1
        self.maze = Maze(self.level)
        self.player = self.maze.player_start
        self.enemies = self.maze.enemy_starts
        self.start_time = pygame.time.get_ticks()

    def save_result(self, time_taken):
        with open('highscores.txt', 'a') as file:
            file.write(f'{self.name} - Level {self.level} completed in {time_taken} seconds\n')

    def show_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render('Game Over', True, RED)
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
        menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)

        pygame.draw.rect(self.screen, GREEN, restart_button)
        pygame.draw.rect(self.screen, GREEN, menu_button)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
        self.screen.blit(self.font.render('Restart', True, BLACK), (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(self.font.render('Main Menu', True, BLACK), (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        self.handle_game_over_events(restart_button, menu_button)

    def handle_game_over_events(self, restart_button, menu_button):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.collidepoint(mouse_pos):
                    self.reset_game()
                    self.state = "playing"
                elif menu_button.collidepoint(mouse_pos):
                    self.state = "menu"

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.maze = Maze(self.level)
        self.player = self.maze.player_start
        self.enemies = self.maze.enemy_starts

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        score_text = self.font.render(f'Score: {self.score}', True, YELLOW)
        time_text = self.font.render(f'Time: {self.timer} seconds', True, YELLOW)
        level_text = self.font.render(f'Level: {self.level}', True, YELLOW)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(time_text, (SCREEN_WIDTH - 200, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))

        pygame.display.flip()


class Maze:
    def __init__(self, level):
        self.level = level
        self.points = []
        self.walls = []
        self.player_start = None
        self.enemy_starts = []
        self.create_maze()

    def create_maze(self):
        # Пример лабиринта (можно усложнять в зависимости от уровня)
        layout = [
            "############################",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#..........................#",
            "#.####.##.########.##.####.#",
            "#......##....##....##......#",
            "######.##### ## #####.######",
            "######.##### ## #####.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#E..##.......P........##...#",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#..........................#",
            "############################"
        ]

        for row_index, row in enumerate(layout):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "#":
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == ".":
                    self.points.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "P":
                    self.player_start = Player(x, y)
                elif tile == "E":
                    self.enemy_starts.append(Enemy(x, y))

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, WHITE, wall)
        for point in self.points:
            pygame.draw.circle(screen, YELLOW, point.center, TILE_SIZE // 8)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.color = YELLOW
        self.speed = 5

    def update(self, maze):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move(-self.speed, 0, maze.walls)
        if keys[pygame.K_RIGHT]:
            self.move(self.speed, 0, maze.walls)
        if keys[pygame.K_UP]:
            self.move(0, -self.speed, maze.walls)
        if keys[pygame.K_DOWN]:
            self.move(0, self.speed, maze.walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:  # Moving right
                    self.rect.right = wall.left
                if dx < 0:  # Moving left
                    self.rect.left = wall.right
                if dy > 0:  # Moving down
                    self.rect.bottom = wall.top
                if dy < 0:  # Moving up
                    self.rect.top = wall.bottom

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.color = RED
        self.speed = 2

    def update(self, maze, player):
        if self.rect.x < player.rect.x:
            self.move(self.speed, 0, maze.walls)
        if self.rect.x > player.rect.x:
            self.move(-self.speed, 0, maze.walls)
        if self.rect.y < player.rect.y:
            self.move(0, self.speed, maze.walls)
        if self.rect.y > player.rect.y:
            self.move(0, -self.speed, maze.walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:  # Moving right
                    self.rect.right = wall.left
                if dx < 0:  # Moving left
                    self.rect.left = wall.right
                if dy > 0:  # Moving down
                    self.rect.bottom = wall.top
                if dy < 0:  # Moving up
                    self.rect.top = wall.bottom

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


if __name__ == "__main__":
    game = Game()
    game.run()
