#!/usr/bin/env python3
"""
Extract Lucario PROJECTILE sprites — the attacks that fly across the duel toward
Pikachu — from a single 2x2 white-background sheet (no grid lines).

Layout (clockwise from top-left): Vacuum Wave, Flash Cannon, Dragon Pulse, Aura
Sphere. In reading order (TL, TR, BL, BR) that is: Vacuum Wave, Flash Cannon,
Aura Sphere, Dragon Pulse.

Saves one tightly-cropped PNG per move (luca_proj_*.png), scaled to a uniform
longest-side. White-bg handling matches tools/extract_pika_proj.py (edge flood +
global white key + small-holes-only fill).

Run:  python3 tools/extract_luca_proj.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'lucario_redo', 'projectiles.png')
# reading order TL, TR, BL, BR
ORDER = [('vw', 'Vacuum Wave'), ('fc', 'Flash Cannon'), ('as', 'Aura Sphere'), ('dp', 'Dragon Pulse')]
TARGET = 240        # px — longest side of each saved projectile

def sat_val(a):
    mx = a.max(2); mn = a.min(2)
    return (mx - mn), mx

def find_frames(a):
    """The 4 grid cells as quadrant boxes in reading order (TL, TR, BL, BR), with a
    margin so neighbours never bleed across the centre."""
    H, W = a.shape[:2]
    mx, my, m = W // 2, H // 2, 10
    return [(0, 0, mx - m, my - m), (mx + m, 0, W, my - m),
            (0, my + m, mx - m, H), (mx + m, my + m, W, H)]

def cutout(a, box, whitebg):
    x0, y0, x1, y1 = box
    crop = a[y0:y1, x0:x1].astype(int)
    h, w, _ = crop.shape
    sat, val = sat_val(crop)
    bglike = (np.abs(crop - whitebg).sum(2) < 60) | ((sat < 18) & (val > 232))
    seed = np.zeros((h, w), bool)
    seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)
    fg &= ~(np.abs(crop - whitebg).sum(2) < 30)            # global white key
    lab, n = ndimage.label(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < 0.0004 * h * w:                    # tiny speck
            continue
        keep |= comp
    filled = ndimage.binary_fill_holes(keep)               # fill only small interior holes
    holes = filled & ~keep
    hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        comp = hl == i
        if comp.sum() < 0.0015 * h * w:
            keep |= comp
    fg = keep
    out = np.dstack([crop.astype(np.uint8), (fg * 255).astype(np.uint8)])
    ys, xs = np.where(fg)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def main():
    a = np.asarray(Image.open(SRC).convert('RGB')).astype(int)
    whitebg = np.array([255, 255, 255])
    previews = []
    for box, (key, label) in zip(find_frames(a), ORDER):
        rgba = cutout(a, box, whitebg)
        im = Image.fromarray(rgba, 'RGBA')
        s = TARGET / max(im.width, im.height)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        outp = os.path.join(ROOT, f'luca_proj_{key}.png')
        im.save(outp)
        print(f'{label:13s} -> luca_proj_{key}.png  {im.width}x{im.height}')
        previews.append(im)
    cw = max(im.width for im in previews); ch = max(im.height for im in previews); pad = 14
    sheet = Image.new('RGBA', (cw * 2 + pad * 3, ch * 2 + pad * 3), (255, 0, 255, 255))
    for i, im in enumerate(previews):
        r, c = divmod(i, 2)
        x = pad + c * (cw + pad) + (cw - im.width) // 2
        y = pad + r * (ch + pad) + (ch - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    sheet.convert('RGB').save('/tmp/luca_proj_preview.png')
    print('preview -> /tmp/luca_proj_preview.png')

if __name__ == '__main__':
    main()
