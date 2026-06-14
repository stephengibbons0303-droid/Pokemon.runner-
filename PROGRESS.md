# Progress / status

Working notes for **Spark Run — Maths Adventure**. All game code lives in
`sparkrunmath.html` (single inline `<script>`). Branch:
`claude/pokemon-math-game-v1-txqzrt`.

_Last updated: 2026-06-14._

## Done

### Maths runner (levels 1–5)
- 25 questions per level on a within-level difficulty ramp (`LEVELS`).
- L1 addition (eased: `1+n` → single digits → two-digit no-carry → round
  doubles); L2 subtraction; L3 +/− mix; L4 ×; L5 +/−/× (× on 6–9 tables).
- 3 hearts, refilled at the start of each level (shared with that level's boss).
- Correct answer placed in a **uniformly random** lane (`makeChoices`).
- Speed run (×1.5, ⅓ less time) on a 5-streak — difficulty unchanged.
- Wrong answer: dazed Pikachu wobble + dust/stars (`oopsPuff`).
- Pause button + `P`/`Esc`; music pauses too.
- **Timed jump (skill).** A tap launches a real arc — gentle eased rise
  (`RISE_EASE`) → brief apex hover (`JUMP_HANG`) → gravity-accelerated, steeper
  fall (`JUMP_GRAV`). Pikachu no longer *holds* the lane: you must jump so he
  meets the answer balloon as it passes. Double-tap = double jump to the high
  lane; you can re-jump to re-time while a card approaches. The duel dodge-hop is
  unaffected (separate code path; `player.jumping` gates the arc).
- **Scoring = 2-D pass-over overlap (forgiving).** Two parts:
  - *Vertical:* a hit needs Pikachu's catch band (`PIKA_REACH_UP 52` /
    `PIKA_REACH_DN 42` up his body, since his y-anchor sits near his feet) to
    overlap the balloon band (`overlapsBalloon`). Much more of the character
    counts than a single point.
  - *Horizontal/time:* the hit locks the **instant** Pikachu's band overlaps the
    **correct** balloon while it's passing over him (sprites overlap within
    `±(CARD_W/2 + PIKA_HALF_W 36)`) — responsive and forgiving (pre-positioned,
    on-arrival, and reaction-late jumps all register). A miss only locks once the
    balloon has fully passed without contact. You still miss if you never reach
    the lane.
  Tuning knobs: `RISE_EASE 9`, `JUMP_HANG 0.44`, `JUMP_GRAV 3400`,
  `PIKA_REACH_UP/DN`, `PIKA_HALF_W` — all first-pass, dial by feel.

### Scenery
- Multi-layer parallax driven by one `world` scroll accumulator.
- Per-level scenes (`SCENES`): meadow+snowy mountains, orchard, bubble bay,
  crystal cave, star summit. Snow-cap peaks, clouds, bubbles, crystals.
- 8-bit post-pixelation was tried and **reverted** (caused scrolling shimmer).

### No-maths duels (config-driven)
A boss becomes an action duel by setting `cfg.duel` (`'lake'` for Gyarados,
`'dojo'` for Lucario); without it the level keeps the classic scrolling-maths
boss. Scene, low-HP mechanic, dodge style, the intro roar (`cfg.roar`), attack
strips (`cfg.atkSeqs`) and the power-up strip (`cfg.powerSeq`) are all per-boss.
L3–L5 are still classic.

### Level 1 boss — Gyarados lair duel (`duel:'lake'`)
- **Scene:** lake with a back basin + front surface so Gyarados sits **partly
  submerged**; he **rises out of the lake** on entry. Ash on the left bank,
  Pikachu beside him (crouched stance, not running).
- **Scripted intro** (`buildIntro`/`tickIntro`, generic): three Ash↔Pikachu
  coaching exchanges (Ash encourages, Pikachu replies each time) → the foe roars
  and Pikachu answers → **"Ready to battle?"** prompt. Voice + Ash poses only,
  no on-screen dialogue box. Sounds are sequenced with gaps and channelled (no
  overlap). Tap skips the cutscene to the prompt.
- **Energy bars** (0–100): Pikachu yellow (left), Gyarados blue (right); red at
  ≤10%. Hearts/charge meter hidden in the duel.
- **Combat:** basic move = instant / 10% dmg; special = ~0.55s wind-up / 15%.
  Gyarados attacks the same (basic short tell / special long tell). Foe wind-up /
  dodge window ~1.15s (basic) / 1.8s (special). Gyarados **submerge-dodges**
  (~28%) and, once at ≤30% HP, **dives → heals ~45% → re-emerges stronger**
  (power ×1.35, plays Dragon Dance). Pikachu at ≤18% gets an **angry rile-up**
  (+24% energy, once).
- **Move delivery:** each Pikachu move travels to the boss (`pikaFire` →
  `bossAimPoint`/`bossImpact`): `bolt` (Thunderbolt, G-Max) = lightning arc,
  `orb` (Electro Ball, Electroweb) = a flying energy ball (`shots`/`drawShots`),
  `dash` (Quick Attack, Iron Tail) = Pikachu lunges in (`pikaLunge`, duel only).
- **Scroll freeze:** the `world` scroll stops during a duel (it's a stand-off),
  so the foreground grass doesn't slide; lake ripples shimmer on a clock instead.
- **Controls (both always on during battle):** 3 dodge arrows hug the
  **bottom-left** (`◀ ▲ ▶`, any one dodges; they light up while a foe attack
  winds up and dim otherwise); move buttons hug the **bottom-right** (icons +
  `FAST`/`POWER` + `Z X C V B` key chips). Keyboard ←/→/↑ also dodge.
- **Animations:** Pikachu 4-frame move sequences (`pika_seq_*`); real 4-frame
  dodge roll (`pika_roll*`); Gyarados Dragon Dance / Waterfall / Ice Fang
  (`gyara_seq_*`). Ash poses (ready/point/punch) driven by battle beats.
- Removed the drawn "serpent placeholder" — nothing draws until the real sprite
  loads.

### Level 2 boss — Lucario dojo duel (`duel:'dojo'`)
- **Scene** (`drawDojoBack`): a shoji-screen training hall — paper wall in a
  dark-wood lattice, a rising-sun banner and two lanterns up top, a plank floor.
  Lucario **stands** on the floor (`DOJO_DROP`, no water/submersion).
- **Dodge:** instead of submerging he **sidesteps** (`boss.sideX`, ~28%) — a
  quick lateral shift, left or right.
- **Low-HP:** at ≤30% energy he uses **Swords Dance** once — power ×1.35, **no
  heal** (an enrage, not a recover); plays the `luca_energy` clip and the Flash
  Cannon strip as the flourish (`cfg.powerSeq`).
- **Moves:** Aura Sphere / Flash Cannon / Dragon Pulse / Vacuum Wave animate from
  `luca_seq_*` (extracted by `tools/extract_lucario.py`), cycled via `cfg.atkSeqs`.
- **Voice:** `luca_growl` (intro/attacks), `luca_aura` (dodge/faint),
  `luca_energy` (Swords Dance). **Lines:** aura-themed dojo challenge.
- Shares all duel plumbing with Gyarados; differences are the four `cfg` fields
  plus the `duel==='dojo'` branches in scene/dodge/low-HP.

### Audio
- `Audio8` chiptune + `music.mp3`/`music2.mp3` (speed-run crossfade) +
  `levelup.mp3`.
- `voice(file, vol, chan)` one-shot clips with channels `foe`/`pika`/`ash`.

### Dev / testing aids
- **Fullscreen toggle** — a small DOM `#fsbtn` in the top-left viewport corner
  (Fullscreen API). Purely for testing in a mobile browser; auto-hidden when the
  API is unsupported or when running as an installed PWA (`display-mode:
  standalone`). Refreshes `RENDER_SCALE` on `fullscreenchange`.
- **Dev jump menu** — a DOM `#devjump` `<select>` on the start screen (gated by
  the `DEV` flag, default on; set `false` for release). Jumps straight to any
  level's play section or its boss fight via `devJump(kind, idx)`. Shown only on
  the menu screen.
- **`tools/selftest.js`** — headless guard. Run `node tools/selftest.js` before
  pushing gameplay / load-order changes. It (1) *executes* the inline script
  under DOM/canvas/Audio stubs to catch load-time errors a plain parse misses
  (e.g. const used-before-init), and (2) drives the real `update()` loop to
  assert the scoring rule holds (timed jump onto the correct balloon scores;
  never-jumping for a raised lane misses). Exit 0 = pass, 1 = fail.
- **`.githooks/pre-push`** — runs the selftest and blocks the push on failure.
  Enable in a fresh clone with `git config core.hooksPath .githooks` (it's local
  config, not committed). Skips gracefully if Node is absent; override one push
  with `git push --no-verify`.

## Open items / TODO
- **Tablet test pass (on-device)** — the controls now scale: `rowDiameter`
  enforces a ~46 CSS-px physical-tap floor (via a live `RENDER_SCALE`) and
  `bottomRightRow` anchors both clusters in the bottom-right thumb-zone (dodge
  arrows and the move bar are mutually exclusive, so they share the zone and the
  thumb doesn't travel). The top-corner pause/mute buttons scale to the same
  floor too (`layoutTopButtons`, capped to stay tidy). Button text scales with
  radius. Still needs **real
  hardware play-testing** to confirm reach/size feel; revisit the floor (46px),
  edge pad (`CTRL_PAD`), and zone widths (`W*0.6` / `W*0.74`) from there.
- **Balance tuning** (all first-pass, untested): energy 100 each; dmg 10/15;
  dive at 30% HP heals 45%; submerge-dodge 28%; rile at 18%; wind-ups
  basic 0.85s / special 1.5s; intro ~9s (has skip).
- **Earthquake** sheet missing — Gyarados's 4th move falls back to a static
  image. Same for non-sequenced Pikachu moves (Electroweb, Charm, Reflect,
  G-Max) and the other bosses' moves — they animate only once 2×2 sheets are
  supplied.
- **Other bosses (L3–L5)** are still the classic maths boss; no duels yet
  (deferred by choice). L1 (Gyarados) and L2 (Lucario) are action duels.
- Possible: weight the speed-run move mix; mid-level checkpoint; per-level boss
  question styles for the classic bosses.

## Asset pipeline (how supplied sheets are turned into game assets)

Supplied art often comes as a **2×2 grid sheet** (4 frames) with a title bar and
per-cell labels, on a flat background. Extraction (done offline with Pillow,
then committed as cleaned PNGs) roughly:

1. **Find the character rows** by scanning row-density of "content" pixels
   (yellow for Pikachu; saturated for Gyarados) — titles/labels have none, so
   they fall outside the detected bands.
2. **Crop each cell** to its band, split into left/right halves, shaving the
   inner/outer edges to drop the grid divider lines.
3. **Remove the background:**
   - Gray bg (Pikachu sheets): flood-fill from the crop edges.
   - Dark/black bg (Gyarados sheets): a **global** dark key (near-black →
     transparent) — needed because big effects touch every edge, so edge
     flood-fill can't reach the enclosed background.
4. **Drop label remnants:** remove small components and wide-thin (text-shaped)
   blobs; occasionally a targeted top-crop where a label merged into a bright
   effect (e.g. Waterfall's "Power" frame).
5. **Assemble** the 4 frames into a uniform horizontal strip and record
   `cw`/`ch` in `MOVE_SEQ` / `BOSS_SEQ` (+ on-screen size `h` and anchor `ax`).

In-game, run/jump/move/boss sheets are sliced by frame at draw time;
`cleanSprite`/`cleanSheet`/`drawTinted` handle per-load fixes (fringe/dark-disc
removal, neighbour-bleed, isolated hit-flash tint).

## Layout quick-reference (in `sparkrunmath.html`)
- Maths generators: `LEVELS`, `makeChoices`.
- Scenery: `SCENES`, `drawBackground` and its layer helpers.
- Moves: `PIKA_MOVES`, `MOVE_SEQ`; bosses `BOSSES`, `BOSS_SEQ`.
- Duel logic: `enterBoss`, `buildIntro`/`tickIntro`, `castMove`/`applyPikaHit`,
  `foeAttack`, `doDodge`, `rileUp`, `updateDuel`.
- Duel drawing: `drawDuel`, `drawBossSprite`, `drawDuelBars`, `drawMoveBar`,
  `drawDodgeButtons`, `drawAsh`, `drawRoll`, `drawPikaAttack`.
- Input: `onPress`, the `keydown` handler (`MOVE_KEYS`).
