# Progress archive — implemented-feature detail

Accumulated detail for **Spark Run — Maths Adventure** (all game code in
`sparkrunmath.html`). This is the stable record of *what's built and how*; the
living status, TODOs and recent work stay in [`PROGRESS.md`](PROGRESS.md).

## Maths runner (levels 1–5)
- 25 questions per level on a within-level difficulty ramp (`LEVELS`).
- L1 addition & L2 subtraction each run in 3 fixed-difficulty stages (random,
  non-repeating draws from `L1_POOLS`/`L2_POOLS` via `drawQ`/`QBAG`): Q1–8 single
  digit, Q9–17 teens/twenties, Q18–25 two-digit (no carry/borrow, <100). L3 +/−
  mix; L4 ×; L5 +/−/× (× on 6–9 tables).
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

## Scenery
- Multi-layer parallax driven by one `world` scroll accumulator.
- Per-level scenes (`SCENES`): meadow+snowy mountains, orchard, bubble bay,
  crystal cave, star summit. Snow-cap peaks, clouds, bubbles, crystals.
- 8-bit post-pixelation was tried and **reverted** (caused scrolling shimmer).

## No-maths duels (config-driven)
A boss becomes an action duel by setting `cfg.duel` (`'lake'` for Gyarados,
`'dojo'` for Lucario); without it the level keeps the classic scrolling-maths
boss. Scene, low-HP mechanic, dodge style, the intro roar (`cfg.roar`), attack
strips (`cfg.atkSeqs`) and the power-up strip (`cfg.powerSeq`) are all per-boss.
L3–L5 are still classic.

### Level 1 boss — Gyarados lair duel (`duel:'lake'`)
- **Scene:** lake with a back basin + front surface so Gyarados sits **partly
  submerged**; he **rises out of the lake** on entry. Ash on the left bank,
  Pikachu beside him (crouched stance, not running).
- **Scripted intro** (`buildIntro`/`tickIntro`, generic; **simplified**): the
  pre-battle announcer lines lead (see *Pre-battle announcer*), then Pikachu's
  battle cry → the foe's cry → **"Ready to battle?"** prompt. Voice + Ash poses
  only, no dialogue box. Sounds are sequenced with gaps and channelled (no
  overlap). Tap skips the cutscene to the prompt. (The old three Ash↔Pikachu
  coaching exchanges were removed.)
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

## Duel combat — supers, directional dodge, projectiles, retries
Built on the L1/L2 duel plumbing; all of this is **shared** by both duel bosses.
- **Boss attack reaches Pikachu.** `foeAttack` spawns a travelling blast
  (`bossFire` → `foeShots`, drawn by `drawFoeShots`): water (lake) / aura (dojo),
  tinted by the move colour, launched from the boss's mouth and arriving as the
  dodge window closes; `duelSplash` on impact. Cleared on faint.
- **Directional dodging.** Each attack is **low** (straight → JUMP ▲) or **high**
  (lobbed arc → ROLL ◀/▶, bigger `foeShots.arc`). `doDodge` checks the dodge vs
  `boss.atkArc`; the wrong button (or none) lets the hit land (`foeHit`). The
  correct dodge button(s) light up (`drawDodgeButtons`) and the prompt shows
  JUMP!/ROLL!. Boss attacks every ~2.4s (basic) / ~3.2s (special).
- **Super moves (30%, `SUPER_DMG`).** Pikachu's **Thunderbolt** is a charged super
  (`castMove` → `pikaCast.super`): ~1.6s glow+shake wind-up, **invulnerable while
  charging** (`foeHit` no-ops), not evaded, 30% damage. Each boss has a signature
  **heavy** (`cfg.heavy`/`heavyName`: Gyarados Waterfall, Lucario Aura Sphere) it
  occasionally charges (`startHeavy` → `boss.charging`, ~2s glow+shake, **can't be
  damaged** — `canTarget` excludes it), then unleashes a telegraphed 30% attack.
  Casting a *normal* special can't dodge (the hit lands); only Thunderbolt grants
  i-frames. Per-hit base damage stays symmetric (10 basic / 15 special).
- **Ash voice in battle:** "Be careful, Pikachu!" (`ash_careful.mp3`, `ashWarn`,
  4s cooldown) on incoming specials/heavy; "You did it!" (`ash_youdidit.mp3`) on a
  boss faint (duel and classic).
- **Retries.** Losing a duel (energy → 0) spends one **heart** and restarts the
  fight fresh, no cutscene (`bossFail` → `enterBoss(retry)`); attempts = hearts
  remaining, game over only at 0. Hearts show in the duel HUD. Classic maths
  bosses already spend a heart per wrong answer (continuous attempts).

## Two games — content packs
The same runner/boss engine drives two packs, picked on the start screen
(`PACKS`, `selectPack`, `LEVELS` points at the active pack's levels):
- **Maths** (older): the original written sums (unchanged).
- **ABC & 123** (younger, audio recognition, `PACK.audio`): no reading. Ash's
  portrait sits in the prompt box and **speaks** a letter/number (`sayGlyph` →
  `say_<x>.mp3`, device speech-synth fallback); the child jumps to the matching
  balloon. Levels (8 questions each): 1–10 / A–M / N–Z / 11–20 / A–Z
  (`recogLevel`/`pickChoices`; gens return their own `choices` + an `audio` key).
  - **Ash portrait** (`drawAshPrompt`, transparent cut-outs over the scene):
    closed `ash_say0` → opens `ash_say1` **once** for the spoken clip
    (`promptTalking`) → closed; **celebration** `ash_yay` for a moment on a correct
    answer (`ashYayT`). Tap the box to replay.
  - **Jump difficulty** toggle (round button by the ABC banner, saved `abcEasy`,
    default **Easy**): Easy hops to the tapped lane and *holds* it (taps cycle
    ground→mid→high, no timed arc); Tricky = the timed-jump arc. Maths is always
    timed.
- The duels (L1/L2) and classic bosses are shared by both packs.

## Spark Friends gallery
- Every Pokémon you defeat joins a gallery, **saved per pack** (`localStorage`,
  key `sparkrun.caught.v1.<pack>`, `caught` set; `bossDefeated` → `catchMon`).
- A `dex` state/screen (`drawDex`/`drawMonInSlot`), opened from the start-screen 🏆
  button (`openDex`) and shown automatically after a win with the fresh catch
  highlighted (`newlyCaught`, sparkles); uncaught slots show a `?` silhouette.
- Per-Pokémon animations are drop-in: a horizontal frame strip + an `ACH_ANIM[name]`
  entry (same `cw`/`ch`/`n` convention as the move strips); otherwise the static
  boss sprite with an idle bob.

## Pre-battle announcer (voice)
Before each boss: "<player> has done his maths/numbers/letters…" → "it's <Boss>!"
→ the intro. First line by pack/level (`ash_pre_maths/numbers/letters.mp3`, level
`kind`); second per boss (`BOSS_VS_CLIP` → `ash_its_*.mp3`). Duels prepend both as
intro beats; classic bosses drain a `bossIntroQueue` clip-by-clip (`bossHold`,
per-clip `PRE_DUR`) before the first question. All announcer clips preloaded.

## Answer feedback & scoring
- **Correct** card turns green, glows, and bursts gold sparkles (`cardCheer` +
  orbiting twinkles in `drawCard`). **Wrong** picked card **pops** like a balloon
  into themed fragments (`cardPop`; `drawCard` skips the popped card). Green shows
  **only on a correct answer**; the miss resolves a bit quicker (0.6s vs 0.9s).
  Applies to the runner and classic bosses.
- **Scoring requires the *chosen* lane.** A hit needs `player.lane === correctLane`
  **and** the height overlap — so lanes merely passed through (rising or falling
  back from a higher lane) no longer score. Guarded by a selftest case.

## Volume
- Three-stage button (`Audio8.cycleVol`/`volMul`): full → low (~32%) → mute →
  full, scaling every output (chiptune, sfx, cheer, voice clips). Icon 🔊/🔉/🔇.

## Audio
- `Audio8` chiptune + `music.mp3`/`music2.mp3` (speed-run crossfade) +
  `levelup.mp3`.
- `voice(file, vol, chan)` one-shot clips with channels `foe`/`pika`/`ash`/`prompt`.

## Dev / testing aids
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
   Lucario's strips use the same approach via `tools/extract_lucario.py` (sources
   under `tools/lucario_sheets/`).

In-game, run/jump/move/boss sheets are sliced by frame at draw time;
`cleanSprite`/`cleanSheet`/`drawTinted` handle per-load fixes (fringe/dark-disc
removal, neighbour-bleed, isolated hit-flash tint).

### Asset tools (`tools/`)
- **`slice_speech.py`** — cuts one recitation recording (A–Z or 1–20) into the
  per-item `say_*.mp3` clips on the silences between items; **refuses** to export
  unless the segment count matches the expected item count (so a run-together take
  fails loudly instead of mislabelling). Used for the ABC voice set.
- **`cutout_bg.py`** — knocks a flat/gradient background out of a portrait PNG
  (edge region-grow + halo cleanup; tunable ref/tolerances). Used for the
  transparent Ash portraits and the Waterfall frames.
- **`extract_lucario.py`** — Lucario move-strip extraction (sources under
  `tools/lucario_sheets/`).
- ffmpeg for these came from the `imageio-ffmpeg` pip package (no system ffmpeg).
