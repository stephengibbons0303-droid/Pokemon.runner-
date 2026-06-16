#!/usr/bin/env python3
"""
Extract Galarian Moltres's two FLYING poses (wings down / wings up) into a 2-frame
wing-flap pair for the duel hover idle. Both are saved at the SAME canvas size with
the body centred on a common baseline, so alternating them flaps the wings without
the body jumping. White-bg, tight white-only flood (keeps the pink flame wisps).

Run:  python3 tools/extract_moltres_fly.py  ->  moltres_fly0.png (down), moltres_fly1.png (up)
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'moltres_sheets')
FRAMES = [('fly_down.png', 'moltres_fly0.png'), ('fly_up.png', 'moltres_fly1.png')]
TARGET_BODY = 240
PADX, PADTOP, PADBOT = 24, 18, 14

def cut(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    h, w, _ = a.shape
    sat = a.max(2) - a.min(2)
    bglike = np.abs(a - 255).sum(2) < 18                   # only the flat white sheet
    seed = np.zeros((h, w), bool); seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)
    lab, n = ndimage.label(fg); keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() >= 0.0006 * h * w:
            keep |= comp
    # Moltres's belly is pure white (= the sheet) and connects out through the gap
    # between his legs, so the flood ate it. Close that thin slit, then add back any
    # LARGE now-enclosed white region (the belly) — small flame-gaps stay transparent.
    bird = np.abs(a - 255).sum(2) > 18
    enclosed = ndimage.binary_fill_holes(ndimage.binary_closing(bird, iterations=8)) & ~keep
    el, en = ndimage.label(enclosed)
    for i in range(1, en + 1):
        comp = el == i
        if comp.sum() > 2500:
            keep |= comp
    fg = keep
    ys, xs = np.where(fg); t, b, l, r = ys.min(), ys.max(), xs.min(), xs.max()
    out = np.dstack([a.astype(np.uint8), (fg * 255).astype(np.uint8)])[t:b + 1, l:r + 1]
    body = fg & (sat > 55)
    byc = np.where(body.any(1))[0]; bxc = np.where(body.any(0))[0]
    cx = (bxc.min() + bxc.max()) / 2 - l
    body_h = float(byc.max() - byc.min())
    return out, cx, body_h

def main():
    cuts = [(cut(os.path.join(SRC, src)), out) for src, out in FRAMES]
    scale = TARGET_BODY / np.median([c[0][2] for c in cuts])
    sized = []
    for (rgba, cx, _), outname in cuts:
        im = Image.fromarray(rgba, 'RGBA')
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        sized.append((im, cx * scale, outname))
    left = max(cx for _, cx, _ in sized); right = max(im.width - cx for im, cx, _ in sized)
    cw = int(left + right) + 2 * PADX
    ch = int(max(im.height for im, _, _ in sized)) + PADTOP + PADBOT
    axc = int(left) + PADX; baseY = ch - PADBOT
    for im, cx, outname in sized:
        canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        canvas.alpha_composite(im, (axc - int(cx), baseY - im.height))
        canvas.save(os.path.join(ROOT, outname))
        print(f'{outname}  {cw}x{ch}')
    # green QA pair
    sheet = Image.new('RGBA', (cw * 2 + 30, ch + 20), (40, 120, 60, 255))
    for i, (_, _, outname) in enumerate(sized):
        sheet.alpha_composite(Image.open(os.path.join(ROOT, outname)), (10 + i * (cw + 10), 10))
    sheet.convert('RGB').save('/tmp/moltres_fly_preview.png'); print('preview -> /tmp/moltres_fly_preview.png')

if __name__ == '__main__':
    main()
