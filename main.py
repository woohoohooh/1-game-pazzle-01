import pygame
import os
from PIL import Image
import random

# SETTINGS
IMG_FOLDER = "i"
WIN_W, WIN_H = 900, 1200  # mobile-like portrait
BG_COLOR = (30, 30, 40)

# puzzle sizes (difficulty)
LEVELS = {
    "Easy": 3,
    "Medium": 5,
    "Hard": 8
}

pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Puzzle Game")
font = pygame.font.SysFont(None, 36)


# ================= LOAD IMAGES =================
def load_images():
    imgs = []
    for f in os.listdir(IMG_FOLDER):
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            imgs.append(os.path.join(IMG_FOLDER, f))
    return imgs


# ================= SPLIT IMAGE =================
def split_image(path, n):
    img = Image.open(path)
    w, h = img.size
    piece_w = w // n
    piece_h = h // n

    pieces = []
    for y in range(n):
        for x in range(n):
            box = (x * piece_w, y * piece_h, (x + 1) * piece_w, (y + 1) * piece_h)
            piece = img.crop(box)
            pieces.append(piece)

    return pieces, piece_w, piece_h


# ================= PUZZLE CLASS =================
class Piece:
    def __init__(self, img, correct_pos, pos):
        self.image = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        self.rect = self.image.get_rect(topleft=pos)
        self.correct_pos = correct_pos
        self.drag = False


# ================= MAIN GAME =================
def run_game(img_path, level_name):
    n = LEVELS[level_name]
    pieces, pw, ph = split_image(img_path, n)

    # scale puzzle to screen width
    scale = WIN_W / (pw * n)
    pw = int(pw * scale)
    ph = int(ph * scale)

    # convert PIL -> pygame
    puzzle = []
    for i, p in enumerate(pieces):
        p = p.resize((pw, ph))
        x = (i % n) * pw
        y = (i // n) * ph
        puzzle.append((p, (x, y)))

    # shuffle positions
    positions = [pos for _, pos in puzzle]
    random.shuffle(positions)

    pieces_objs = []
    for i, (img, _) in enumerate(puzzle):
        pos = positions[i]
        pieces_objs.append(Piece(img, puzzle[i][1], pos))

    offset_x = 0
    offset_y = (WIN_H - (ph * n)) // 2  # center vertically

    dragging = None
    running = True

    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for p in reversed(pieces_objs):
                    if p.rect.collidepoint(event.pos):
                        dragging = p
                        p.drag = True
                        break

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    dragging.drag = False
                    dragging = None

            if event.type == pygame.MOUSEMOTION and dragging:
                dragging.rect.x += event.rel[0]
                dragging.rect.y += event.rel[1]

        # draw pieces
        for p in pieces_objs:
            screen.blit(p.image, (p.rect.x + offset_x, p.rect.y + offset_y))

        pygame.display.flip()


# ================= MENU =================
def main_menu():
    images = load_images()
    if not images:
        print("No images in folder i/")
        return

    selected_img = 0
    selected_level = 0
    levels = list(LEVELS.keys())

    while True:
        screen.fill(BG_COLOR)

        # draw image list
        y = 100
        for i, img in enumerate(images):
            txt = font.render(os.path.basename(img), True, (255, 255, 255))
            screen.blit(txt, (50, y))
            if i == selected_img:
                pygame.draw.rect(screen, (255, 200, 0), (40, y-2, 400, 30), 2)
            y += 40

        # draw difficulty
        y = 600
        for i, lvl in enumerate(levels):
            txt = font.render(lvl, True, (255, 255, 255))
            screen.blit(txt, (500, y))
            if i == selected_level:
                pygame.draw.rect(screen, (0, 200, 255), (490, y-2, 200, 30), 2)
            y += 40

        # start text
        screen.blit(font.render("ENTER to start", True, (255,255,255)), (350, 1100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_img = (selected_img + 1) % len(images)
                if event.key == pygame.K_UP:
                    selected_img = (selected_img - 1) % len(images)

                if event.key == pygame.K_RIGHT:
                    selected_level = (selected_level + 1) % len(levels)
                if event.key == pygame.K_LEFT:
                    selected_level = (selected_level - 1) % len(levels)

                if event.key == pygame.K_RETURN:
                    run_game(images[selected_img], levels[selected_level])

        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
