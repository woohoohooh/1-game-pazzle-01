import pygame
import os
import random
from PIL import Image, ImageDraw

SCREEN_W = 1080
SCREEN_H = 2048

IMG_DIR = "i"

LEVELS = {
    "easy":3,
    "medium":5,
    "hard":8
}

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Puzzle")

clock = pygame.time.Clock()


# ---------- load images ----------

def load_images():

    imgs = []

    if not os.path.exists(IMG_DIR):
        return []

    for f in os.listdir(IMG_DIR):
        if f.lower().endswith((".png",".jpg",".jpeg")):
            imgs.append(os.path.join(IMG_DIR,f))

    return imgs


# ---------- puzzle mask ----------

def create_mask(size, edges):

    w,h = size
    tab = int(min(w,h)*0.35)

    mask = Image.new("L",(w,h),0)
    draw = ImageDraw.Draw(mask)

    draw.rectangle((0,0,w,h),fill=255)

    cx = w//2
    cy = h//2

    if edges["top"]!=0:
        if edges["top"]==1:
            draw.ellipse((cx-tab,-tab,cx+tab,tab),fill=255)
        else:
            draw.ellipse((cx-tab,-tab,cx+tab,tab),fill=0)

    if edges["bottom"]!=0:
        if edges["bottom"]==1:
            draw.ellipse((cx-tab,h-tab,cx+tab,h+tab),fill=255)
        else:
            draw.ellipse((cx-tab,h-tab,cx+tab,h+tab),fill=0)

    if edges["left"]!=0:
        if edges["left"]==1:
            draw.ellipse((-tab,cy-tab,tab,cy+tab),fill=255)
        else:
            draw.ellipse((-tab,cy-tab,tab,cy+tab),fill=0)

    if edges["right"]!=0:
        if edges["right"]==1:
            draw.ellipse((w-tab,cy-tab,w+tab,cy+tab),fill=255)
        else:
            draw.ellipse((w-tab,cy-tab,w+tab,cy+tab),fill=0)

    return mask


# ---------- generate puzzle ----------

def create_pieces(img_path,n):

    img = Image.open(img_path).convert("RGBA")

    pw = img.width//n
    ph = img.height//n

    edges_grid=[[None]*n for _ in range(n)]

    pieces=[]

    for y in range(n):
        for x in range(n):

            edges={"top":0,"bottom":0,"left":0,"right":0}

            if y>0:
                edges["top"]=-edges_grid[y-1][x]["bottom"]

            if x>0:
                edges["left"]=-edges_grid[y][x-1]["right"]

            if y<n-1:
                edges["bottom"]=random.choice([-1,1])

            if x<n-1:
                edges["right"]=random.choice([-1,1])

            edges_grid[y][x]=edges

            crop=img.crop((x*pw,y*ph,(x+1)*pw,(y+1)*ph))

            mask=create_mask((pw,ph),edges)

            crop.putalpha(mask)

            surf=pygame.image.fromstring(
                crop.tobytes(),
                crop.size,
                crop.mode
            )

            pieces.append({
                "img":surf,
                "correct":(x*pw,y*ph),
                "pos":[random.randint(0,SCREEN_W-pw),
                       random.randint(300,SCREEN_H-ph-300)]
            })

    return pieces,pw,ph


# ---------- puzzle game ----------

def run_game(img):

    n=LEVELS["medium"]

    pieces,pw,ph=create_pieces(img,n)

    dragging=None
    offset=(0,0)

    puzzle_w=pw*n
    puzzle_h=ph*n

    off_x=(SCREEN_W-puzzle_w)//2
    off_y=(SCREEN_H-puzzle_h)//2

    running=True

    while running:

        screen.fill((25,25,35))

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                running=False

            if event.type==pygame.MOUSEBUTTONDOWN:

                mx,my=event.pos

                for p in reversed(pieces):

                    rect=pygame.Rect(
                        p["pos"][0]+off_x,
                        p["pos"][1]+off_y,
                        pw,ph
                    )

                    if rect.collidepoint(mx,my):
                        dragging=p
                        offset=(mx-p["pos"][0],my-p["pos"][1])
                        break

            if event.type==pygame.MOUSEBUTTONUP:

                if dragging:

                    cx,cy=dragging["correct"]

                    if abs(dragging["pos"][0]-cx)<40 and abs(dragging["pos"][1]-cy)<40:
                        dragging["pos"]=[cx,cy]

                    dragging=None

            if event.type==pygame.MOUSEMOTION and dragging:

                mx,my=event.pos
                dragging["pos"][0]=mx-offset[0]
                dragging["pos"][1]=my-offset[1]

        for p in pieces:

            screen.blit(
                p["img"],
                (p["pos"][0]+off_x,p["pos"][1]+off_y)
            )

        pygame.display.flip()
        clock.tick(60)


# ---------- main ----------

def main():

    imgs=load_images()

    if not imgs:
        print("No images in folder i")
        return

    run_game(imgs[0])


if __name__=="__main__":
    main()
