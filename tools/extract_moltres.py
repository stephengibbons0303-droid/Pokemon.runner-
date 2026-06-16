#!/usr/bin/env python3
"""
Extract Galarian Moltres move animation strips from the white-background 2x2 sequence sheets.

Identical pipeline to tools/extract_lucario.py (white-bg sibling): locate the 4
cells as the biggest saturated blobs, grow each box DOWN to recover Scizor's dark
feet, edge-flood-fill the white background to transparent, and assemble all four
moves to ONE shared scale + cell height so every move renders at the same size.

Processes whatever sheets are present in tools/moltres_sheets/, writes cleaned
strips (moltres_seq_*.png) into the repo root, plus a /tmp preview for visual QA.

Run:  python3 tools/extract_scizor.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'moltres_sheets')
WHITE = np.array([255, 255, 255])
# source filename -> (out key, label). moltres_seq_<key>.png; keys mirror the move files.
SHEETS = [
    ('fiery_wrath.png', 'fw', 'Fiery Wrath'),
    ('air_slash.png',   'as', 'Air Slash'),
    ('dark_pulse.png',  'dp', 'Dark Pulse'),
    ('hurricane.png',   'hr', 'Hurricane'),
]
WHITE_FX = {'air_slash.png', 'hurricane.png'}   # these sheets' white IS the FX (wind/cloud) → keep it; others strip trapped sheet-white
TARGET_BODY = 240
PADX, PADTOP, PADBOT = 26, 22, 14
FEET_PAD = 95          # grow each box down this far to recover the dark feet

def sat_val(a):
    mx = a.max(2); mn = a.min(2)
    return (mx - mn), mx

def find_frames(a):
    """The 4 cells as quadrant boxes in reading order (TL, TR, BL, BR), inset to skip
    the outer border and the centre divider. Moltres's FX (wind, vortices, bursts) is
    huge and often dark/white, so a saturation blob box would crop the FX and bases —
    we keep the whole cell and let the white flood-fill carve out only the sheet."""
    H, W = a.shape[:2]; mx, my, o, c = W // 2, H // 2, 6, 8
    return [(o, o, mx - c, my - c), (mx + c, o, W - o, my - c),
            (o, my + c, mx - c, H - o), (mx + c, my + c, W - o, H - o)]

def cutout(a, box, removewhite=False):
    """Carve one cell: edge-flood ONLY the near-pure-white sheet (tight threshold) so
    pale wind/cloud FX survives, with NO global white key (which used to punch holes
    through the body where white FX crossed it). Keep all remaining content; anchor on
    the saturated body so frames align. Returns (rgba, body_cx, content_h, body_h)."""
    x0, y0, x1, y1 = box
    crop = a[y0:y1, x0:x1].astype(int)
    h, w, _ = crop.shape
    sat, val = sat_val(crop)
    bglike = np.abs(crop - WHITE).sum(2) < 18              # ONLY the flat sheet (~252-255); pale FX (<=~248) survives
    seed = np.zeros((h, w), bool)
    seed[0] = seed[-1] = seed[:, 0] = seed[:, -1] = True
    seed &= bglike
    fg = ~ndimage.binary_propagation(seed, mask=bglike)    # everything not reachable-white from the border
    lab, n = ndimage.label(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n + 1):
        comp = lab == i
        ys, xs = np.where(comp)
        bw = xs.max() - xs.min() + 1; bh = ys.max() - ys.min() + 1
        if len(ys) < 0.0006 * h * w:          continue     # tiny speck / jpeg noise
        if min(bw, bh) <= 14 and max(bw, bh) >= 0.5 * max(h, w) and val[comp].mean() < 110 and sat[comp].mean() < 45:
            continue                                        # thin, long, dark = a stray divider remnant
        keep |= comp
    filled = ndimage.binary_fill_holes(keep)                # fill only small interior holes
    holes = filled & ~keep
    hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        comp = hl == i
        if comp.sum() < 0.0012 * h * w:
            keep |= comp
    if removewhite:                                         # no-white-FX sheets (Dark Pulse, Fiery Wrath):
        keep = keep & ~(np.abs(crop - WHITE).sum(2) < 18)  # strip ALL flat sheet-white (incl. trapped inside the
                                                           # dark vortex) — there's no white FX on these sheets
    fg = keep
    out = np.dstack([crop.astype(np.uint8), (fg * 255).astype(np.uint8)])
    ys, xs = np.where(fg)
    t, b, l, r = ys.min(), ys.max(), xs.min(), xs.max()
    out = out[t:b + 1, l:r + 1]
    body = fg & (sat > 55)                                  # the coloured body (pink flames + purple) for alignment
    if body.any(): byc, bxc = np.where(body); cx = (bxc.min() + bxc.max()) / 2 - l; body_h = float(byc.max() - byc.min())
    else:          cx = (l + r) / 2 - l; body_h = float(b - t)
    return out, cx, float(b - t), body_h

def build(frames, scale, ch, padx=PADX, padbot=PADBOT):
    sized = []
    for rgba, cx, _, _ in frames:
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
        rmw = fname not in WHITE_FX                          # strip trapped sheet-white except on white-FX sheets
        frames = [cutout(a, b, removewhite=rmw) for b in find_frames(a)]
        sheets.append((key, label, frames))
    if not sheets:
        print('No sheets found in', SRC); return
    # scale from the prep-frame BODY height (frame 0, index 3) so Moltres is a consistent
    # size across moves; cell height fits the tallest CONTENT (index 2 = incl. big FX).
    scale = TARGET_BODY / np.median([fr[0][3] for _, _, fr in sheets])
    ch = int(round(max(c_h for _, _, fr in sheets for _, _, c_h, _ in fr) * scale)) + PADTOP + PADBOT
    previews = []
    for key, label, frames in sheets:
        strip, cw = build(frames, scale, ch)
        outp = os.path.join(ROOT, f'moltres_seq_{key}.png')
        strip.save(outp)
        print(f'{label:13s} -> moltres_seq_{key}.png  {strip.width}x{strip.height}  (BOSS_SEQ: cw={cw}, ch={ch})')
        previews.append((label, strip, cw))
    # gridded QA preview: each frame in its OWN uniform bordered cell so columns line
    # up across moves (a plain stack misleads, since cw differs per move). GREEN cells —
    # Moltres is dark purple/black, which vanishes against a dark or pink background.
    from PIL import ImageDraw
    cellw = max(cw for _, _, cw in previews); pad = 8
    sheet = Image.new('RGBA', (cellw * 4 + pad * 5, (ch + pad) * len(previews) + pad), (22, 70, 40, 255))
    dr = ImageDraw.Draw(sheet)
    for r, (label, strip, cw) in enumerate(previews):
        for c in range(4):
            x0 = pad + c * (cellw + pad); y0 = pad + r * (ch + pad)
            dr.rectangle([x0, y0, x0 + cellw, y0 + ch], fill=(70, 200, 110, 255), outline=(255, 255, 255, 255))
            frame = strip.crop((c * cw, 0, (c + 1) * cw, ch))
            sheet.alpha_composite(frame, (x0 + (cellw - cw) // 2, y0))
    sheet.convert('RGB').save('/tmp/moltres_preview.png')
    print('preview -> /tmp/moltres_preview.png')

if __name__ == '__main__':
    main()
