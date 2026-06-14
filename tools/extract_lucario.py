#!/usr/bin/env python3
"""
Extract Lucario move animation strips from the supplied 2x2 sequence sheets.

Each source sheet is a 2x2 grid (title bar + per-cell labels) of Lucario doing a
move across 4 frames, on a dark sheet background with lighter interior panels.

Pipeline (mirrors the Gyarados one documented in PROGRESS.md):
  1. Find the 4 sprites as the 4 largest *saturated* blobs (Lucario's blue/yellow
     body is saturated; panels, dividers and grey/white text are not).
  2. For each, crop a padded bbox, then edge-flood-fill the background to
     transparent (keeps interior black outlines, which aren't reachable from the
     edge). Background = near the dark sheet bg OR near the grey panel colour.
  3. Keep the largest blob (+ anything bright/coloured touching it) to drop stray
     label specks, then assemble the 4 frames into one uniform horizontal strip.

Run:  python3 tools/extract_lucario.py
Outputs cleaned strips (luca_seq_*.png) into the repo root, plus a preview.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'lucario_sheets')      # committed source 2x2 grids
SHEETS = [
    ('as', 'Aura Sphere',  f'{SRC}/aura_sphere.png'),
    ('fc', 'Flash Cannon', f'{SRC}/flash_cannon.png'),
    ('dp', 'Dragon Pulse', f'{SRC}/dragon_pulse.png'),
    ('vw', 'Vacuum Wave',  f'{SRC}/vacuum_wave.png'),
]

def sat_val(a):
    mx = a.max(2); mn = a.min(2)
    return (mx - mn), mx           # saturation (chroma), value

def sprite_blobs(a):
    """Bounding boxes of the 4 sprites (biggest saturated blobs)."""
    sat, _ = sat_val(a)
    m = ndimage.binary_dilation(sat > 55, iterations=14)   # merge body+FX per cell
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    boxes = []
    for idx in np.argsort(sizes)[::-1]:
        if sizes[idx] < 0.01 * a.shape[0] * a.shape[1]:
            break
        ys, xs = np.where(lab == idx + 1)
        boxes.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        if len(boxes) == 4:
            break
    return boxes

def find_frames(a):
    """Sprite blob bboxes in reading order (TL, TR, BL, BR)."""
    boxes = sprite_blobs(a)
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    return sorted(boxes[:2], key=lambda b: b[0]) + sorted(boxes[2:], key=lambda b: b[0])

def cutout(a, box, darkbg, pad=10):
    """Tight cutout of one sprite: pad the blob bbox, edge-flood-fill the bg to
    transparent, drop label/divider specks, tighten. Returns (rgba, cx, baseline)."""
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(a.shape[1], x1 + pad); y1 = min(a.shape[0], y1 + pad)
    crop = a[y0:y1, x0:x1].astype(int)
    h, w, _ = crop.shape
    sat, val = sat_val(crop)
    ring = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
    rsat = ring.max(1) - ring.min(1)
    panel = np.median(ring[rsat < 25], axis=0) if (rsat < 25).any() else darkbg
    bglike = (np.abs(crop - darkbg).sum(2) < 64) | ((np.abs(crop - panel).sum(2) < 64) & (sat < 28))
    seed = np.zeros((h, w), bool)
    seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)
    # kill straight frame-border lines near the crop edges (dark OR grey panel),
    # even where the FX touches them so they're not edge-reachable by the flood-fill
    near_dark = np.abs(crop - darkbg).sum(2) < 70
    near_panel = (np.abs(crop - panel).sum(2) < 70) & (sat < 30)
    linecol = (near_dark | near_panel).mean(0)            # fraction of each column that's bg-like
    linerow = near_dark.mean(1)
    edge = np.zeros(w, bool); edge[:max(1, int(w * 0.16))] = True; edge[int(w * 0.84):] = True
    fg[:, edge & (linecol > 0.6)] = False                 # vertical border at a crop edge
    fg[linerow > 0.85, :] = False                          # horizontal border
    lab, n = ndimage.label(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        ys, xs = np.where(comp)
        bw = xs.max() - xs.min() + 1; bh = ys.max() - ys.min() + 1
        if len(ys) < 0.004 * h * w:          continue     # speck
        # dark, thin, tall component spanning most of the height = a frame-border remnant
        if bw <= 18 and bh >= 0.45 * h and bh / bw >= 4 and val[comp].mean() < 105:
            continue
        keep |= comp
    fg = ndimage.binary_fill_holes(keep)
    out = np.dstack([crop.astype(np.uint8), (fg * 255).astype(np.uint8)])
    ys, xs = np.where(fg)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return out, (xs.max() + xs.min()) / 2 - xs.min(), float(ys.max() - ys.min())

def build(frames, target_h=240, padx=26, padtop=20, padbot=14):
    """Uniform scale across the 4 frames (median height); bottom-align on a common
    baseline and centre horizontally so Lucario stays put while the FX plays."""
    scale = target_h / np.median([h for _, _, h in frames])
    sized = []
    for rgba, cx, _ in frames:
        im = Image.fromarray(rgba, 'RGBA')
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        sized.append((im, cx * scale))
    left = max(cx for _, cx in sized); right = max(im.width - cx for im, cx in sized)
    top = max(im.height for im, _ in sized)
    cw = int(left + right) + 2 * padx
    ch = int(top) + padtop + padbot
    axc = int(left) + padx                                  # common horizontal anchor
    baseY = ch - padbot                                     # common baseline (feet)
    strip = Image.new('RGBA', (cw * 4, ch), (0, 0, 0, 0))
    for i, (im, cx) in enumerate(sized):
        strip.alpha_composite(im, (i * cw + axc - int(cx), baseY - im.height))
    return strip, cw

def main():
    previews = []
    for key, label, path in SHEETS:
        a = np.asarray(Image.open(path).convert('RGB')).astype(int)
        darkbg = np.median([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]], axis=0)
        boxes = find_frames(a)
        frames = [cutout(a, b, darkbg) for b in boxes]
        strip, cw = build(frames)
        outp = os.path.join(ROOT, f'luca_seq_{key}.png')
        strip.save(outp)
        print(f'{label:14s} -> luca_seq_{key}.png  {strip.width}x{strip.height} (cell {cw})')
        previews.append((label, strip))
    # contact sheet for visual QA (on magenta so transparency is obvious)
    W = max(s.width for _, s in previews)
    H = sum(s.height for _, s in previews) + 20 * len(previews)
    sheet = Image.new('RGBA', (W, H), (255, 0, 255, 255))
    y = 0
    for _, s in previews:
        sheet.alpha_composite(s, (0, y)); y += s.height + 20
    sheet.convert('RGB').save('/tmp/luca_preview.png')
    print('preview -> /tmp/luca_preview.png')

if __name__ == '__main__':
    main()
