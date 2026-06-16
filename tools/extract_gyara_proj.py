#!/usr/bin/env python3
"""
Extract Gyarados PROJECTILE sprites from individual white-background images
(one isolated projectile per file in tools/gyarados_sheets/).

Tight white-only flood removes the sheet; large flat-white pockets trapped inside
a swirl (e.g. Dragon Dance's spiral gaps) are also stripped, while small enclosed
white specks (the galaxy's stars) are kept.

Run:  python3 tools/extract_gyara_proj.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'gyarados_sheets')
SHEETS = [
    ('dragon_dance.png', 'dd', 'Dragon Dance'),
    ('waterfall.png',    'wf', 'Waterfall jet'),
    ('waterfall_burst.png','wfb','Waterfall burst'),
    ('ice_fang.png',     'if', 'Ice Fang'),
    ('earthquake.png',   'eq', 'Earthquake'),
]
TARGET = 240

def cutout(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    h, w, _ = a.shape
    corners = np.array([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]])
    whitebg = corners.sum(1).mean() > 600                   # bg is white (Dragon Dance) vs black (Ice Fang)
    bgm = (np.abs(a - 255).sum(2) < 18) if whitebg else (a.sum(2) < 45)
    seed = np.zeros((h, w), bool); seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bgm
    fg = ~ndimage.binary_propagation(seed, mask=bgm)        # drop bg reachable from the border
    lab, n = ndimage.label(fg); keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        c = lab == i
        if c.sum() >= 0.0004 * h * w: keep |= c             # main blob(s), drop specks
    # strip LARGE flat-bg pockets trapped inside the FX (e.g. swirl gaps); keep small specks (stars)
    tl, tn = ndimage.label(keep & bgm)
    for i in range(1, tn + 1):
        c = tl == i
        if c.sum() > 0.0006 * h * w: keep &= ~c
    fg = keep
    ys, xs = np.where(fg)
    out = np.dstack([a.astype(np.uint8), (fg * 255).astype(np.uint8)])[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return out

def main():
    previews = []
    for fname, key, label in SHEETS:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path): continue
        im = Image.fromarray(cutout(path), 'RGBA')
        s = TARGET / max(im.width, im.height)
        im = im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.LANCZOS)
        im.save(os.path.join(ROOT, f'gyara_proj_{key}.png'))
        print(f'{label:13s} -> gyara_proj_{key}.png  {im.width}x{im.height}')
        previews.append(im)
    if not previews: print('no sheets in', SRC); return
    cw=max(i.width for i in previews); ch=max(i.height for i in previews); pad=14
    sheet=Image.new('RGBA',(cw*len(previews)+pad*(len(previews)+1), ch+2*pad),(26,16,30,255))
    for i,im in enumerate(previews): sheet.alpha_composite(im,(pad+i*(cw+pad)+(cw-im.width)//2, pad+(ch-im.height)//2))
    sheet.convert('RGB').save('/tmp/gyara_proj_preview.png'); print('preview -> /tmp/gyara_proj_preview.png')

if __name__ == '__main__':
    main()
