# Spark Run — Maths Adventure

A single-file, browser-based maths runner for ~Year 2/3 (ages 6–8), starring a
Pikachu mascot. The creature auto-runs; the player taps to hop it between three
answer lanes. Clear a level's questions and you face an end-of-level Pokémon in
a battle. Original procedural art, parallax scenery, and a live chiptune,
overlaid with supplied Pokémon/Ash sprite sheets and voice clips.

**Play:** open `sparkrunmath.html` (or `index.html`, which redirects to it).
Hosted via GitHub Pages.

## How to play

- **Runner (levels 1–5):** the creature auto-runs and three answers float at the
  ground / middle / high lanes. **Tap / Space / ↑** to jump (tap twice to
  double-jump to the high lane). The jump is a timed arc — rise, a brief hover,
  then a steeper drop — so **time it to be at the correct answer's height when
  the card reaches you** (a short grace window keeps it forgiving). A correct
  answer scores; a wrong one costs a heart.
- **Speed run:** a streak of 5 correct triggers a faster "Speed Run" — same
  question difficulty, just ~⅓ less time to think (×1.5 gate speed).
- **Pause:** the ❚❚ button (top-left of the mute button), or **P / Esc**.
- **Mute:** 🔊 button (top-right).

### Maths design

Each level is a **25-question run**, then a boss. Difficulty ramps within the
level (per `LEVELS` in the source):

| Level | Scene | Operation |
|------:|-------|-----------|
| 1 | Bloom Meadow | Addition (eases in: `1+n` → single digits → two-digit no-carry → round doubles). Boss-style ramp ends with two-digit + single-digit crossers. |
| 2 | Orchard Hop | Subtraction only |
| 3 | Bubble Bay | Mix of + and − (two-digit, carry/borrow) |
| 4 | Crystal Caves | Multiplication only (2/5/10, widening to 3/4) |
| 5 | Star Summit | Mix of +, −, × (× uses the 6/7/8/9 tables) |

Answers are shown across three lanes with the correct one in a **uniformly
random** lane.

## The no-maths boss duels (Levels 1 & 2)

Levels 1 and 2 cap with a bespoke **action duel** instead of a maths boss
(Levels 3–5 still use the classic scrolling-maths boss). A boss opts in via
`cfg.duel` — `'lake'` (Gyarados) or `'dojo'` (Lucario) — and the scene, intro
lines, dodge style and low-HP mechanic vary per boss. Flow:

1. **Scripted intro** (`buildIntro`): the foe greets → Pikachu responds → the
   foe warns → Pikachu fires up → Ash encouragement → **"Ready to battle?"**
   prompt. Each line shows in a dialogue box. Tap mid-cutscene to skip to the
   prompt; tap the prompt to start.
2. **Battle:** no questions. Energy bars for both (Pikachu yellow top-left,
   Gyarados blue top-right; red at ≤10%).
   - **Attack:** tap a circular move button (or **Z/X/C/V/B**). **Basic**
     (Quick Attack) fires instantly for 10%; **special** (Thunderbolt, Electro
     Ball, …) has a short wind-up for 15%. Pikachu's moves play 4-frame
     animations.
   - **Dodge:** when the foe winds up, three arrows appear — **◀ roll back /
     ▲ jump / ▶ roll forward** (any one dodges; keyboard **←/→/↑**). A missed
     dodge costs energy.
   - **Per-boss tricks:** **Gyarados** (lake) can **submerge-dodge** a hit, and
     at low HP **dives to replenish and re-emerge stronger** (Dragon Dance).
     **Lucario** (dojo) instead **sidesteps** to dodge, and at low HP uses
     **Swords Dance** — a one-time enrage (power up, no heal). Pikachu at low
     energy gets an **angry rile-up** that restores some bar.
   - Ash coaches from the side (pose + voice on key beats).

Cast: Ash (4 poses), Pikachu (run / jump / roll / 4 move sequences), Gyarados
(idle + Dragon Dance / Waterfall / Ice Fang sequences), Lucario (idle/hurt +
Aura Sphere / Flash Cannon / Dragon Pulse / Vacuum Wave sequences).

## Controls summary

| Action | Touch | Keyboard |
|--------|-------|----------|
| Hop lane / advance | tap | Space / ↑ |
| Pause | ❚❚ button | P / Esc |
| Duel: dodge | ◀ ▲ ▶ buttons | ← / ↑ / → |
| Duel: moves 1–5 | circular buttons | Z X C V B |

## Tech

- **One file:** `sparkrunmath.html` — all game logic in a single inline
  `<script>`, rendered to a fixed **960×540** canvas scaled to fit (landscape;
  a rotate prompt shows in portrait). No build step, no dependencies.
- **Procedural visuals:** parallax scenery (`SCENES`, one per level), a chiptune
  + mp3 tracks (`Audio8`), particle FX.
- **Supplied assets** are PNG sprite sheets / single images and mp3 voice clips
  (see below). Sheets are sliced/cleaned at load:
  - `cleanSprite` — flood-fills transparent/fringe (and, for `DARKBG` sprites,
    a baked dark disc) from sprite edges.
  - `cleanSheet` — keeps the largest blob per run/jump frame (drops neighbour
    bleed).
  - `drawTinted` — isolated red hit-flash so it doesn't flood the bounding box.
- **Audio channels:** `voice(file, vol, chan)` keeps foe/Pikachu/Ash clips from
  talking over themselves.

### Key assets

- **Mascot:** `pikachu-run.png`, `pikachu-jump.png`, `pikachu-celebrate.png`,
  `pika_roll0..3.png`.
- **Pikachu move animations (4-frame strips):** `pika_seq_qa/tb/eb/it.png`;
  round button icons `pika_btn_*.png`; legacy single move art `pika_*.png`.
- **Bosses:** `gyarados.png`, `lucario.png`, `venusaur.png`, `scizor.png`,
  `galmoltres.png`; Gyarados move animations `gyara_seq_dd/wf/if.png`.
- **Ash:** `ash_ready/point/punch/neutral.png`.
- **Audio:** music `music.mp3`, `music2.mp3`, `levelup.mp3`; Gyarados
  `gyara_roar/roar2/cry.mp3`; Lucario `luca_growl/aura/energy.mp3`; Pikachu
  `pika_voice/cry/thunder/angry.mp3`; Ash
  `ash_hey/battlehuh/wannabattle/spirit/dobest/counton.mp3`.

See `PROGRESS.md` for current status, open items, and how the sprite-sheet
extraction pipeline works.
