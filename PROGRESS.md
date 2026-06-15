# Progress / status

Working notes for **Spark Run — Maths Adventure**. All game code lives in
`sparkrunmath.html` (single inline `<script>`). Branch:
`claude/pokemon-math-game-v1-txqzrt`.

Full implemented-feature detail lives in
[`PROGRESS_ARCHIVE.md`](PROGRESS_ARCHIVE.md). This file is the *living* doc:
current status, recent work, open items.

_Last updated: 2026-06-14._

## Current status (snapshot)
- **Maths runner, 5 levels**, 25 questions each, timed-jump skill mechanic,
  forgiving 2-D overlap scoring, speed-run streak bonus, hearts/pause. *(detail
  → archive)*
- **L1–L3 questions** are curated 3-stage pools (`L1_POOLS`/`L2_POOLS`/`L3_POOLS`
  = add / subtract / multiply), random with no repeats per stage. L4–L5 still use
  procedural generators (and L4 also × — likely redefined when its sets arrive).
- **No-maths boss duels** (config-driven via `cfg.duel`): **L1 Gyarados** (lake)
  and **L2 Lucario** (dojo) are full action duels — scripted intro, energy bars,
  move-vs-dodge, per-boss low-HP mechanic, projectiles that travel to the boss.
- **L3–L5 bosses** are still the classic scrolling-maths boss (no duels yet).
- **Achievement gallery ("Spark Friends"):** every Pokémon you defeat joins a
  gallery, **saved across sessions** (`localStorage`, `caught` set). Opened from a
  start-screen button (🏆 counter) and shown automatically with the fresh catch
  highlighted right after a win. Each slot animates via `ACH_ANIM[name]`
  (drop-in frame strip) or falls back to the static boss sprite + idle bob.
- **Tooling:** `tools/selftest.js` headless guard + `.githooks/pre-push`;
  `#devjump` start-screen dev menu (`DEV` flag) to jump to any level/boss.

## Recent work (this session)
- **Two games via content packs** — same runner/boss engine, selectable on the
  start screen. `PACKS.maths` (the original written sums, unchanged) and
  `PACKS.abc` (younger, audio recognition). `LEVELS` now points at the active
  pack; `selectPack()` swaps content + the per-child gallery save
  (`sparkrun.caught.v1.<pack>`).
- **Younger "ABC & 123" game** — Ash *speaks* a letter/number and the child jumps
  to the matching balloon. In the prompt box (top centre, where the sum sits) Ash's
  portrait (transparent cut-out, floats over the scene) **opens his mouth once for
  the spoken clip** (`ash_say0` closed → `ash_say1` open → closed) and swaps to a
  **celebration frame on a correct answer** (`ash_yay.png`); tap the box to replay. Levels: 1–10 / A–M / N–Z / 11–20 / A–Z, 8 questions each, same
  Pokémon bosses. `recogLevel`/`pickChoices` build the content; gens return their
  own `choices` + an `audio` key; `sayGlyph()` plays `say_<x>.mp3` (falls back to
  device speech-synth if a clip is missing) and drives the lip-flap via
  `promptTalking()`.
- **Pre-battle** (simplified) — announcer "…has done his maths/numbers/letters…"
  → "it's <Boss>!" → Pikachu's battle cry → the opponent's (duel bosses only) →
  battle. The old Ash↔Pikachu coaching exchanges were dropped from the intro. Pack/content picks the
  first line (`ash_pre_maths/numbers/letters.mp3` by level `kind`); the second is
  per boss (`BOSS_VS_CLIP` → `ash_its_*.mp3`). Duels prepend both as intro beats;
  classic bosses drain a `bossIntroQueue` (clip-by-clip, `bossHold` per-clip
  `PRE_DUR`) before the first question. All announcer clips are preloaded.
- **ABC jump difficulty** (start-screen toggle, saved `abcEasy`, default Easy) —
  **Easy** hops to the tapped lane and *holds* it (taps cycle ground→mid→high,
  no timed arc) so the child just aligns and waits; **Tricky** is the timed-jump
  arc. Easy reuses the existing non-jumping ease path; scoring is unchanged.
- **Three-stage volume** — the audio button cycles full → low → mute → full
  (`Audio8.cycleVol`/`volMul`), scaling every output.
- **Voice clips** — Ash's recorded A–Z and 1–20 sliced into 46 `say_*.mp3`
  via `tools/slice_speech.py` (silence-split, refuses on a count mismatch).
- selftest extended with a section [4] covering the audio pack.
- **Flipped Lucario** to face Pikachu in the dojo duel (per-boss `flip` flag,
  mirrors idle / hurt / move cut-ins in `drawBossSprite`).
- **Achievement gallery ("Spark Friends")** — new `dex` screen + state. Defeating
  a boss adds it to a persisted `caught` set (`bossDefeated`→`catchMon`), then
  routes through the gallery (`dexReturn` → `levelup`/`won`). Start-screen 🏆
  button (`dexBtnRect`/`openDex`) browses it any time. Slots drawn by
  `drawDex`/`drawMonInSlot`; locked Pokémon show a `?` silhouette. **To add a
  unique animation:** drop a horizontal frame strip and add an `ACH_ANIM[name]`
  entry (same `cw`/`ch`/`n` convention as the move strips) — no other code change.
- Extracted **Lucario** move strips (`tools/extract_lucario.py`, sources under
  `tools/lucario_sheets/`) → `luca_seq_*`.
- Added **Lucario voice clips** (`luca_growl/aura/energy.mp3`).
- Built the **L2 Lucario dojo duel** — generalised the duel system to be
  config-driven; dojo scene, sidestep dodge, Swords-Dance enrage.
- Duel fixes: **scroll freeze** during a duel; **persistent dodge bar**
  (bottom-left) + move bar (bottom-right); **projectiles now reach the boss**
  (bolt / orb / dash via `pikaFire`/`bossAimPoint`); dev jump menu.
- Intro reworked to **three Ash↔Pikachu exchanges → roar → "Ready to battle?"**;
  removed the on-screen dialogue box. Intro beats are now **chained on audio
  completion** (`tickIntro` waits for each clip's `ended` + a gap) so voices
  never overlap; `voice()` returns its `<audio>` element to drive this.
- Duel polish: Pikachu & Ash **planted on the floor, no idle sway**
  (`DUEL_PIKA_DROP`, `still` flag on `drawCreature`, Ash bob removed); lighter
  lair dusk tint so the bank reads clearly.
- **L1 + L2 + L3 questions** converted to the 3-stage curated pools (L3 is now
  multiplication, replacing the old +/− mix; exact-duplicate facts in the
  supplied L3 batch-1/2 lists were dropped so a run never repeats a fact).

## Recent fixes
- **Directional duel dodging** — boss attacks are now **low** (straight → JUMP ▲)
  or **high** (lobbed arc → ROLL ◀/▶); the wrong button (or none) lets the hit
  land, so hits actually connect. The correct dodge button(s) light up and the
  prompt shows JUMP!/ROLL!. High shots lob over (`foeShots.arc`). Boss attacks a
  little more often (`foeTimer` 2.4/3.2s). Per-hit damage is symmetric with
  Pikachu (10 basic / 15 special); shared `foeHit()`.
- **Boss attack now reaches Pikachu** — duel bosses fire a travelling blast
  (`bossFire`/`foeShots`, water at the lake / aura in the dojo, tinted by the
  special's colour) from their mouth to Pikachu, arriving as the dodge window
  closes, with a splash on impact (`drawFoeShots`/`duelSplash`). Previously the
  special only animated on the boss with nothing crossing to Pikachu.
- **Power-button icons preloaded** so they're never blank (incl. dev-jump entry).

## Open items / TODO
- **Tablet test pass (on-device)** — controls scale to a ~46 CSS-px physical-tap
  floor (`rowDiameter` + live `RENDER_SCALE`); dodge arrows now sit bottom-left,
  move bar bottom-right (separate clusters). Top-corner pause/mute scale too
  (`layoutTopButtons`). Still needs **real hardware play-testing** to confirm
  reach/size feel; revisit the floor (46px), `CTRL_PAD`, and zone widths.
- **Balance tuning** (first-pass, untested): energy 100 each; move dmg 10/15;
  dive at 30% HP heals 45%; submerge/sidestep-dodge 28%; rile at 18%; foe
  wind-ups 1.15s/1.8s. Intro now audio-paced (no fixed length).
- **Ash "transparency"** reported in the L1 duel: investigated — the committed
  `ash_*.png` are 100% opaque (binary alpha) and `cleanSprite` removes 0 of his
  pixels, so the asset/code are intact. Lightened the lair dusk tint as the
  likely cause (dimming). If he still looks see-through, suspect a stale
  deployed asset / browser cache, not the source.
- **Earthquake** sheet missing — Gyarados's 4th move falls back to a static
  image. Same for non-sequenced Pikachu moves (Charm, Reflect, G-Max) — they
  animate only once 2×2 sheets are supplied.
- **L3–L5 duels** not built (deferred by choice); L3–L5 bosses are classic maths.
- **L4–L5 question pools** — could get the same curated 3-stage treatment as
  L1–L3 once sets are supplied (L4 is currently still procedural × — overlaps L3,
  so it likely needs redefining; L5 is the procedural +/−/× mix).
- Possible: weight the speed-run move mix; mid-level checkpoint.

## Layout quick-reference (in `sparkrunmath.html`)
- Maths generators: `LEVELS`, `L1_POOLS`/`L2_POOLS`/`L3_POOLS`, `drawQ`/`QBAG`,
  `makeChoices`.
- Scenery: `SCENES`, `drawBackground` and its layer helpers.
- Moves: `PIKA_MOVES`, `MOVE_SEQ`; bosses `BOSSES`, `BOSS_SEQ`.
- Duel logic: `enterBoss`, `buildIntro`/`tickIntro`, `castMove`/`applyPikaHit`,
  `pikaFire`/`bossAimPoint`/`bossImpact`, `foeAttack`, `doDodge`, `rileUp`,
  `updateDuel`.
- Duel drawing: `drawDuel`, `drawDojoBack`, `drawBossSprite`, `drawDuelBars`,
  `drawMoveBar`, `drawDodgeButtons`, `drawShots`, `drawAsh`, `drawRoll`,
  `drawPikaAttack`.
- Input: `onPress`, the `keydown` handler (`MOVE_KEYS`); dev menu wiring at the
  bottom of the script (`DEV`, `devJump`, `#devjump`).
