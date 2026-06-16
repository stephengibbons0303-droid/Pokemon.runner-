#!/usr/bin/env python3
"""
Extract Galarian Moltres PROJECTILE sprites from a single 2x2 white-background sheet.

Layout (clockwise from top-left): Fiery Wrath, Hurricane, Air Slash, Dark Pulse.
In reading order (TL, TR, BL, BR): Fiery Wrath, Hurricane, Dark Pulse, Air Slash.

Two of these (Hurricane, Air Slash) are pale white/silver FX, so — like the Moltres
cast strips — we edge-flood ONLY near-pure-white sheet (tight threshold, no global
white key), otherwise the wind would be erased. Hurricane is re-oriented 180°
(flip both axes) per the brief so it points down-left toward Pikachu.

Run:  python3 tools/extract_moltres_proj.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'moltres_sheets', 'projectiles.png')
# reading order TL, TR, BL, BR ; rot180 = bake the requested reorientation
ORDER = [('fw', 'Fiery Wrath', False), ('hr', 'Hurricane', True),
         ('dp', 'Dark Pulse', False), ('as', 'Air Slash', False)]
TARGET = 240        # px — longest side of each saved projectile

def find_frames(a):
    H, W = a.shape[:2]; mx, my, m = W // 2, H // 2, 10
    return [(0, 0, mx - m, my - m), (mx + m, 0, W, my - m),
            (0, my + m, mx - m, H), (mx + m, my + m, W, H)]

def cutout(a, box):
    """Tight white-only flood so pale wind/cloud FX survives (no global white key)."""
    x0, y0, x1, y1 = box
    crop = a[y0:y1, x0:x1].astype(int)
    h, w, _ = crop.shape
    bglike = np.abs(crop - 255).sum(2) < 18                # only the flat sheet (~252-255)
    seed = np.zeros((h, w), bool)
    seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)
    lab, n = ndimage.label(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < 0.0006 * h * w:        continue    # speck
        keep |= comp
    filled = ndimage.binary_fill_holes(keep)
    holes = filled & ~keep
    hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        comp = hl == i
        if comp.sum() < 0.0012 * h * w:
            keep |= comp
    fg = keep
    out = np.dstack([crop.astype(np.uint8), (fg * 255).astype(np.uint8)])
    ys, xs = np.where(fg)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def main():
    a = np.asarray(Image.open(SRC).convert('RGB')).astype(int)
    previews = []
    for box, (key, label, rot180) in zip(find_frames(a), ORDER):
        im = Image.fromarray(cutout(a, box), 'RGBA')
        if rot180:
            im = im.transpose(Image.ROTATE_180)            # flip both axes → points down-left
        s = TARGET / max(im.width, im.height)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        outp = os.path.join(ROOT, f'moltres_proj_{key}.png')
        im.save(outp)
        print(f'{label:13s} -> moltres_proj_{key}.png  {im.width}x{im.height}' + ('  (rot180)' if rot180 else ''))
        previews.append(im)
    # green QA contact sheet (Moltres is dark; magenta/dark bg hides it)
    cw = max(im.width for im in previews); ch = max(im.height for im in previews); pad = 14
    sheet = Image.new('RGBA', (cw * 2 + pad * 3, ch * 2 + pad * 3), (40, 120, 60, 255))
    for i, im in enumerate(previews):
        r, c = divmod(i, 2)
        x = pad + c * (cw + pad) + (cw - im.width) // 2
        y = pad + r * (ch + pad) + (ch - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    sheet.convert('RGB').save('/tmp/moltres_proj_preview.png')
    print('preview -> /tmp/moltres_proj_preview.png')

if __name__ == '__main__':
    main()
