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
PUZZLE_SIZE = 1024
BUTTON_HEIGHT = 50
INFO_HEIGHT = 80

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)
GREEN = (100, 255, 150)
ORANGE = (255, 200, 100)


class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Пазл игра")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Состояния игры
        self.state = "menu"  # menu, select_image, game
        self.difficulty = 3  # 3x3, 4x4, 5x5
        self.images = []
        self.selected_image = None
        self.puzzle = None
        self.dragging = False
        self.drag_piece = None
        self.drag_offset = (0, 0)
        self.completed = False

        # Загрузка изображений из папки
        self.load_images_from_folder()

    def load_images_from_folder(self):
        """Загрузка всех изображений из папки 'images'"""
        folder = "images"
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Создана папка '{folder}'. Поместите туда изображения для пазлов.")
            return

        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        for file in os.listdir(folder):
            if file.lower().endswith(valid_extensions):
                try:
                    img_path = os.path.join(folder, file)
                    img = pygame.image.load(img_path)
                    # Масштабируем до размера пазла
                    img = pygame.transform.scale(img, (PUZZLE_SIZE, PUZZLE_SIZE))
                    self.images.append((file, img))
                except Exception as e:
                    print(f"Ошибка загрузки {file}: {e}")

        print(f"Загружено изображений: {len(self.images)}")

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(WHITE)

        # Заголовок
        title = self.font.render("Пазл игра", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Кнопки сложности
        difficulties = [
            ("Легкий (3x3)", 3, 150),
            ("Средний (4x4)", 4, 250),
            ("Сложный (5x5)", 5, 350)
        ]

        mouse_pos = pygame.mouse.get_pos()

        for text, diff, y_pos in difficulties:
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_pos, 300, 60)
            color = DARK_BLUE if button_rect.collidepoint(mouse_pos) else BLUE

            if self.difficulty == diff:
                pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, color, button_rect, border_radius=10)

            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)

            diff_text = self.font.render(text, True, BLACK)
            text_rect = diff_text.get_rect(center=button_rect.center)
            self.screen.blit(diff_text, text_rect)

        # Кнопка выбора изображения
        if self.images:
            select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 60)
            color = DARK_BLUE if select_rect.collidepoint(mouse_pos) else BLUE
            pygame.draw.rect(self.screen, color, select_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, select_rect, 2, border_radius=10)

            select_text = self.font.render("Выбрать", True, BLACK)
            text_rect = select_text.get_rect(center=select_rect.center)
            self.screen.blit(select_text, text_rect)

        # Информация о количестве изображений
        info_text = self.small_font.render(f"Загружено изображений: {len(self.images)}", True, DARK_GRAY)
        self.screen.blit(info_text, (20, SCREEN_HEIGHT - 40))

    def draw_image_selection(self):
        """Отрисовка экрана выбора изображения"""
        self.screen.fill(WHITE)

        title = self.font.render("Выберите изображение", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Отображение миниатюр
        cols = 3
        rows = 3
        thumb_size = 200
        margin = 30
        start_x = (SCREEN_WIDTH - (cols * thumb_size + (cols - 1) * margin)) // 2
        start_y = 120

        mouse_pos = pygame.mouse.get_pos()

        for i, (name, img) in enumerate(self.images):
            if i >= cols * rows:
                break

            row = i // cols
            col = i % cols
            x = start_x + col * (thumb_size + margin)
            y = start_y + row * (thumb_size + margin)

            # Миниатюра
            thumb = pygame.transform.scale(img, (thumb_size, thumb_size))
            thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)

            # Подсветка при наведении
            if thumb_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLUE, thumb_rect.inflate(10, 10), 3)

            self.screen.blit(thumb, (x, y))
            pygame.draw.rect(self.screen, BLACK, thumb_rect, 1)

            # Имя файла
            name_text = self.small_font.render(name[:15] + "..." if len(name) > 15 else name, True, BLACK)
            self.screen.blit(name_text, (x, y + thumb_size + 5))

        # Кнопка назад
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 70, 150, 50)
        color = DARK_BLUE if back_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(self.screen, color, back_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2, border_radius=10)

        back_text = self.small_font.render("Назад", True, BLACK)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)

    def create_puzzle(self, image):
        """Создание пазла из изображения"""
        pieces = []
        piece_width = PUZZLE_SIZE // self.difficulty
        piece_height = PUZZLE_SIZE // self.difficulty

        positions = []
        for row in range(self.difficulty):
            for col in range(self.difficulty):
                positions.append((row, col))

        random.shuffle(positions)

        for i, (row, col) in enumerate(positions):
            # Вырезаем кусочек
            rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece_surface = pygame.Surface((piece_width, piece_height))
            piece_surface.blit(image, (0, 0), rect)

            pieces.append({
                'surface': piece_surface,
                'correct_row': row,
                'correct_col': col,
                'current_row': positions[i][0],
                'current_col': positions[i][1],
                'rect': None,
                'id': i
            })

        return pieces

    def draw_game(self):
        """Отрисовка игрового процесса"""
        self.screen.fill(WHITE)

        # Верхняя панель
        top_panel_height = 60
        pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, top_panel_height))

        # Информация о сложности и кнопка назад
        diff_text = self.small_font.render(f"Сложность: {self.difficulty}x{self.difficulty}", True, BLACK)
        self.screen.blit(diff_text, (20, 20))

        mouse_pos = pygame.mouse.get_pos()

        # Кнопка назад
        back_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 120, 40)
        color = DARK_BLUE if back_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(self.screen, color, back_rect, border_radius=5)
        back_text = self.small_font.render("В меню", True, BLACK)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)

        # Область пазла
        puzzle_area_y = top_panel_height + 10
        puzzle_area_height = SCREEN_HEIGHT - puzzle_area_y - 10

        # Масштабируем пазл, чтобы поместился на экране
        scale = min((SCREEN_WIDTH - 40) / PUZZLE_SIZE, (puzzle_area_height - 40) / PUZZLE_SIZE)
        display_size = int(PUZZLE_SIZE * scale)

        puzzle_x = (SCREEN_WIDTH - display_size) // 2
        puzzle_y = puzzle_area_y + (puzzle_area_height - display_size) // 2

        # Рисуем сетку и кусочки
        piece_size = display_size // self.difficulty

        # Сначала обновляем позиции кусочков
        for piece in self.puzzle:
            piece_x = puzzle_x + piece['current_col'] * piece_size
            piece_y = puzzle_y + piece['current_row'] * piece_size
            piece['rect'] = pygame.Rect(piece_x, piece_y, piece_size, piece_size)

        # Рисуем сетку
        for row in range(self.difficulty + 1):
            y = puzzle_y + row * piece_size
            pygame.draw.line(self.screen, GRAY, (puzzle_x, y), (puzzle_x + display_size, y), 2)

        for col in range(self.difficulty + 1):
            x = puzzle_x + col * piece_size
            pygame.draw.line(self.screen, GRAY, (x, puzzle_y), (x, puzzle_y + display_size), 2)

        # Рисуем кусочки
        for piece in self.puzzle:
            if piece == self.drag_piece:
                continue  # Не рисуем перемещаемый кусочек сейчас

            # Масштабируем поверхность кусочка
            scaled_piece = pygame.transform.scale(piece['surface'], (piece_size, piece_size))
            self.screen.blit(scaled_piece, piece['rect'])

            # Рамка
            pygame.draw.rect(self.screen, BLACK, piece['rect'], 1)

        # Рисуем перемещаемый кусочек поверх остальных
        if self.drag_piece:
            scaled_piece = pygame.transform.scale(self.drag_piece['surface'], (piece_size, piece_size))
            self.screen.blit(scaled_piece, self.drag_piece['rect'])
            pygame.draw.rect(self.screen, BLUE, self.drag_piece['rect'], 3)

        # Проверка на завершение
        if self.check_completion():
            self.draw_completion_message()

    def draw_completion_message(self):
        """Отрисовка сообщения о завершении пазла"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        complete_text = self.font.render("Пазл собран!", True, GREEN)
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(complete_text, text_rect)

        congrats_text = self.small_font.render("Поздравляем!", True, BLACK)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(congrats_text, congrats_rect)

    def check_completion(self):
        """Проверка, собран ли пазл"""
        for piece in self.puzzle:
            if piece['current_row'] != piece['correct_row'] or piece['current_col'] != piece['correct_col']:
                return False
        return True

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.handle_mouse_down(event.pos)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.handle_mouse_up(event.pos)

            elif event.type == MOUSEMOTION:
                if self.dragging:
                    self.handle_mouse_drag(event.pos)

        return True

    def handle_mouse_down(self, pos):
        """Обработка нажатия мыши"""
        if self.state == "menu":
            # Проверка кнопок сложности
            difficulties = [(3, 150), (4, 250), (5, 350)]
            for diff, y_pos in difficulties:
                button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_pos, 300, 60)
                if button_rect.collidepoint(pos):
                    self.difficulty = diff

            # Кнопка выбора изображения
            select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 60)
            if select_rect.collidepoint(pos) and self.images:
                self.state = "select_image"

        elif self.state == "select_image":
            # Проверка нажатия на миниатюры
            cols = 3
            rows = 3
            thumb_size = 200
            margin = 30
            start_x = (SCREEN_WIDTH - (cols * thumb_size + (cols - 1) * margin)) // 2
            start_y = 120

            for i, (name, img) in enumerate(self.images):
                if i >= cols * rows:
                    break

                row = i // cols
                col = i % cols
                x = start_x + col * (thumb_size + margin)
                y = start_y + row * (thumb_size + margin)
                thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)

                if thumb_rect.collidepoint(pos):
                    self.selected_image = img
                    self.puzzle = self.create_puzzle(img)
                    self.state = "game"
                    self.completed = False
                    return

            # Кнопка назад
            back_rect = pygame.Rect(50, SCREEN_HEIGHT - 70, 150, 50)
            if back_rect.collidepoint(pos):
                self.state = "menu"

        elif self.state == "game":
            # Проверка кнопки назад
            back_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 120, 40)
            if back_rect.collidepoint(pos):
                self.state = "menu"
                self.puzzle = None
                return

            # Проверка нажатия на кусочек
            if self.puzzle:
                for piece in reversed(self.puzzle):
                    if piece['rect'] and piece['rect'].collidepoint(pos):
                        self.dragging = True
                        self.drag_piece = piece
                        self.drag_offset = (pos[0] - piece['rect'].x, pos[1] - piece['rect'].y)
                        break

    def handle_mouse_up(self, pos):
        """Обработка отпускания мыши"""
        if self.dragging and self.drag_piece and self.puzzle:
            # Находим ближайшую ячейку
            puzzle_area_y = 70
            display_size = int(PUZZLE_SIZE * min((SCREEN_WIDTH - 40) / PUZZLE_SIZE,
                                                 (SCREEN_HEIGHT - puzzle_area_y - 40) / PUZZLE_SIZE))
            puzzle_x = (SCREEN_WIDTH - display_size) // 2
            puzzle_y = puzzle_area_y + (SCREEN_HEIGHT - puzzle_area_y - display_size) // 2
            piece_size = display_size // self.difficulty

            # Вычисляем ближайшую ячейку
            col = round((pos[0] - puzzle_x - self.drag_offset[0] + piece_size // 2) / piece_size)
            row = round((pos[1] - puzzle_y - self.drag_offset[1] + piece_size // 2) / piece_size)

            # Ограничиваем границами
            col = max(0, min(self.difficulty - 1, col))
            row = max(0, min(self.difficulty - 1, row))

            # Проверяем, свободна ли ячейка
            target_free = True
            for piece in self.puzzle:
                if piece != self.drag_piece and piece['current_row'] == row and piece['current_col'] == col:
                    target_free = False
                    # Меняем местами
                    piece['current_row'], self.drag_piece['current_row'] = self.drag_piece['current_row'], piece[
                        'current_row']
                    piece['current_col'], self.drag_piece['current_col'] = self.drag_piece['current_col'], piece[
                        'current_col']
                    break

            if target_free:
                self.drag_piece['current_row'] = row
                self.drag_piece['current_col'] = col

        self.dragging = False
        self.drag_piece = None

    def handle_mouse_drag(self, pos):
        """Обработка перетаскивания мыши"""
        if self.drag_piece:
            self.drag_piece['rect'].x = pos[0] - self.drag_offset[0]
            self.drag_piece['rect'].y = pos[1] - self.drag_offset[1]

    def run(self):
        """Основной цикл игры"""
        running = True
        while running:
            running = self.handle_events()

            # Отрисовка в зависимости от состояния
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "select_image":
                self.draw_image_selection()
            elif self.state == "game" and self.puzzle:
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PuzzleGame()
    game.run()