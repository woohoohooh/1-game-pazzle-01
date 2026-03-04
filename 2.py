import pygame
import os
import sys
import random
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000  # Увеличена высота для мобильного формата
PIECE_SIZE = 100  # Базовый размер кусочка
BOARD_WIDTH = 1024
BOARD_HEIGHT = 1024

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)


class PuzzlePiece:
    def __init__(self, image, rect, correct_pos):
        self.image = image
        self.rect = rect
        self.correct_pos = correct_pos
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def update(self, pos=None):
        if self.dragging and pos:
            self.rect.x = pos[0] + self.offset_x
            self.rect.y = pos[1] + self.offset_y

    def is_correct_position(self):
        return (abs(self.rect.x - self.correct_pos[0]) < 20 and
                abs(self.rect.y - self.correct_pos[1]) < 20)


class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Пазл игра")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Переменные игры
        self.difficulty = 3  # По умолчанию 3x3
        self.images = []
        self.selected_image = None
        self.pieces = []
        self.dragging_piece = None
        self.completed = False
        self.game_state = "menu"  # menu, image_select, game

        # Загружаем изображения из папки
        self.load_images_from_folder()

    def load_images_from_folder(self):
        """Загрузка всех изображений из папки 'images'"""
        if not os.path.exists('images'):
            os.makedirs('images')
            print("Создана папка 'images'. Поместите туда изображения для пазлов.")

        for file in os.listdir('images'):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                try:
                    img_path = os.path.join('images', file)
                    img = pygame.image.load(img_path)
                    # Масштабируем до 1024x1024
                    img = pygame.transform.scale(img, (BOARD_WIDTH, BOARD_HEIGHT))
                    self.images.append((file, img))
                except Exception as e:
                    print(f"Ошибка загрузки {file}: {e}")

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(WHITE)

        # Заголовок
        title = self.font.render("Пазл игра", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Выбор сложности
        diff_text = self.small_font.render("Выберите сложность:", True, BLACK)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(diff_text, diff_rect)

        # Кнопки сложности
        difficulties = [("3x3 (9 частей)", 3), ("4x4 (16 частей)", 4), ("5x5 (25 частей)", 5)]
        button_y = 250

        for text, value in difficulties:
            color = BLUE if self.difficulty == value else GRAY
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 50)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)

            diff_label = self.small_font.render(text, True, BLACK)
            label_rect = diff_label.get_rect(center=button_rect.center)
            self.screen.blit(diff_label, label_rect)
            button_y += 70

        # Кнопка начала игры
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, start_rect)
        pygame.draw.rect(self.screen, BLACK, start_rect, 2)

        start_text = self.font.render("Начать", True, BLACK)
        start_rect_text = start_text.get_rect(center=start_rect.center)
        self.screen.blit(start_text, start_rect_text)

        return difficulties

    def draw_image_select(self):
        """Отрисовка экрана выбора изображения"""
        self.screen.fill(WHITE)

        title = self.font.render("Выберите изображение:", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        if not self.images:
            no_img_text = self.font.render("Нет изображений в папке 'images'", True, BLACK)
            no_img_rect = no_img_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_img_text, no_img_rect)

            back_text = self.small_font.render("Нажмите ESC для возврата в меню", True, BLACK)
            back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(back_text, back_rect)
            return []

        # Отображение превью изображений
        preview_rects = []
        cols = 2
        rows = (len(self.images) + cols - 1) // cols
        preview_width = 300
        preview_height = 300
        margin = 50

        start_x = (SCREEN_WIDTH - (cols * preview_width + (cols - 1) * margin)) // 2
        start_y = 150

        for i, (filename, img) in enumerate(self.images):
            row = i // cols
            col = i % cols

            x = start_x + col * (preview_width + margin)
            y = start_y + row * (preview_height + margin)

            # Создаем превью
            preview = pygame.transform.scale(img, (preview_width, preview_height))

            # Рамка
            pygame.draw.rect(self.screen, BLACK, (x - 2, y - 2, preview_width + 4, preview_height + 4), 2)
            self.screen.blit(preview, (x, y))

            # Название файла
            name_text = self.small_font.render(os.path.basename(filename)[:20], True, BLACK)
            name_rect = name_text.get_rect(center=(x + preview_width // 2, y + preview_height + 15))
            self.screen.blit(name_text, name_rect)

            preview_rects.append(pygame.Rect(x, y, preview_width, preview_height))

        return preview_rects

    def draw_game(self):
        """Отрисовка игрового поля"""
        self.screen.fill(WHITE)

        # Верхняя панель (адаптивная)
        top_panel = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, BLUE, top_panel)

        # Кнопка назад
        back_rect = pygame.Rect(10, 10, 80, 40)
        pygame.draw.rect(self.screen, LIGHT_BLUE, back_rect)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2)
        back_text = self.small_font.render("Меню", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Информация о пазле
        info_text = self.small_font.render(f"Пазл {self.difficulty}x{self.difficulty}", True, BLACK)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(info_text, info_rect)

        if self.completed:
            complete_text = self.font.render("Пазл собран!", True, BLACK)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(complete_text, complete_rect)

        # Игровое поле с центрированием
        board_size = self.difficulty * PIECE_SIZE
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = 80 + (SCREEN_HEIGHT - 80 - board_size) // 2

        # Рисуем сетку
        for i in range(self.difficulty + 1):
            # Вертикальные линии
            pygame.draw.line(self.screen, GRAY,
                             (board_x + i * PIECE_SIZE, board_y),
                             (board_x + i * PIECE_SIZE, board_y + board_size))
            # Горизонтальные линии
            pygame.draw.line(self.screen, GRAY,
                             (board_x, board_y + i * PIECE_SIZE),
                             (board_x + board_size, board_y + i * PIECE_SIZE))

        # Рисуем кусочки пазла
        for piece in self.pieces:
            self.screen.blit(piece.image, piece.rect)
            # Если кусочек перетаскивается, рисуем рамку
            if piece.dragging:
                pygame.draw.rect(self.screen, BLUE, piece.rect, 3)

        # Нижняя панель (адаптивная)
        bottom_panel = pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
        pygame.draw.rect(self.screen, BLUE, bottom_panel)

        return back_rect

    def create_puzzle(self, image):
        """Создание кусочков пазла"""
        self.pieces = []
        piece_width = BOARD_WIDTH // self.difficulty
        piece_height = BOARD_HEIGHT // self.difficulty

        # Центрирование игрового поля
        board_size = self.difficulty * PIECE_SIZE
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = 80 + (SCREEN_HEIGHT - 80 - board_size) // 2

        # Создаем кусочки
        for row in range(self.difficulty):
            for col in range(self.difficulty):
                # Вырезаем кусочек из изображения
                piece_surface = pygame.Surface((piece_width, piece_height))
                piece_surface.blit(image, (0, 0),
                                   (col * piece_width, row * piece_height,
                                    piece_width, piece_height))
                # Масштабируем до PIECE_SIZE
                piece_surface = pygame.transform.scale(piece_surface,
                                                       (PIECE_SIZE, PIECE_SIZE))

                # Правильная позиция
                correct_x = board_x + col * PIECE_SIZE
                correct_y = board_y + row * PIECE_SIZE

                # Случайная начальная позиция (в пределах видимости)
                start_x = random.randint(50, SCREEN_WIDTH - PIECE_SIZE - 50)
                start_y = random.randint(100, SCREEN_HEIGHT - PIECE_SIZE - 100)

                piece_rect = piece_surface.get_rect()
                piece_rect.x = start_x
                piece_rect.y = start_y

                piece = PuzzlePiece(piece_surface, piece_rect, (correct_x, correct_y))
                self.pieces.append(piece)

        self.completed = False

    def check_completion(self):
        """Проверка, собран ли пазл"""
        for piece in self.pieces:
            if not piece.is_correct_position():
                return False
        return True

    def run(self):
        running = True
        difficulties = []
        preview_rects = []
        back_rect = None

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.game_state == "image_select":
                            self.game_state = "menu"
                        elif self.game_state == "game":
                            self.game_state = "menu"

                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        mouse_pos = pygame.mouse.get_pos()

                        if self.game_state == "menu":
                            # Проверка кликов по кнопкам сложности
                            button_y = 250
                            for diff_value in [3, 4, 5]:
                                button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 50)
                                if button_rect.collidepoint(mouse_pos):
                                    self.difficulty = diff_value
                                button_y += 70

                            # Кнопка начала игры
                            start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
                            if start_rect.collidepoint(mouse_pos):
                                if self.images:
                                    self.game_state = "image_select"
                                else:
                                    print("Нет изображений для игры!")

                        elif self.game_state == "image_select":
                            # Проверка кликов по превью
                            for i, rect in enumerate(preview_rects):
                                if rect.collidepoint(mouse_pos):
                                    self.selected_image = self.images[i][1]
                                    self.create_puzzle(self.selected_image)
                                    self.game_state = "game"
                                    break

                        elif self.game_state == "game":
                            # Проверка клика по кнопке назад
                            if back_rect and back_rect.collidepoint(mouse_pos):
                                self.game_state = "menu"

                            # Проверка кликов по кусочкам
                            for piece in reversed(self.pieces):
                                if piece.rect.collidepoint(mouse_pos):
                                    piece.dragging = True
                                    piece.offset_x = piece.rect.x - mouse_pos[0]
                                    piece.offset_y = piece.rect.y - mouse_pos[1]
                                    self.dragging_piece = piece
                                    break

                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.dragging_piece:
                            self.dragging_piece.dragging = False

                            # Проверка, находится ли кусочек близко к правильной позиции
                            if self.dragging_piece.is_correct_position():
                                self.dragging_piece.rect.x = self.dragging_piece.correct_pos[0]
                                self.dragging_piece.rect.y = self.dragging_piece.correct_pos[1]

                            self.dragging_piece = None

                            # Проверка завершения пазла
                            self.completed = self.check_completion()

                elif event.type == MOUSEMOTION:
                    if self.dragging_piece:
                        mouse_pos = pygame.mouse.get_pos()
                        self.dragging_piece.update(mouse_pos)

            # Отрисовка в зависимости от состояния
            if self.game_state == "menu":
                difficulties = self.draw_menu()
            elif self.game_state == "image_select":
                preview_rects = self.draw_image_select()
            elif self.game_state == "game":
                back_rect = self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PuzzleGame()
    game.run()