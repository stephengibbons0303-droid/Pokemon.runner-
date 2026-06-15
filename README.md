# Spark Run — Maths Adventure

A single-file, browser-based maths runner for ~Year 2/3 (ages 6–8), starring a
Pikachu mascot. The creature auto-runs; the player taps to hop it between three
answer lanes. Clear a level's questions and you face an end-of-level Pokémon in
a battle. Original procedural art, parallax scenery, and a live chiptune,
overlaid with supplied Pokémon/Ash sprite sheets and voice clips.

**Play:** open `sparkrunmath.html` (or `index.html`, which redirects to it).
Hosted via GitHub Pages.

## Two games (pick a player on the start screen)

The same runner/boss engine drives two content packs:

- **Maths** (ages 6–8) — the written-sum game described below.
- **ABC & 123** (little ones) — no reading required. Ash's headshot sits in the
  prompt box and **speaks** a letter or number (tap his face to hear it again);
  the child jumps to the balloon that matches. Numbers **1–20**, uppercase
  **A–Z**, 8 questions per level, same Pokémon bosses. Voice is Ash's recorded
  clips (`say_a.mp3 … say_z.mp3`, `say_1.mp3 … say_20.mp3`), with the device's
  speech-synth as a fallback. Each child keeps their **own** Spark Friends
  gallery.

Add per-Pokémon gallery animations or more spoken sets the same drop-in way as
the rest of the assets (see `ACH_ANIM` and `say_*.mp3` / `tools/slice_speech.py`).

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

## Game progression

A full run is **5 levels**. Each level is a **25-question runner stage** in its
own scene, followed by that level's **boss**. You have **3 hearts**, refilled at
the start of each level (and shared with its boss). The first two bosses are
hands-on **action duels** (no maths); the last three are **classic maths bosses**.

| Level | Scene | Questions (×25) | Boss | Boss battle |
|------:|-------|-----------------|------|-------------|
| 1 | Bloom Meadow  | **Addition** — 3 stages | Gyarados | Action duel (lake) |
| 2 | Orchard Hop   | **Subtraction** — 3 stages | Lucario | Action duel (dojo) |
| 3 | Bubble Bay    | **Multiplication** — 3 stages | Venusaur | Classic maths boss |
| 4 | Crystal Caves | **×** (2/5/10 → 3/4 tables) | Scizor | Classic maths boss |
| 5 | Star Summit   | **+ / − / ×** (× on the 6/7/8/9 tables) | Galarian Moltres | Classic maths boss |

Answers are shown across three lanes with the correct one in a **uniformly
random** lane.

## Question types

For **Levels 1, 2 & 3** the questions are drawn **at random with no repeats**
within a run, from fixed pools split into **three difficulty stages** that step
up as the level goes on. **Levels 4 & 5** use procedural generators that ramp
within the level.

### Level 1 — Addition (Bloom Meadow)

| Stage | Questions | Type | Examples |
|------:|-----------|------|----------|
| 1 | Q1–8   | single digit, answers ≤ 9 | `4 + 3`, `6 + 2`, `1 + 8` |
| 2 | Q9–17  | sums into the teens / twenties | `8 + 7`, `12 + 13`, `19 + 5` |
| 3 | Q18–25 | two-digit + two-digit, no carry, under 100 | `23 + 14`, `83 + 16`, `55 + 33` |

### Level 2 — Subtraction (Orchard Hop)

| Stage | Questions | Type | Examples |
|------:|-----------|------|----------|
| 1 | Q1–8   | single digit, minuend ≤ 10 | `9 − 4`, `10 − 5`, `8 − 3` |
| 2 | Q9–17  | teens / twenties − small, no borrow | `17 − 10`, `25 − 10`, `19 − 8` |
| 3 | Q18–25 | two-digit − two-digit, no borrow | `45 − 23`, `89 − 46`, `98 − 76` |

### Level 3 — Multiplication (Bubble Bay)

| Stage | Questions | Type | Examples |
|------:|-----------|------|----------|
| 1 | Q1–8   | ×2 / ×5 / ×10, small multipliers | `4 × 2`, `3 × 5`, `2 × 10` |
| 2 | Q9–17  | ×2 / ×5 / ×10, multipliers 6–10 | `6 × 2`, `7 × 5`, `9 × 10` |
| 3 | Q18–25 | harder tables (3, 4, 6, 7, 8, 9) | `6 × 6`, `8 × 7`, `9 × 9` |

### Levels 4–5 — procedural (ramp within the level)

- **L4 Crystal Caves** — multiplication only, starting on the 2 / 5 / 10 tables
  and widening to 3 / 4.
- **L5 Star Summit** — a mix of +, − and ×, with × drawing on the harder
  6 / 7 / 8 / 9 tables.

## Bosses & battle scenes

After a level's 25 questions, its boss appears. There are two battle styles.

### Action duels (no maths) — Levels 1 & 2

A bespoke, hands-on fight. A boss opts in via `cfg.duel` — `'lake'` (Gyarados) or
`'dojo'` (Lucario) — and the scene, intro, dodge style and low-HP trick vary per
boss. Flow:

1. **Scripted intro** (`buildIntro`): three Ash↔Pikachu coaching exchanges (Ash
   encourages, Pikachu replies each time) → the foe roars and Pikachu answers →
   **"Ready to battle?"** prompt. Voice + Ash poses, no dialogue box. Tap
   mid-cutscene to skip to the prompt; tap the prompt to start.
2. **Battle:** no questions — pure action. Both sides have an **energy bar**
   (Pikachu yellow top-left, boss blue top-right; red at ≤10%). Empty the boss's
   bar to win; don't let yours hit zero.
   - **Attack:** tap a circular move button (or **Z/X/C/V/B**). **Basic** (Quick
     Attack) fires instantly for ~10%; **specials** (Thunderbolt, Electro Ball, …)
     wind up briefly for ~15%. Each move travels to the boss — a **lightning arc**
     (Thunderbolt), a **flying energy orb** (Electro Ball), or a **dash lunge**
     (Quick Attack).
   - **Dodge:** three arrows sit permanently **bottom-left** — **◀ roll back /
     ▲ jump / ▶ roll forward** (any one dodges; keyboard **←/→/↑**). They light up
     when the foe winds up to attack; a missed dodge costs energy. Move buttons
     sit **bottom-right**, so both control rows are always on screen.
   - **Per-boss tricks:** **Gyarados** (lake) can **submerge-dodge** a hit, and at
     low HP **dives to replenish and re-emerge stronger** (Dragon Dance).
     **Lucario** (dojo) instead **sidesteps**, and at low HP uses **Swords Dance**
     — a one-time enrage (power up, no heal). Pikachu, when low on energy, gets an
     **angry rile-up** that restores some bar.
   - Ash coaches from the side (pose + voice on key beats).

### Classic maths bosses — Levels 3–5

The boss appears and **questions keep coming** (drawn from the hard end of the
level's range). It's the same jump-to-answer runner mechanic, but now:

- A **correct answer** fires Pikachu's **equipped move** at the boss for damage.
  You manage a **charge meter**: stronger moves cost charge, while Quick Attack /
  Charm refund it — so you pick when to unload your big hits.
- A **wrong answer** costs a **heart** (unless a shield move soaks it).
- Empty the boss's **HP bar** to win. Boss HP scales with the level (roughly
  10 at L3 up to ~16 at L5).
- Bosses: **Venusaur**, **Scizor**, **Galarian Moltres** (their move cut-ins
  appear when they strike).

**Cast:** Ash (4 poses), Pikachu (run / jump / roll / 4 move sequences), Gyarados
(idle + Dragon Dance / Waterfall / Ice Fang), Lucario (idle/hurt + Aura Sphere /
Flash Cannon / Dragon Pulse / Vacuum Wave), plus Venusaur, Scizor and Galarian
Moltres.

## Controls summary

| Action | Touch | Keyboard |
|--------|-------|----------|
| Hop lane / advance | tap | Space / ↑ |
| Pause | ❚❚ button | P / Esc |
| Duel: dodge | ◀ ▲ ▶ buttons (bottom-left) | ← / ↑ / → |
| Duel: moves 1–5 | circular buttons (bottom-right) | Z X C V B |

> **Dev tip:** a `#devjump` dropdown on the start screen (enabled by the `DEV`
> flag) jumps straight to any level's play stage or boss fight, for testing.

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
  `galmoltres.png`; Gyarados move animations `gyara_seq_dd/wf/if.png`; Lucario
  `luca_seq_as/fc/dp/vw.png`.
- **Ash:** `ash_ready/point/punch/neutral.png`.
- **Audio:** music `music.mp3`, `music2.mp3`, `levelup.mp3`; Gyarados
  `gyara_roar/roar2/cry.mp3`; Lucario `luca_growl/aura/energy.mp3`; Pikachu
  `pika_voice/cry/thunder/angry.mp3`; Ash
  `ash_hey/battlehuh/wannabattle/spirit/dobest/counton.mp3`.

See `PROGRESS.md` for current status and open items, and `PROGRESS_ARCHIVE.md`
for full implemented-feature detail and the sprite-sheet extraction pipeline.
