#!/usr/bin/env python3
"""Knock the flat/gradient background out of a portrait PNG, making it transparent.

Region-grows a flood from the top/left/right edges (NOT the bottom, where the
subject's body often touches the frame), following the smooth background gradient
and stopping at the subject's hard outline. Then a couple of "halo" passes remove
the anti-aliased background fringe left around the edge.

Tuned for the Ash prompt portraits (pink studio background). Adjust --grow /
--halo tolerances if a different background bleeds into the subject or leaves a
ring.

    python3 tools/cutout_bg.py ash_say0.png ash_say1.png ash_yay.png
"""
import sys, argparse
from collections import deque
from PIL import Image

def d2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

def cutout(path, grow, halo, ref):
    im = Image.open(path).convert('RGBA')
    W, H = im.size
    px = list(im.getdata())                       # flat [(r,g,b,a), ...]
    bg = bytearray(W*H)                            # 1 = background (make transparent)
    q = deque()
    def seed(x, y):
        i = y*W + x
        if not bg[i]: bg[i] = 1; q.append((x, y))
    for x in range(W): seed(x, 0)                  # top edge
    for y in range(H): seed(0, y); seed(W-1, y)    # left + right edges
    # region grow: a neighbour joins the background if it's close to the pixel we
    # came from (follows a gradient) and still in the broad background colour range
    while q:
        x, y = q.popleft()
        cur = px[y*W + x]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < W and 0 <= ny < H:
                j = ny*W + nx
                if not bg[j]:
                    c = px[j]
                    if d2(c, cur) <= grow*grow and d2(c, ref) <= 140*140:
                        bg[j] = 1; q.append((nx, ny))
    # halo: opaque pixels touching transparency that are still background-ish
    for _ in range(2):
        add = []
        for y in range(H):
            for x in range(W):
                i = y*W + x
                if bg[i]: continue
                if d2(px[i], ref) <= halo*halo:
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < W and 0 <= ny < H and bg[ny*W+nx]:
                            add.append(i); break
        if not add: break
        for i in add: bg[i] = 1
    out = [(r, g, b, 0) if bg[k] else (r, g, b, a) for k, (r, g, b, a) in enumerate(px)]
    im.putdata(out)
    im.save(path)
    cleared = sum(bg)
    print(f"{path}: cleared {cleared} px ({100*cleared/(W*H):.1f}%) -> transparent")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--grow', type=int, default=46, help='region-grow colour tolerance')
    ap.add_argument('--halo', type=int, default=70, help='fringe-removal tolerance vs the reference bg colour')
    ap.add_argument('--ref', default='251,190,196', help='reference background colour r,g,b')
    a = ap.parse_args()
    ref = tuple(int(v) for v in a.ref.split(','))
    for f in a.files: cutout(f, a.grow, a.halo, ref)
