#!/usr/bin/env python3
"""
Extract Scizor move animation strips from the white-background 2x2 sequence sheets.

Identical pipeline to tools/extract_lucario.py (white-bg sibling): locate the 4
cells as the biggest saturated blobs, grow each box DOWN to recover Scizor's dark
feet, edge-flood-fill the white background to transparent, and assemble all four
moves to ONE shared scale + cell height so every move renders at the same size.

Processes whatever sheets are present in tools/scizor_sheets/, writes cleaned
strips (sciz_seq_*.png) into the repo root, plus a /tmp preview for visual QA.

Run:  python3 tools/extract_scizor.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'scizor_sheets')
WHITE = np.array([255, 255, 255])
# source filename -> (out key, label). sciz_seq_<key>.png; keys mirror the move files.
SHEETS = [
    ('x_scissor.png',   'xs', 'X-Scissor'),
    ('swords_dance.png', 'sd', 'Swords Dance'),
    ('bullet_punch.png', 'bp', 'Bullet Punch'),
    ('air_slash.png',    'as', 'Air Slash'),
]
TARGET_BODY = 240
PADX, PADTOP, PADBOT = 26, 22, 14
FEET_PAD = 95          # grow each box down this far to recover the dark feet

def sat_val(a):
    mx = a.max(2); mn = a.min(2)
    return (mx - mn), mx

def sprite_blobs(a):
    """Bounding boxes of the 4 sprites (biggest *saturated* blobs). Saturation cleanly
    separates the cells; boxes are grown down in find_frames to recover the feet."""
    sat, _ = sat_val(a)
    m = ndimage.binary_dilation(sat > 55, iterations=14)
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
    """Sprite bboxes in reading order (TL, TR, BL, BR), each grown DOWN to include the
    dark feet — clamped within the cell's quadrant so it never crosses the divider."""
    H, W = a.shape[:2]
    boxes = sprite_blobs(a)
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    ordered = sorted(boxes[:2], key=lambda b: b[0]) + sorted(boxes[2:], key=lambda b: b[0])
    grown = []
    for x0, y0, x1, y1 in ordered:
        qbot = (H // 2) if (y0 + y1) / 2 < H / 2 else H
        grown.append((x0, y0, x1, min(qbot - 8, y1 + FEET_PAD)))
    return grown

def cutout(a, box, pad=10):
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(a.shape[1], x1 + pad); y1 = min(a.shape[0], y1 + pad)
    crop = a[y0:y1, x0:x1].astype(int)
    h, w, _ = crop.shape
    sat, val = sat_val(crop)
    bglike = (np.abs(crop - WHITE).sum(2) < 60) | ((sat < 18) & (val > 232))
    seed = np.zeros((h, w), bool)
    seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)
    fg &= ~(np.abs(crop - WHITE).sum(2) < 30)             # global pure-white key
    dark = (val < 110) & (sat < 40)
    linecol = dark.mean(0)
    linerow = dark.mean(1)
    edge = np.zeros(w, bool); edge[:max(1, int(w * 0.16))] = True; edge[int(w * 0.84):] = True
    edgeR = np.zeros(h, bool); edgeR[:max(1, int(h * 0.16))] = True; edgeR[int(h * 0.84):] = True
    fg[:, edge & (linecol > 0.6)] = False
    fg[edgeR & (linerow > 0.6), :] = False
    lab, n = ndimage.label(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        ys, xs = np.where(comp)
        bw = xs.max() - xs.min() + 1; bh = ys.max() - ys.min() + 1
        if len(ys) < 0.004 * h * w:          continue
        if min(bw, bh) <= 16 and max(bw, bh) >= 0.45 * max(h, w) and val[comp].mean() < 120 and sat[comp].mean() < 45:
            continue
        keep |= comp
    filled = ndimage.binary_fill_holes(keep)
    holes = filled & ~keep
    hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        comp = hl == i
        if comp.sum() < 0.0015 * h * w:
            keep |= comp
    fg = keep
    out = np.dstack([crop.astype(np.uint8), (fg * 255).astype(np.uint8)])
    ys, xs = np.where(fg)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return out, (xs.max() + xs.min()) / 2 - xs.min(), float(ys.max() - ys.min())

def build(frames, scale, ch, padx=PADX, padbot=PADBOT):
    sized = []
    for rgba, cx, _ in frames:
        im = Image.fromarray(rgba, 'RGBA')
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        sized.append((im, cx * scale))
    left = max(cx for _, cx in sized); right = max(im.width - cx for im, cx in sized)
    cw = int(left + right) + 2 * padx
    axc = int(left) + padx
    baseY = ch - padbot
    strip = Image.new('RGBA', (cw * 4, ch), (0, 0, 0, 0))
    for i, (im, cx) in enumerate(sized):
        strip.alpha_composite(im, (i * cw + axc - int(cx), baseY - im.height))
    return strip, cw

def main():
    sheets = []
    for fname, key, label in SHEETS:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            continue
        a = np.asarray(Image.open(path).convert('RGB')).astype(int)
        frames = [cutout(a, b) for b in find_frames(a)]
        sheets.append((key, label, frames))
    if not sheets:
        print('No sheets found in', SRC); return
    scale = TARGET_BODY / np.median([fr[0][2] for _, _, fr in sheets])
    ch = int(round(max(h for _, _, fr in sheets for _, _, h in fr) * scale)) + PADTOP + PADBOT
    previews = []
    for key, label, frames in sheets:
        strip, cw = build(frames, scale, ch)
        outp = os.path.join(ROOT, f'sciz_seq_{key}.png')
        strip.save(outp)
        print(f'{label:13s} -> sciz_seq_{key}.png  {strip.width}x{strip.height}  (BOSS_SEQ: cw={cw}, ch={ch})')
        previews.append((label, strip))
    W = max(s.width for _, s in previews)
    H = sum(s.height for _, s in previews) + 20 * len(previews)
    sheet = Image.new('RGBA', (W, H), (255, 0, 255, 255))
    y = 0
    for _, s in previews:
        sheet.alpha_composite(s, (0, y)); y += s.height + 20
    sheet.convert('RGB').save('/tmp/sciz_preview.png')
    print('preview -> /tmp/sciz_preview.png')

if __name__ == '__main__':
    main()
