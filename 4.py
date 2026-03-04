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

# Цвета - современная палитра
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
GRAY = (240, 240, 245)
DARK_GRAY = (150, 150, 160)
PRIMARY = (52, 152, 219)      # Ярко-синий
PRIMARY_DARK = (41, 128, 185)  # Темно-синий
SUCCESS = (46, 204, 113)       # Зеленый
WARNING = (241, 196, 15)       # Желтый
DANGER = (231, 76, 60)         # Красный
PURPLE = (155, 89, 182)        # Фиолетовый
ORANGE = (230, 126, 34)        # Оранжевый

# Градиентные цвета для фона
BG_TOP = (52, 73, 94)
BG_BOTTOM = (44, 62, 80)


class Button:
    """Класс для стильных кнопок"""
    def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=PRIMARY_DARK,
                 text_color=WHITE, font_size=36, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.border_radius = border_radius
        self.is_hovered = False
        self.animation_offset = 0
        self.target_offset = 0

    def draw(self, screen):
        # Анимация при наведении
        if self.is_hovered:
            self.target_offset = -5
        else:
            self.target_offset = 0

        # Плавное движение
        self.animation_offset += (self.target_offset - self.animation_offset) * 0.3

        # Рисуем тень
        shadow_rect = self.rect.copy()
        shadow_rect.y += 5
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))
        screen.blit(shadow_surf, shadow_rect)

        # Рисуем кнопку
        button_rect = self.rect.copy()
        button_rect.y += self.animation_offset
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, button_rect, border_radius=self.border_radius)

        # Обводка
        pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=self.border_radius)

        # Текст
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puzzle Master - Собери пазл")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 72)

        # Состояния игры
        self.state = "menu"  # menu, select_image, game
        self.difficulty = 3  # 3x3, 4x4, 5x5
        self.images = []
        self.selected_image = None
        self.puzzle = None
        self.dragging = False
        self.drag_piece = None
        self.drag_offset = (0, 0)
        self.drag_start_pos = (0, 0)
        self.completed = False
        self.swap_animation = 0
        self.swap_piece = None
        self.show_instructions = True

        # Загрузка изображений из папки
        self.load_images_from_folder()

        # Создание кнопок
        self.create_buttons()

    def create_buttons(self):
        """Создание кнопок интерфейса"""
        self.menu_buttons = []
        self.diff_buttons = []

        # Кнопки сложности
        difficulties = [
            ("Новичок (3x3)", 3, 220, SUCCESS),
            ("Любитель (4x4)", 4, 320, WARNING),
            ("Мастер (5x5)", 5, 420, DANGER)
        ]

        for text, diff, y_pos, color in difficulties:
            btn = Button(SCREEN_WIDTH // 2 - 150, y_pos, 300, 60, text, color,
                        PRIMARY_DARK, WHITE, 32)
            btn.difficulty = diff
            self.diff_buttons.append(btn)

        # Кнопка выбора изображения
        self.select_btn = Button(SCREEN_WIDTH // 2 - 100, 520, 200, 60,
                                 "Выбрать", PRIMARY, PRIMARY_DARK, WHITE, 36)

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

    def draw_gradient_bg(self, top_color, bottom_color):
        """Рисует градиентный фон"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.draw_gradient_bg(BG_TOP, BG_BOTTOM)

        # Заголовок с тенью
        title_shadow = self.title_font.render("Puzzle Master", True, (0, 0, 0, 100))
        title = self.title_font.render("Puzzle Master", True, WHITE)

        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 5, 105))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))

        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)

        # Подзаголовок
        subtitle = self.small_font.render("Собери пазл своей мечты", True, GRAY)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, sub_rect)

        # Обработка событий мыши для кнопок
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.diff_buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_pos)

        self.select_btn.is_hovered = self.select_btn.rect.collidepoint(mouse_pos)

        # Рисуем кнопки сложности
        for btn in self.diff_buttons:
            if self.difficulty == btn.difficulty:
                # Подсветка выбранной сложности
                pygame.draw.circle(self.screen, SUCCESS,
                                 (btn.rect.x - 20, btn.rect.centery), 8)
            btn.draw(self.screen)

        # Кнопка выбора изображения
        if self.images:
            self.select_btn.draw(self.screen)
        else:
            # Сообщение об отсутствии изображений
            no_img_text = self.small_font.render("Нет изображений в папке 'images'",
                                                True, DANGER)
            text_rect = no_img_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
            self.screen.blit(no_img_text, text_rect)

        # Информация о количестве изображений
        info_bg = pygame.Surface((300, 50))
        info_bg.set_alpha(128)
        info_bg.fill(BLACK)
        self.screen.blit(info_bg, (20, SCREEN_HEIGHT - 70))

        info_text = self.small_font.render(f"📷 Изображений: {len(self.images)}",
                                          True, WHITE)
        self.screen.blit(info_text, (30, SCREEN_HEIGHT - 60))

        # Инструкция
        if self.show_instructions:
            instr_bg = pygame.Surface((400, 80))
            instr_bg.set_alpha(200)
            instr_bg.fill(PRIMARY_DARK)
            self.screen.blit(instr_bg, (SCREEN_WIDTH - 420, 20))

            instr_text = self.small_font.render("Перетаскивай кусочки", True, WHITE)
            instr_text2 = self.small_font.render("чтобы собрать картинку!", True, WHITE)
            self.screen.blit(instr_text, (SCREEN_WIDTH - 410, 30))
            self.screen.blit(instr_text2, (SCREEN_WIDTH - 410, 60))

    def draw_image_selection(self):
        """Отрисовка экрана выбора изображения"""
        self.draw_gradient_bg(BG_TOP, BG_BOTTOM)

        # Заголовок
        title = self.font.render("Выберите изображение", True, WHITE)
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

            # Тень для миниатюры
            shadow_rect = pygame.Rect(x + 5, y + 5, thumb_size, thumb_size)
            shadow_surf = pygame.Surface((thumb_size, thumb_size), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 50))
            self.screen.blit(shadow_surf, shadow_rect)

            # Миниатюра
            thumb = pygame.transform.scale(img, (thumb_size, thumb_size))
            thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)

            # Подсветка при наведении
            if thumb_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, WHITE, thumb_rect.inflate(10, 10), 3)

            self.screen.blit(thumb, (x, y))
            pygame.draw.rect(self.screen, WHITE, thumb_rect, 2)

            # Плашка с именем файла
            name_bg = pygame.Surface((thumb_size, 30))
            name_bg.set_alpha(180)
            name_bg.fill(BLACK)
            self.screen.blit(name_bg, (x, y + thumb_size - 30))

            name_text = self.small_font.render(name[:15] + "..." if len(name) > 15 else name,
                                              True, WHITE)
            self.screen.blit(name_text, (x + 10, y + thumb_size - 25))

        # Кнопка назад
        back_btn = Button(50, SCREEN_HEIGHT - 70, 150, 50, "← Назад",
                         PRIMARY, PRIMARY_DARK, WHITE, 32)
        back_btn.is_hovered = back_btn.rect.collidepoint(mouse_pos)
        back_btn.draw(self.screen)

        # Возвращаем back_btn для обработки событий
        return back_btn

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

    def find_piece_at_position(self, row, col):
        """Находит кусочек в указанной позиции"""
        for piece in self.puzzle:
            if piece['current_row'] == row and piece['current_col'] == col:
                return piece
        return None

    def draw_game(self):
        """Отрисовка игрового процесса"""
        self.draw_gradient_bg(BG_TOP, BG_BOTTOM)

        # Верхняя панель
        panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        panel_surf = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 100))
        self.screen.blit(panel_surf, panel_rect)

        # Информация о сложности
        diff_text = self.small_font.render(f"{self.difficulty} x {self.difficulty}", True, WHITE)
        self.screen.blit(diff_text, (30, 25))

        # Прогресс
        if self.puzzle:
            correct = sum(1 for p in self.puzzle
                         if p['current_row'] == p['correct_row'] and
                         p['current_col'] == p['correct_col'])
            total = len(self.puzzle)
            progress = correct / total

            # Полоса прогресса
            progress_bg = pygame.Rect(150, 25, 300, 30)
            pygame.draw.rect(self.screen, DARK_GRAY, progress_bg, border_radius=15)

            progress_fill = pygame.Rect(150, 25, int(300 * progress), 30)
            color = SUCCESS if progress == 1 else WARNING
            pygame.draw.rect(self.screen, color, progress_fill, border_radius=15)

            progress_text = self.small_font.render(f"{correct}/{total}", True, WHITE)
            text_rect = progress_text.get_rect(center=progress_bg.center)
            self.screen.blit(progress_text, text_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Кнопка назад
        back_btn = Button(SCREEN_WIDTH - 150, 15, 120, 50, "Меню",
                         DANGER, PRIMARY_DARK, WHITE, 28)
        back_btn.is_hovered = back_btn.rect.collidepoint(mouse_pos)
        back_btn.draw(self.screen)

        # Область пазла
        puzzle_area_y = 90
        puzzle_area_height = SCREEN_HEIGHT - puzzle_area_y - 20

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
            pygame.draw.line(self.screen, (255, 255, 255, 100),
                           (puzzle_x, y), (puzzle_x + display_size, y), 2)

        for col in range(self.difficulty + 1):
            x = puzzle_x + col * piece_size
            pygame.draw.line(self.screen, (255, 255, 255, 100),
                           (x, puzzle_y), (x, puzzle_y + display_size), 2)

        # Рисуем кусочки
        for piece in self.puzzle:
            if piece == self.drag_piece:
                continue  # Не рисуем перемещаемый кусочек сейчас

            # Масштабируем поверхность кусочка
            scaled_piece = pygame.transform.scale(piece['surface'], (piece_size, piece_size))

            # Добавляем легкую тень
            shadow_offset = 3
            shadow_rect = piece['rect'].copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            shadow_surf = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 30))
            self.screen.blit(shadow_surf, shadow_rect)

            self.screen.blit(scaled_piece, piece['rect'])

            # Если кусочек на своем месте - зеленая рамка
            if piece['current_row'] == piece['correct_row'] and piece['current_col'] == piece['correct_col']:
                pygame.draw.rect(self.screen, SUCCESS, piece['rect'], 3)
            else:
                pygame.draw.rect(self.screen, WHITE, piece['rect'], 1)

        # Рисуем перемещаемый кусочек поверх остальных
        if self.drag_piece:
            scaled_piece = pygame.transform.scale(self.drag_piece['surface'], (piece_size, piece_size))
            # Увеличиваем тень для перетаскиваемого
            shadow_offset = 8
            shadow_rect = self.drag_piece['rect'].copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            shadow_surf = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 80))
            self.screen.blit(shadow_surf, shadow_rect)

            self.screen.blit(scaled_piece, self.drag_piece['rect'])
            pygame.draw.rect(self.screen, PRIMARY, self.drag_piece['rect'], 4)

            # Рисуем стрелки направления
            if self.drag_start_pos:
                dx = mouse_pos[0] - self.drag_start_pos[0]
                dy = mouse_pos[1] - self.drag_start_pos[1]
                if abs(dx) > 20 or abs(dy) > 20:
                    center = self.drag_piece['rect'].center
                    if abs(dx) > abs(dy):
                        # Горизонтальное движение
                        if dx > 0:
                            pygame.draw.polygon(self.screen, PRIMARY,
                                              [(center[0] + 30, center[1]),
                                               (center[0] + 50, center[1] - 15),
                                               (center[0] + 50, center[1] + 15)])
                        else:
                            pygame.draw.polygon(self.screen, PRIMARY,
                                              [(center[0] - 30, center[1]),
                                               (center[0] - 50, center[1] - 15),
                                               (center[0] - 50, center[1] + 15)])
                    else:
                        # Вертикальное движение
                        if dy > 0:
                            pygame.draw.polygon(self.screen, PRIMARY,
                                              [(center[0], center[1] + 30),
                                               (center[0] - 15, center[1] + 50),
                                               (center[0] + 15, center[1] + 50)])
                        else:
                            pygame.draw.polygon(self.screen, PRIMARY,
                                              [(center[0], center[1] - 30),
                                               (center[0] - 15, center[1] - 50),
                                               (center[0] + 15, center[1] - 50)])

        # Проверка на завершение
        if self.check_completion():
            self.draw_completion_message()

    def draw_completion_message(self):
        """Отрисовка сообщения о завершении пазла"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Поздравление
        complete_text = self.font.render("🎉 ПАЗЛ СОБРАН! 🎉", True, SUCCESS)
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(complete_text, text_rect)

        congrats_text = self.small_font.render("Отличная работа!", True, WHITE)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(congrats_text, congrats_rect)

        # Кнопка в меню
        menu_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70,
                         200, 60, "В меню", PRIMARY, PRIMARY_DARK, WHITE, 36)
        menu_btn.draw(self.screen)

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
            for btn in self.diff_buttons:
                if btn.handle_event(pygame.event.Event(MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                    self.difficulty = btn.difficulty

            # Кнопка выбора изображения
            if self.select_btn.handle_event(pygame.event.Event(MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                if self.images:
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
            back_btn = Button(50, SCREEN_HEIGHT - 70, 150, 50, "← Назад",
                             PRIMARY, PRIMARY_DARK, WHITE, 32)
            if back_btn.handle_event(pygame.event.Event(MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                self.state = "menu"

        elif self.state == "game":
            # Проверка кнопки назад
            back_btn = Button(SCREEN_WIDTH - 150, 15, 120, 50, "Меню",
                             DANGER, PRIMARY_DARK, WHITE, 28)
            if back_btn.handle_event(pygame.event.Event(MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                self.state = "menu"
                self.puzzle = None
                return

            # Проверка нажатия на кусочек
            if self.puzzle and not self.completed:
                for piece in reversed(self.puzzle):
                    if piece['rect'] and piece['rect'].collidepoint(pos):
                        self.dragging = True
                        self.drag_piece = piece
                        self.drag_start_pos = pos
                        self.drag_offset = (pos[0] - piece['rect'].x, pos[1] - piece['rect'].y)
                        break

    def handle_mouse_up(self, pos):
        """Обработка отпускания мыши"""
        if self.dragging and self.drag_piece and self.puzzle:
            # Проверяем, достаточно ли далеко переместили для свапа
            drag_distance = math.hypot(pos[0] - self.drag_start_pos[0],
                                      pos[1] - self.drag_start_pos[1])

            if drag_distance > 30:  # Минимальное расстояние для свапа
                # Определяем направление
                dx = pos[0] - self.drag_start_pos[0]
                dy = pos[1] - self.drag_start_pos[1]

                target_row = self.drag_piece['current_row']
                target_col = self.drag_piece['current_col']

                if abs(dx) > abs(dy):
                    # Горизонтальное движение
                    if dx > 0 and target_col < self.difficulty - 1:
                        target_col += 1
                    elif dx < 0 and target_col > 0:
                        target_col -= 1
                else:
                    # Вертикальное движение
                    if dy > 0 and target_row < self.difficulty - 1:
                        target_row += 1
                    elif dy < 0 and target_row > 0:
                        target_row -= 1

                # Меняемся с кусочком в целевой позиции
                target_piece = self.find_piece_at_position(target_row, target_col)
                if target_piece and target_piece != self.drag_piece:
                    # Меняем местами
                    target_piece['current_row'], self.drag_piece['current_row'] = \
                        self.drag_piece['current_row'], target_piece['current_row']
                    target_piece['current_col'], self.drag_piece['current_col'] = \
                        self.drag_piece['current_col'], target_piece['current_col']

        self.dragging = False
        self.drag_piece = None

    def handle_mouse_drag(self, pos):
        """Обработка перетаскивания мыши"""
        if self.drag_piece:
            # Обновляем позицию для визуального отображения
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