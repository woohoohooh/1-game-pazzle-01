import pygame
import sys
import os
import random
import math
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
PUZZLE_SIZE = 1024  # Размер картинки пазла

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)


class PuzzlePiece:
    def __init__(self, image, rect, piece_id, grid_pos):
        self.image = image
        self.rect = rect
        self.original_rect = rect.copy()
        self.id = piece_id
        self.grid_pos = grid_pos  # (row, col) позиция в сетке
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
                return True

        elif event.type == MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y

        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Рисуем тонкую границу вокруг кусочка
        pygame.draw.rect(screen, BLACK, self.rect, 1)


class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puzzle Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Состояния игры
        self.STATE_MENU = 0
        self.STATE_SELECT_IMAGE = 1
        self.STATE_SELECT_DIFFICULTY = 2
        self.STATE_PLAYING = 3

        self.state = self.STATE_MENU

        # Параметры пазла
        self.images = []
        self.selected_image = None
        self.difficulty = 1  # 1-3 (легкий, средний, сложный)
        self.puzzle_pieces = []
        self.grid_size = 0
        self.piece_size = 0
        self.completed = False

        # Загружаем список картинок
        self.load_images()

        # UI элементы
        self.ui_elements = self.create_ui()

    def load_images(self):
        """Загружает список картинок из папки i"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        self.images = []

        if os.path.exists('i'):
            for file in os.listdir('i'):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    try:
                        path = os.path.join('i', file)
                        img = pygame.image.load(path)
                        # Масштабируем до размера пазла
                        img = pygame.transform.scale(img, (PUZZLE_SIZE, PUZZLE_SIZE))
                        self.images.append((file, img))
                    except:
                        print(f"Не удалось загрузить {file}")

        # Если картинок нет, создаем тестовую
        if not self.images:
            print("Картинки не найдены, создаю тестовую")
            test_surface = pygame.Surface((PUZZLE_SIZE, PUZZLE_SIZE))
            test_surface.fill((255, 0, 0))
            pygame.draw.circle(test_surface, (0, 255, 0), (512, 512), 256)
            pygame.draw.rect(test_surface, (0, 0, 255), (256, 256, 512, 512), 10)
            self.images.append(("test", test_surface))

    def create_ui(self):
        """Создает UI элементы с учетом растяжения"""
        # Верхняя панель
        top_panel = {
            'rect': pygame.Rect(0, 0, SCREEN_WIDTH, 80),
            'color': DARK_GRAY
        }

        # Нижняя панель
        bottom_panel = {
            'rect': pygame.Rect(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80),
            'color': DARK_GRAY
        }

        return {'top': top_panel, 'bottom': bottom_panel}

    def show_menu(self):
        """Показывает главное меню"""
        # Отрисовка фона
        self.screen.fill(WHITE)

        # Верхняя и нижняя панели
        pygame.draw.rect(self.screen, self.ui_elements['top']['color'], self.ui_elements['top']['rect'])
        pygame.draw.rect(self.screen, self.ui_elements['bottom']['color'], self.ui_elements['bottom']['rect'])

        # Заголовок
        title = self.font.render("PUZZLE GAME", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Кнопки меню
        button_y = 200
        buttons = [
            ("Начать игру", self.STATE_SELECT_IMAGE),
            ("Выход", None)
        ]

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for text, next_state in buttons:
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 60)

            # Анимация при наведении
            color = LIGHT_BLUE if button_rect.collidepoint(mouse_pos) else BLUE
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)

            text_surf = self.font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

            # Обработка клика
            if mouse_click[0] and button_rect.collidepoint(mouse_pos):
                if next_state is not None:
                    self.state = next_state
                else:
                    pygame.quit()
                    sys.exit()

            button_y += 100

    def show_image_selection(self):
        """Показывает выбор картинки"""
        self.screen.fill(WHITE)

        # Панели
        pygame.draw.rect(self.screen, self.ui_elements['top']['color'], self.ui_elements['top']['rect'])
        pygame.draw.rect(self.screen, self.ui_elements['bottom']['color'], self.ui_elements['bottom']['rect'])

        # Заголовок
        title = self.font.render("Выберите картинку", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Отображаем превью картинок
        preview_size = 200
        cols = 4
        start_x = 50
        start_y = 150

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for i, (name, img) in enumerate(self.images):
            col = i % cols
            row = i // cols

            x = start_x + col * (preview_size + 20)
            y = start_y + row * (preview_size + 50)

            # Масштабируем превью
            preview = pygame.transform.scale(img, (preview_size, preview_size))
            preview_rect = preview.get_rect(topleft=(x, y))

            # Рамка при наведении
            if preview_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLUE, preview_rect.inflate(10, 10), 3)

            self.screen.blit(preview, preview_rect)

            # Имя файла (обрезанное если длинное)
            short_name = name[:15] + "..." if len(name) > 15 else name
            name_text = self.small_font.render(short_name, True, BLACK)
            name_rect = name_text.get_rect(center=(x + preview_size // 2, y + preview_size + 15))
            self.screen.blit(name_text, name_rect)

            # Выбор картинки
            if mouse_click[0] and preview_rect.collidepoint(mouse_pos):
                self.selected_image = img
                self.state = self.STATE_SELECT_DIFFICULTY

        # Кнопка назад
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 130, 150, 50)
        pygame.draw.rect(self.screen, GRAY, back_rect)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2)
        back_text = self.font.render("Назад", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

        if mouse_click[0] and back_rect.collidepoint(mouse_pos):
            self.state = self.STATE_MENU

    def show_difficulty_selection(self):
        """Показывает выбор сложности"""
        self.screen.fill(WHITE)

        # Панели
        pygame.draw.rect(self.screen, self.ui_elements['top']['color'], self.ui_elements['top']['rect'])
        pygame.draw.rect(self.screen, self.ui_elements['bottom']['color'], self.ui_elements['bottom']['rect'])

        # Заголовок
        title = self.font.render("Выберите сложность", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Кнопки сложности
        button_y = 250
        difficulties = [
            ("Легкий (4x4)", 4),
            ("Средний (8x8)", 8),
            ("Сложный (16x16)", 16)
        ]

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for text, grid_size in difficulties:
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 60)

            # Анимация при наведении
            color = LIGHT_BLUE if button_rect.collidepoint(mouse_pos) else BLUE
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)

            text_surf = self.font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

            # Выбор сложности
            if mouse_click[0] and button_rect.collidepoint(mouse_pos):
                self.grid_size = grid_size
                self.piece_size = PUZZLE_SIZE // grid_size
                self.create_puzzle()
                self.state = self.STATE_PLAYING

            button_y += 100

        # Кнопка назад
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 130, 150, 50)
        pygame.draw.rect(self.screen, GRAY, back_rect)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2)
        back_text = self.font.render("Назад", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

        if mouse_click[0] and back_rect.collidepoint(mouse_pos):
            self.state = self.STATE_SELECT_IMAGE

    def create_puzzle(self):
        """Создает кусочки пазла"""
        self.puzzle_pieces = []

        # Создаем кусочки
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Вырезаем кусочек из картинки
                piece_rect = pygame.Rect(
                    col * self.piece_size,
                    row * self.piece_size,
                    self.piece_size,
                    self.piece_size
                )

                piece_image = self.selected_image.subsurface(piece_rect)

                # Случайная начальная позиция (но в пределах экрана)
                start_x = random.randint(50, SCREEN_WIDTH - self.piece_size - 50)
                start_y = random.randint(100, SCREEN_HEIGHT - self.piece_size - 100)

                piece = PuzzlePiece(
                    piece_image,
                    pygame.Rect(start_x, start_y, self.piece_size, self.piece_size),
                    row * self.grid_size + col,
                    (row, col)
                )

                self.puzzle_pieces.append(piece)

        random.shuffle(self.puzzle_pieces)
        self.completed = False

    def check_completion(self):
        """Проверяет, собрана ли головоломка"""
        tolerance = 20  # Допуск в пикселях

        for piece in self.puzzle_pieces:
            target_x = piece.grid_pos[1] * self.piece_size + 50  # Смещение от левого края
            target_y = piece.grid_pos[0] * self.piece_size + 100  # Смещение от верхнего края

            if abs(piece.rect.x - target_x) > tolerance or abs(piece.rect.y - target_y) > tolerance:
                return False

        return True

    def play_game(self):
        """Основной игровой процесс"""
        self.screen.fill(WHITE)

        # Панели
        pygame.draw.rect(self.screen, self.ui_elements['top']['color'], self.ui_elements['top']['rect'])
        pygame.draw.rect(self.screen, self.ui_elements['bottom']['color'], self.ui_elements['bottom']['rect'])

        # Область сборки пазла (прозрачный прямоугольник)
        puzzle_area = pygame.Rect(50, 100, PUZZLE_SIZE, PUZZLE_SIZE)
        pygame.draw.rect(self.screen, GRAY, puzzle_area, 2)

        # Рисуем сетку в области сборки
        for i in range(self.grid_size + 1):
            # Вертикальные линии
            x = 50 + i * self.piece_size
            pygame.draw.line(self.screen, GRAY, (x, 100), (x, 100 + PUZZLE_SIZE), 1)

            # Горизонтальные линии
            y = 100 + i * self.piece_size
            pygame.draw.line(self.screen, GRAY, (50, y), (50 + PUZZLE_SIZE, y), 1)

        # Обработка событий мыши для кусочков
        for piece in self.puzzle_pieces:
            piece.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {'pos': pygame.mouse.get_pos()}))

        # Рисуем кусочки
        for piece in self.puzzle_pieces:
            piece.draw(self.screen)

        # Информация в верхней панели
        info_text = f"Пазл {self.grid_size}x{self.grid_size}"
        info_surf = self.font.render(info_text, True, WHITE)
        info_rect = info_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(info_surf, info_rect)

        # Кнопка "Назад" в нижней панели
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 65, 150, 50)
        pygame.draw.rect(self.screen, GRAY, back_rect)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2)
        back_text = self.font.render("Меню", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Проверка завершения
        if not self.completed and self.check_completion():
            self.completed = True

        # Сообщение о завершении
        if self.completed:
            complete_text = self.font.render("ГОТОВО!", True, BLUE)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(complete_text, complete_rect)

        return back_rect

    def run(self):
        """Главный игровой цикл"""
        running = True

        while running:
            mouse_click = pygame.mouse.get_pressed()
            back_rect = None

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == MOUSEBUTTONDOWN:
                    if self.state == self.STATE_PLAYING:
                        # Проверка клика на кнопку "Меню"
                        if back_rect and back_rect.collidepoint(event.pos):
                            self.state = self.STATE_MENU

                # Передаем события кусочкам
                if self.state == self.STATE_PLAYING:
                    for piece in self.puzzle_pieces:
                        piece.handle_event(event)

            # Отрисовка в зависимости от состояния
            if self.state == self.STATE_MENU:
                self.show_menu()

            elif self.state == self.STATE_SELECT_IMAGE:
                self.show_image_selection()

            elif self.state == self.STATE_SELECT_DIFFICULTY:
                self.show_difficulty_selection()

            elif self.state == self.STATE_PLAYING:
                back_rect = self.play_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Создаем папку i если её нет
    if not os.path.exists('i'):
        os.makedirs('i')
        print("Создана папка 'i'. Поместите в неё картинки и запустите игру снова.")

    game = PuzzleGame()
    game.run()