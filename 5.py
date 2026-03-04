import pygame
import sys
import os
import random
from pygame.locals import *
import math

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
PUZZLE_SIZE = 1024

# Цвета в современном стиле
DARK_BG = (18, 18, 24)  # Тёмно-синий фон
DARKER_BG = (12, 12, 18)
PANEL_BG = (30, 30, 40)  # Панели
PANEL_BG_LIGHT = (40, 40, 50)
ACCENT_BLUE = (64, 128, 255)  # Ярко-синий акцент
ACCENT_BLUE_HOVER = (100, 150, 255)
ACCENT_PURPLE = (128, 100, 255)  # Фиолетовый
ACCENT_GREEN = (100, 255, 150)  # Зелёный
ACCENT_ORANGE = (255, 200, 100)  # Оранжевый
TEXT_WHITE = (240, 240, 255)  # Белый текст
TEXT_GRAY = (160, 160, 180)  # Серый текст
BORDER_COLOR = (60, 60, 80)
SHADOW_COLOR = (0, 0, 0, 64)


class Button:
    def __init__(self, x, y, width, height, text, color=ACCENT_BLUE,
                 hover_color=ACCENT_BLUE_HOVER, text_color=TEXT_WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        self.click_sound = None  # Можно добавить звук позже

    def draw(self, screen):
        # Тень
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height))
        shadow_surf.set_alpha(64)
        shadow_surf.fill((0, 0, 0))
        screen.blit(shadow_surf, shadow_rect)

        # Кнопка
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 2, border_radius=15)

        # Текст
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


class PuzzlePiece:
    def __init__(self, surface, correct_row, correct_col, piece_id):
        self.surface = surface
        self.correct_row = correct_row
        self.correct_col = correct_col
        self.current_row = correct_row
        self.current_col = correct_col
        self.id = piece_id
        self.rect = None
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.original_rect = None
        self.scale = 1.0
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.rotation = 0
        self.shadow_offset = 0

    def update_rect(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        if not self.is_dragging:
            self.original_rect = self.rect.copy()

    def start_drag(self, mouse_x, mouse_y):
        if self.rect:
            self.is_dragging = True
            self.drag_offset_x = mouse_x - self.rect.x
            self.drag_offset_y = mouse_y - self.rect.y
            self.original_rect = self.rect.copy()
            self.target_scale = 1.1  # Увеличиваем при перетаскивании
            self.shadow_offset = 8

    def update_drag(self, mouse_x, mouse_y):
        if self.is_dragging and self.rect:
            self.rect.x = mouse_x - self.drag_offset_x
            self.rect.y = mouse_y - self.drag_offset_y

    def end_drag(self):
        self.is_dragging = False
        self.target_scale = 1.0
        self.shadow_offset = 0

    def update(self):
        # Плавное изменение масштаба
        if self.scale < self.target_scale:
            self.scale = min(self.scale + 0.05, self.target_scale)
        elif self.scale > self.target_scale:
            self.scale = max(self.scale - 0.05, self.target_scale)

    def draw(self, screen):
        if self.rect:
            self.update()

            # Вычисляем размер с учётом масштаба
            scaled_width = int(self.rect.width * self.scale)
            scaled_height = int(self.rect.height * self.scale)

            # Центрируем масштабированное изображение
            draw_x = self.rect.x - (scaled_width - self.rect.width) // 2
            draw_y = self.rect.y - (scaled_height - self.rect.height) // 2

            # Масштабируем поверхность
            scaled_piece = pygame.transform.scale(self.surface, (scaled_width, scaled_height))

            # Тень
            if self.shadow_offset > 0:
                shadow_surf = pygame.Surface((scaled_width, scaled_height))
                shadow_surf.set_alpha(100)
                shadow_surf.fill((0, 0, 0))
                screen.blit(shadow_surf, (draw_x + self.shadow_offset, draw_y + self.shadow_offset))

            screen.blit(scaled_piece, (draw_x, draw_y))

            # Рамка
            if self.is_dragging:
                pygame.draw.rect(screen, ACCENT_BLUE,
                                 (draw_x, draw_y, scaled_width, scaled_height), 3)
            else:
                pygame.draw.rect(screen, BORDER_COLOR,
                                 (draw_x, draw_y, scaled_width, scaled_height), 1)


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 255
        self.size = random.randint(2, 5)
        self.color = random.choice([ACCENT_BLUE, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_ORANGE])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 5
        self.vy += 0.1  # Гравитация
        return self.life > 0

    def draw(self, screen):
        if self.life > 0:
            alpha_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color = (*self.color, self.life)
            pygame.draw.circle(alpha_surf, color, (self.size, self.size), self.size)
            screen.blit(alpha_surf, (self.x - self.size, self.y - self.size))


class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puzzle Master - Собери пазл")
        self.clock = pygame.time.Clock()

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)

        # Состояния игры
        self.state = "menu"  # menu, select_image, game
        self.difficulty = 3  # 3x3, 4x4, 5x5
        self.images = []
        self.selected_image = None
        self.puzzle = []
        self.dragging = False
        self.drag_piece = None
        self.completed = False
        self.moves = 0
        self.start_time = None
        self.current_time = 0
        self.particles = []

        # Анимация
        self.transition_alpha = 0
        self.completion_alpha = 0
        self.completion_direction = 1

        # Загрузка изображений
        self.load_images_from_folder()

        # Создание звёзд для фона
        self.stars = self.create_stars()

        # Создание кнопок
        self.create_buttons()

    def create_stars(self):
        stars = []
        for _ in range(100):
            stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5),
                'twinkle': random.uniform(0, 2 * math.pi)
            })
        return stars

    def create_buttons(self):
        """Создание кнопок интерфейса"""
        self.buttons = {
            'menu': {
                'easy': Button(SCREEN_WIDTH // 2 - 150, 250, 300, 70, "Лёгкий (3x3)"),
                'medium': Button(SCREEN_WIDTH // 2 - 150, 340, 300, 70, "Средний (4x4)"),
                'hard': Button(SCREEN_WIDTH // 2 - 150, 430, 300, 70, "Сложный (5x5)"),
                'select': Button(SCREEN_WIDTH // 2 - 150, 540, 300, 70, "Выбрать картинку")
            },
            'game': {
                'back': Button(20, 20, 120, 50, "← Меню", ACCENT_PURPLE,
                               color=(150, 120, 255)),
                'shuffle': Button(SCREEN_WIDTH - 180, 20, 150, 50, "Перемешать",
                                  ACCENT_ORANGE, color=(255, 150, 50))
            },
            'select': {
                'back': Button(20, 20, 120, 50, "← Назад", ACCENT_PURPLE,
                               color=(150, 120, 255))
            }
        }

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

    def create_puzzle(self, image):
        """Создание пазла из изображения"""
        pieces = []
        piece_width = PUZZLE_SIZE // self.difficulty
        piece_height = PUZZLE_SIZE // self.difficulty

        # Создаем список всех позиций
        positions = []
        for row in range(self.difficulty):
            for col in range(self.difficulty):
                positions.append((row, col))

        # Перемешиваем позиции
        random.shuffle(positions)

        # Создаем кусочки
        for i, (row, col) in enumerate(positions):
            # Вырезаем кусочек из изображения
            rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece_surface = pygame.Surface((piece_width, piece_height))
            piece_surface.blit(image, (0, 0), rect)

            # Создаем кусочек с правильными координатами, но текущие из перемешанных
            piece = PuzzlePiece(piece_surface, row, col, i)
            piece.current_row = positions[i][0]
            piece.current_col = positions[i][1]
            pieces.append(piece)

        return pieces

    def shuffle_puzzle(self):
        """Перемешивание пазла"""
        if not self.puzzle:
            return

        # Создаем список всех позиций
        positions = []
        for row in range(self.difficulty):
            for col in range(self.difficulty):
                positions.append((row, col))

        # Перемешиваем
        random.shuffle(positions)

        # Назначаем новые позиции
        for i, piece in enumerate(self.puzzle):
            piece.current_row = positions[i][0]
            piece.current_col = positions[i][1]

        self.moves = 0
        self.completed = False
        self.update_piece_positions()

        # Создаем частицы для эффекта
        self.create_particles(20)

    def create_particles(self, count):
        """Создание эффекта частиц"""
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.particles.append(Particle(x, y))

    def update_particles(self):
        """Обновление частиц"""
        self.particles = [p for p in self.particles if p.update()]

    def update_piece_positions(self):
        """Обновление позиций кусочков"""
        if not self.puzzle:
            return

        # Вычисляем размеры области пазла
        top_panel_height = 100
        available_height = SCREEN_HEIGHT - top_panel_height - 40

        # Масштабируем пазл, чтобы поместился на экране
        scale = min((SCREEN_WIDTH - 80) / PUZZLE_SIZE, available_height / PUZZLE_SIZE)
        display_size = int(PUZZLE_SIZE * scale)
        piece_size = display_size // self.difficulty

        puzzle_x = (SCREEN_WIDTH - display_size) // 2
        puzzle_y = top_panel_height + (available_height - display_size) // 2

        # Обновляем позиции каждого кусочка
        for piece in self.puzzle:
            if not piece.is_dragging:
                x = puzzle_x + piece.current_col * piece_size
                y = puzzle_y + piece.current_row * piece_size
                piece.update_rect(x, y, piece_size, piece_size)

    def find_piece_at_position(self, row, col, exclude_piece=None):
        """Поиск кусочка в указанной ячейке"""
        for piece in self.puzzle:
            if piece != exclude_piece and piece.current_row == row and piece.current_col == col:
                return piece
        return None

    def swap_pieces(self, piece1, piece2):
        """Обмен двух кусочков местами"""
        # Меняем текущие позиции
        piece1.current_row, piece2.current_row = piece2.current_row, piece1.current_row
        piece1.current_col, piece2.current_col = piece2.current_col, piece1.current_col
        self.moves += 1

        # Создаем эффект частиц
        if piece1.rect and piece2.rect:
            center_x = (piece1.rect.centerx + piece2.rect.centerx) // 2
            center_y = (piece1.rect.centery + piece2.rect.centery) // 2
            for _ in range(5):
                self.particles.append(Particle(center_x, center_y))

    def check_completion(self):
        """Проверка, собран ли пазл"""
        for piece in self.puzzle:
            if piece.current_row != piece.correct_row or piece.current_col != piece.correct_col:
                return False
        return True

    def format_time(self, seconds):
        """Форматирование времени"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def draw_background(self):
        """Отрисовка фона со звёздами"""
        self.screen.fill(DARK_BG)

        # Анимированные звёзды
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH)

            # Мерцание
            twinkle = (math.sin(star['twinkle']) + 1) * 0.5
            star['twinkle'] += 0.05
            alpha = int(100 + 155 * twinkle)

            color = (alpha, alpha, alpha)
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])

    def draw_panel(self, x, y, width, height, alpha=200):
        """Отрисовка панели с эффектом стекла"""
        panel = pygame.Surface((width, height))
        panel.set_alpha(alpha)
        panel.fill(PANEL_BG)
        self.screen.blit(panel, (x, y))

        # Верхняя подсветка
        highlight = pygame.Surface((width, 2))
        highlight.set_alpha(100)
        highlight.fill(TEXT_WHITE)
        self.screen.blit(highlight, (x, y))

        pygame.draw.rect(self.screen, BORDER_COLOR, (x, y, width, height), 2)

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.draw_background()

        # Заголовок с эффектом тени
        title = self.title_font.render("PUZZLE MASTER", True, ACCENT_BLUE)
        title_shadow = self.title_font.render("PUZZLE MASTER", True, (32, 64, 128))

        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        self.screen.blit(title_shadow, (title_x + 4, 124))
        self.screen.blit(title_shadow, (title_x + 2, 122))
        self.screen.blit(title, (title_x, 120))

        # Подзаголовок
        subtitle = self.small_font.render("Собери пазл своей мечты", True, TEXT_GRAY)
        subtitle_x = SCREEN_WIDTH // 2 - subtitle.get_width() // 2
        self.screen.blit(subtitle, (subtitle_x, 190))

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        for key, button in self.buttons['menu'].items():
            button.is_hovered = button.rect.collidepoint(mouse_pos)
            button.draw(self.screen)

        # Информация о количестве изображений
        if self.images:
            info_text = self.tiny_font.render(f"📷 Загружено: {len(self.images)} картинок", True, TEXT_GRAY)
        else:
            info_text = self.tiny_font.render("📷 Поместите картинки в папку 'images'", True, ACCENT_ORANGE)
        self.screen.blit(info_text, (20, SCREEN_HEIGHT - 40))

    def draw_image_selection(self):
        """Отрисовка экрана выбора изображения"""
        self.draw_background()

        # Заголовок
        title = self.font.render("Выберите изображение", True, TEXT_WHITE)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, 80))

        # Сетка миниатюр
        cols = 3
        thumb_size = 200
        margin = 30
        start_x = (SCREEN_WIDTH - (cols * thumb_size + (cols - 1) * margin)) // 2
        start_y = 150

        mouse_pos = pygame.mouse.get_pos()

        for i, (name, img) in enumerate(self.images):
            if i >= 9:  # Показываем только первые 9 изображений
                break

            row = i // cols
            col = i % cols
            x = start_x + col * (thumb_size + margin)
            y = start_y + row * (thumb_size + margin)

            # Тень миниатюры
            shadow_rect = pygame.Rect(x + 5, y + 5, thumb_size, thumb_size)
            pygame.draw.rect(self.screen, (0, 0, 0, 64), shadow_rect, border_radius=10)

            # Миниатюра
            thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)
            thumb = pygame.transform.scale(img, (thumb_size, thumb_size))

            # Подсветка при наведении
            if thumb_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, ACCENT_BLUE, thumb_rect.inflate(6, 6), 3, border_radius=12)

            self.screen.blit(thumb, (x, y))
            pygame.draw.rect(self.screen, BORDER_COLOR, thumb_rect, 2, border_radius=10)

            # Имя файла
            name_text = self.tiny_font.render(name[:15] + "..." if len(name) > 15 else name, True, TEXT_GRAY)
            self.screen.blit(name_text, (x, y + thumb_size + 5))

        # Если нет изображений
        if not self.images:
            no_img_text = self.font.render("Нет изображений в папке 'images'", True, TEXT_GRAY)
            no_img_rect = no_img_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_img_text, no_img_rect)

        # Кнопка назад
        back_button = self.buttons['select']['back']
        back_button.is_hovered = back_button.rect.collidepoint(mouse_pos)
        back_button.draw(self.screen)

    def draw_game(self):
        """Отрисовка игрового процесса"""
        self.draw_background()

        # Верхняя панель
        self.draw_panel(0, 0, SCREEN_WIDTH, 100, 200)

        # Информация
        diff_text = self.small_font.render(f"📊 {self.difficulty}x{self.difficulty}", True, TEXT_WHITE)
        moves_text = self.small_font.render(f"🔄 Ходов: {self.moves}", True, TEXT_WHITE)

        self.screen.blit(diff_text, (160, 40))
        self.screen.blit(moves_text, (300, 40))

        # Таймер
        if self.start_time and not self.completed:
            self.current_time = int(pygame.time.get_ticks() / 1000) - self.start_time
        time_text = self.small_font.render(f"⏱️ {self.format_time(self.current_time)}", True, TEXT_WHITE)
        self.screen.blit(time_text, (460, 40))

        # Прогресс
        if self.puzzle:
            correct_pieces = sum(1 for p in self.puzzle
                                 if p.current_row == p.correct_row and p.current_col == p.correct_col)
            progress = correct_pieces / len(self.puzzle)

            progress_bg = pygame.Rect(620, 45, 250, 30)
            progress_fill = pygame.Rect(620, 45, int(250 * progress), 30)

            pygame.draw.rect(self.screen, DARKER_BG, progress_bg, border_radius=15)
            pygame.draw.rect(self.screen, ACCENT_GREEN, progress_fill, border_radius=15)
            pygame.draw.rect(self.screen, BORDER_COLOR, progress_bg, 2, border_radius=15)

            progress_text = self.tiny_font.render(f"{correct_pieces}/{len(self.puzzle)}", True, TEXT_WHITE)
            text_rect = progress_text.get_rect(center=progress_bg.center)
            self.screen.blit(progress_text, text_rect)

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        for key, button in self.buttons['game'].items():
            button.is_hovered = button.rect.collidepoint(mouse_pos)
            button.draw(self.screen)

        # Обновляем позиции кусочков
        self.update_piece_positions()

        # Рисуем сетку
        if self.puzzle:
            top_panel_height = 100
            available_height = SCREEN_HEIGHT - top_panel_height - 40
            scale = min((SCREEN_WIDTH - 80) / PUZZLE_SIZE, available_height / PUZZLE_SIZE)
            display_size = int(PUZZLE_SIZE * scale)
            piece_size = display_size // self.difficulty

            puzzle_x = (SCREEN_WIDTH - display_size) // 2
            puzzle_y = top_panel_height + (available_height - display_size) // 2

            # Рисуем сетку
            for row in range(self.difficulty + 1):
                y = puzzle_y + row * piece_size
                pygame.draw.line(self.screen, BORDER_COLOR, (puzzle_x, y),
                                 (puzzle_x + display_size, y), 1)

            for col in range(self.difficulty + 1):
                x = puzzle_x + col * piece_size
                pygame.draw.line(self.screen, BORDER_COLOR, (x, puzzle_y),
                                 (x, puzzle_y + display_size), 1)

            # Рисуем кусочки (сначала не перетаскиваемые)
            for piece in self.puzzle:
                if not piece.is_dragging:
                    piece.draw(self.screen)

            # Рисуем перетаскиваемые кусочки поверх
            for piece in self.puzzle:
                if piece.is_dragging:
                    piece.draw(self.screen)

        # Рисуем частицы
        self.update_particles()
        for particle in self.particles:
            particle.draw(self.screen)

        # Проверка на завершение
        if self.check_completion() and not self.completed:
            self.completed = True
            self.completion_alpha = 0
            self.create_particles(50)

        if self.completed:
            self.draw_completion_message()

    def draw_completion_message(self):
        """Отрисовка сообщения о завершении"""
        self.completion_alpha += self.completion_direction * 5
        if self.completion_alpha >= 255:
            self.completion_alpha = 255
            self.completion_direction = -1
        elif self.completion_alpha <= 0:
            self.completion_alpha = 0
            self.completion_direction = 1

        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Сообщение
        complete_text = self.title_font.render("ПАЗЛ СОБРАН!", True, ACCENT_GREEN)
        complete_shadow = self.title_font.render("ПАЗЛ СОБРАН!", True, (0, 100, 0))

        text_x = SCREEN_WIDTH // 2 - complete_text.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - 50

        self.screen.blit(complete_shadow, (text_x + 4, text_y + 4))

        # Устанавливаем альфа-канал для текста
        text_surf = complete_text.copy()
        text_surf.set_alpha(self.completion_alpha)
        self.screen.blit(text_surf, (text_x, text_y))

        # Статистика
        stats = [
            f"Ходов: {self.moves}",
            f"Время: {self.format_time(self.current_time)}",
            f"Сложность: {self.difficulty}x{self.difficulty}"
        ]

        y_offset = 0
        for stat in stats:
            stat_text = self.font.render(stat, True, TEXT_WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30 + y_offset))
            self.screen.blit(stat_text, stat_rect)
            y_offset += 40

        congrats = self.small_font.render("Поздравляем с победой!", True, TEXT_GRAY)
        congrats_rect = congrats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
        self.screen.blit(congrats, congrats_rect)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            mouse_pos = pygame.mouse.get_pos()

            if self.state == "menu":
                # Кнопки меню
                if self.buttons['menu']['easy'].handle_event(event):
                    self.difficulty = 3
                    if self.images:
                        self.selected_image = self.images[0][1]
                        self.puzzle = self.create_puzzle(self.selected_image)
                        self.moves = 0
                        self.start_time = int(pygame.time.get_ticks() / 1000)
                        self.current_time = 0
                        self.state = "game"
                        self.completed = False
                        self.create_particles(20)

                elif self.buttons['menu']['medium'].handle_event(event):
                    self.difficulty = 4
                    if self.images:
                        self.selected_image = self.images[0][1]
                        self.puzzle = self.create_puzzle(self.selected_image)
                        self.moves = 0
                        self.start_time = int(pygame.time.get_ticks() / 1000)
                        self.current_time = 0
                        self.state = "game"
                        self.completed = False
                        self.create_particles(20)

                elif self.buttons['menu']['hard'].handle_event(event):
                    self.difficulty = 5
                    if self.images:
                        self.selected_image = self.images[0][1]
                        self.puzzle = self.create_puzzle(self.selected_image)
                        self.moves = 0
                        self.start_time = int(pygame.time.get_ticks() / 1000)
                        self.current_time = 0
                        self.state = "game"
                        self.completed = False
                        self.create_particles(20)

                elif self.buttons['menu']['select'].handle_event(event) and self.images:
                    self.state = "select_image"

            elif self.state == "select_image":
                # Кнопка назад
                if self.buttons['select']['back'].handle_event(event):
                    self.state = "menu"

                # Выбор изображения
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_image_selection(mouse_pos)

            elif self.state == "game":
                # Кнопки игры
                if self.buttons['game']['back'].handle_event(event):
                    self.state = "menu"
                    self.puzzle = []
                    self.completed = False

                elif self.buttons['game']['shuffle'].handle_event(event):
                    self.shuffle_puzzle()
                    self.start_time = int(pygame.time.get_ticks() / 1000)
                    self.current_time = 0

                # Управление пазлом
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.completed:
                        self.handle_puzzle_click(mouse_pos)

                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_puzzle_release()

                elif event.type == MOUSEMOTION:
                    if event.buttons[0] and not self.completed:  # Левая кнопка нажата
                        self.handle_puzzle_drag(mouse_pos)

        return True

    def handle_image_selection(self, pos):
        """Обработка выбора изображения"""
        cols = 3
        thumb_size = 200
        margin = 30
        start_x = (SCREEN_WIDTH - (cols * thumb_size + (cols - 1) * margin)) // 2
        start_y = 150

        for i, (name, img) in enumerate(self.images):
            if i >= 9:
                break

            row = i // cols
            col = i % cols
            x = start_x + col * (thumb_size + margin)
            y = start_y + row * (thumb_size + margin)
            thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)

            if thumb_rect.collidepoint(pos):
                self.selected_image = img
                self.puzzle = self.create_puzzle(img)
                self.moves = 0
                self.start_time = int(pygame.time.get_ticks() / 1000)
                self.current_time = 0
                self.state = "game"
                self.completed = False
                self.create_particles(20)
                return

    def handle_puzzle_click(self, pos):
        """Обработка клика по пазлу"""
        if not self.puzzle:
            return

        # Ищем кусочек под курсором (с конца, чтобы верхние были приоритетнее)
        for piece in reversed(self.puzzle):
            if piece.rect and piece.rect.collidepoint(pos):
                piece.start_drag(pos[0], pos[1])
                self.dragging = True
                self.drag_piece = piece
                break

    def handle_puzzle_drag(self, pos):
        """Обработка перетаскивания"""
        if not self.dragging or not self.drag_piece:
            return

        # Обновляем позицию перетаскиваемого кусочка
        self.drag_piece.update_drag(pos[0], pos[1])

        # Проверяем пересечения с другими кусочками
        for other in self.puzzle:
            if other != self.drag_piece and other.rect and self.drag_piece.rect:
                if self.drag_piece.rect.colliderect(other.rect):
                    # Меняем местами при пересечении
                    self.swap_pieces(self.drag_piece, other)
                    # Обновляем позиции после обмена
                    self.update_piece_positions()
                    break

    def handle_puzzle_release(self):
        """Обработка отпускания кусочка"""
        if self.drag_piece:
            self.drag_piece.end_drag()
            self.drag_piece = None
        self.dragging = False
        self.update_piece_positions()

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
            elif self.state == "game":
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PuzzleGame()
    game.run()