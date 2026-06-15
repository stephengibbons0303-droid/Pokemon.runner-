#!/usr/bin/env python3
"""Slice a single spoken-recitation recording into per-item clips.

Used to turn one recording of "A B C ... Z" (or "1 2 3 ... 20") into the
individual clips the younger game plays as its audio prompts:
    say_a.mp3 ... say_z.mp3   /   say_1.mp3 ... say_20.mp3

It cuts on the silences between items, so the source MUST have a clear pause
(~0.4s or more) between each spoken item — otherwise the items run together and
the split can't be trusted. The script refuses to export unless the number of
detected voiced segments matches the expected item count, so a bad recording
fails loudly instead of producing mislabelled clips.

ffmpeg: uses the system binary if present, else the one bundled with the
`imageio-ffmpeg` pip package.

Examples:
    python3 tools/slice_speech.py letters.mp3 --set letters --dry-run
    python3 tools/slice_speech.py numbers.mp3 --set numbers --out .
"""
import argparse, re, shutil, subprocess, sys, os

def ffmpeg_bin():
    p = shutil.which('ffmpeg')
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg not found (install ffmpeg, or `pip install imageio-ffmpeg`)")

def duration(ff, f):
    out = subprocess.run([ff,'-i',f], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out)
    h,mn,s = m.groups(); return int(h)*3600+int(mn)*60+float(s)

def voiced_segments(ff, f, dur, noise_db, min_gap, min_len):
    """Return [(start,end), ...] of non-silent spans."""
    out = subprocess.run(
        [ff,'-i',f,'-af',f'silencedetect=noise={noise_db}dB:d={min_gap}','-f','null','-'],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', out)]
    ends   = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)',   out)]
    sil = []
    for st in starts:
        en = next((x for x in ends if x > st), dur)
        sil.append((st, en))
    voiced, t = [], 0.0
    for st, en in sil:
        if st > t + 0.02: voiced.append((t, st))
        t = max(t, en)
    if t < dur - 0.02: voiced.append((t, dur))
    return [(a,b) for a,b in voiced if b - a >= min_len]

SETS = {
    'letters': [chr(c) for c in range(ord('A'), ord('Z')+1)],
    'numbers': [str(n) for n in range(1, 21)],
}
def label_to_name(lbl):
    return 'say_' + (lbl.lower() if lbl.isalpha() else lbl) + '.mp3'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--set', choices=SETS, required=True)
    ap.add_argument('--out', default='.')
    ap.add_argument('--noise', type=float, default=-30.0, help='silence threshold dB')
    ap.add_argument('--gap', type=float, default=0.12, help='min silence length (s) that separates items')
    ap.add_argument('--minlen', type=float, default=0.12, help='drop voiced blips shorter than this (s)')
    ap.add_argument('--pad', type=float, default=0.06, help='lead/tail padding added to each clip (s)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    ff = ffmpeg_bin()
    labels = SETS[a.set]
    dur = duration(ff, a.input)
    segs = voiced_segments(ff, a.input, dur, a.noise, a.gap, a.minlen)

    print(f"source: {a.input}  ({dur:.2f}s)")
    print(f"expected {len(labels)} items, detected {len(segs)} voiced segments")
    for i,(s,e) in enumerate(segs):
        lbl = labels[i] if i < len(labels) else '??'
        print(f"  {i+1:2d} {lbl:>3}  {s:6.2f}-{e:6.2f}  ({e-s:.2f}s)")

    if len(segs) != len(labels):
        print("\nMISMATCH — counts differ, refusing to export.")
        print("The recording likely runs items together. Re-record with a clear")
        print("pause (~0.4s+) between each item, or tune --noise/--gap/--minlen.")
        sys.exit(1)
    if a.dry_run:
        print("\n(dry run — counts match; rerun without --dry-run to export)")
        return

    os.makedirs(a.out, exist_ok=True)
    for (s,e), lbl in zip(segs, labels):
        s2 = max(0, s - a.pad); e2 = min(dur, e + a.pad)
        dst = os.path.join(a.out, label_to_name(lbl))
        subprocess.run([ff,'-y','-i',a.input,'-ss',f'{s2:.3f}','-to',f'{e2:.3f}',
                        '-c:a','libmp3lame','-q:a','4', dst],
                       capture_output=True, text=True)
        print(f"  wrote {dst}")
    print(f"\nExported {len(labels)} clips to {a.out}")

if __name__ == '__main__':
    main()
