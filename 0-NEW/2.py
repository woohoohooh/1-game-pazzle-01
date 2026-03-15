import pygame
import os
import random
import json
from PIL import Image, ImageDraw

SCREEN_W = 1080
SCREEN_H = 2048

IMG_DIR = "i"
SAVE_FILE = "save.json"

LEVEL = 6

SNAP_DIST = 40

pygame.init()

screen = pygame.display.set_mode((SCREEN_W,SCREEN_H), pygame.SCALED)
pygame.display.set_caption("Puzzle")

clock = pygame.time.Clock()


def load_images():

    imgs=[]

    if not os.path.exists(IMG_DIR):
        return imgs

    for f in os.listdir(IMG_DIR):

        if f.lower().endswith((".png",".jpg",".jpeg")):
            imgs.append(os.path.join(IMG_DIR,f))

    return imgs


def random_tab():
    return random.choice([-1,1])


def build_edge_grid(n):

    grid=[[None]*n for _ in range(n)]

    for y in range(n):
        for x in range(n):

            edges={"top":0,"bottom":0,"left":0,"right":0}

            if y>0:
                edges["top"]=-grid[y-1][x]["bottom"]

            if x>0:
                edges["left"]=-grid[y][x-1]["right"]

            if y<n-1:
                edges["bottom"]=random_tab()

            if x<n-1:
                edges["right"]=random_tab()

            grid[y][x]=edges

    return grid


def create_mask(w,h,edges):

    scale=3
    W=w*scale
    H=h*scale

    tab=int(min(W,H)*0.18)

    mask=Image.new("L",(W,H),0)
    draw=ImageDraw.Draw(mask)

    draw.rectangle((0,0,W,H),fill=255)

    cx=W//2
    cy=H//2

    if edges["top"]!=0:
        if edges["top"]==1:
            draw.ellipse((cx-tab,-tab,cx+tab,tab),fill=255)
        else:
            draw.ellipse((cx-tab,-tab,cx+tab,tab),fill=0)

    if edges["bottom"]!=0:
        if edges["bottom"]==1:
            draw.ellipse((cx-tab,H-tab,cx+tab,H+tab),fill=255)
        else:
            draw.ellipse((cx-tab,H-tab,cx+tab,H+tab),fill=0)

    if edges["left"]!=0:
        if edges["left"]==1:
            draw.ellipse((-tab,cy-tab,tab,cy+tab),fill=255)
        else:
            draw.ellipse((-tab,cy-tab,tab,cy+tab),fill=0)

    if edges["right"]!=0:
        if edges["right"]==1:
            draw.ellipse((W-tab,cy-tab,W+tab,cy+tab),fill=255)
        else:
            draw.ellipse((W-tab,cy-tab,W+tab,cy+tab),fill=0)

    mask=mask.resize((w,h),Image.LANCZOS)

    return mask


def create_pieces(img_path,n):

    img=Image.open(img_path).convert("RGBA")

    pw=img.width//n
    ph=img.height//n

    grid=build_edge_grid(n)

    pieces=[]
    groups={}

    gid=0

    for y in range(n):
        for x in range(n):

            edges=grid[y][x]

            crop=img.crop((x*pw,y*ph,(x+1)*pw,(y+1)*ph))

            mask=create_mask(pw,ph,edges)

            crop.putalpha(mask)

            surf=pygame.image.fromstring(
                crop.tobytes(),
                crop.size,
                crop.mode
            ).convert_alpha()

            piece={
                "img":surf,
                "correct":[x*pw,y*ph],
                "pos":[0,0],
                "group":gid,
                "locked":False
            }

            pieces.append(piece)

            groups[gid]=[piece]

            gid+=1

    scatter_pieces(pieces)

    return pieces,groups,pw,ph


def scatter_pieces(pieces):

    for p in pieces:

        side=random.choice(["left","right","top","bottom"])

        if side=="left":
            p["pos"]=[random.randint(-300,-50),random.randint(200,1800)]

        if side=="right":
            p["pos"]=[random.randint(1100,1400),random.randint(200,1800)]

        if side=="top":
            p["pos"]=[random.randint(0,1000),random.randint(-300,-50)]

        if side=="bottom":
            p["pos"]=[random.randint(0,1000),random.randint(2100,2400)]


def try_connect(pieces,groups,pw,ph):

    for a in pieces:
        for b in pieces:

            if a==b:
                continue

            if a["group"]==b["group"]:
                continue

            dx=a["correct"][0]-b["correct"][0]
            dy=a["correct"][1]-b["correct"][1]

            if abs(dx)==pw and dy==0 or abs(dy)==ph and dx==0:

                if abs(a["pos"][0]-b["pos"][0]-dx)<30 and \
                   abs(a["pos"][1]-b["pos"][1]-dy)<30:

                    ga=a["group"]
                    gb=b["group"]

                    groups[ga]+=groups[gb]

                    for p in groups[gb]:
                        p["group"]=ga

                    del groups[gb]

                    return


def save_progress(pieces):

    data=[]

    for p in pieces:

        data.append({
            "pos":p["pos"],
            "group":p["group"],
            "locked":p["locked"]
        })

    with open(SAVE_FILE,"w") as f:
        json.dump(data,f)


def load_progress(pieces):

    if not os.path.exists(SAVE_FILE):
        return

    data=json.load(open(SAVE_FILE))

    for i,p in enumerate(pieces):

        p["pos"]=data[i]["pos"]
        p["group"]=data[i]["group"]
        p["locked"]=data[i]["locked"]


def run_game(img):

    pieces,groups,pw,ph=create_pieces(img,LEVEL)

    load_progress(pieces)

    puzzle_w=pw*LEVEL
    puzzle_h=ph*LEVEL

    offx=(SCREEN_W-puzzle_w)//2
    offy=(SCREEN_H-puzzle_h)//2

    zoom=1
    camx=0
    camy=0

    dragging=None
    dx=dy=0

    running=True

    while running:

        screen.fill((25,25,35))

        for e in pygame.event.get():

            if e.type==pygame.QUIT:
                save_progress(pieces)
                running=False

            if e.type==pygame.MOUSEBUTTONDOWN:

                mx,my=pygame.mouse.get_pos()

                for p in reversed(pieces):

                    rect=pygame.Rect(
                        p["pos"][0]+offx,
                        p["pos"][1]+offy,
                        pw,ph
                    )

                    if rect.collidepoint(mx,my):

                        dragging=p
                        dx=mx-p["pos"][0]
                        dy=my-p["pos"][1]

                        pieces.remove(p)
                        pieces.append(p)

                        break

            if e.type==pygame.MOUSEBUTTONUP:

                if dragging:

                    cx,cy=dragging["correct"]

                    if abs(dragging["pos"][0]-cx)<SNAP_DIST and \
                       abs(dragging["pos"][1]-cy)<SNAP_DIST:

                        dragging["pos"]=[cx,cy]
                        dragging["locked"]=True

                    try_connect(pieces,groups,pw,ph)

                    save_progress(pieces)

                    dragging=None

            if e.type==pygame.MOUSEMOTION and dragging:

                mx,my=pygame.mouse.get_pos()

                gx=dragging["group"]

                for p in groups[gx]:

                    p["pos"][0]+=e.rel[0]
                    p["pos"][1]+=e.rel[1]

            if e.type==pygame.MOUSEWHEEL:

                zoom+=e.y*0.1
                zoom=max(0.5,min(zoom,3))

        pygame.draw.rect(screen,(40,40,60),(0,0,SCREEN_W,120))
        pygame.draw.rect(screen,(40,40,60),(0,SCREEN_H-120,SCREEN_W,120))

        for p in pieces:

            img=p["img"]

            w=int(pw*zoom)
            h=int(ph*zoom)

            surf=pygame.transform.smoothscale(img,(w,h))

            x=(p["pos"][0]+offx+camx)*zoom
            y=(p["pos"][1]+offy+camy)*zoom

            screen.blit(surf,(x,y))

        pygame.display.flip()

        clock.tick(60)


def main():

    imgs=load_images()

    if not imgs:
        print("no images in folder i")
        return

    run_game(imgs[0])


if __name__=="__main__":
    main()
