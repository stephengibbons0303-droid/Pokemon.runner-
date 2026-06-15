# Progress / status

Working notes for **Spark Run** (a two-game maths/literacy adventure). All game
code lives in `sparkrunmath.html` (single inline `<script>`). Branch:
`claude/pokemon-math-game-v1-txqzrt`.

Full implemented-feature detail lives in
[`PROGRESS_ARCHIVE.md`](PROGRESS_ARCHIVE.md). This file is the *living* doc:
current status, recent work, open items.

_Last updated: 2026-06-15._

## Current status (snapshot)
- **Two games on one engine**, picked on the start screen (`PACKS`/`selectPack`):
  - **Maths** (older) — written sums, 5 levels × 25 questions, timed-jump skill,
    2-D overlap scoring, speed-run, hearts/pause.
  - **ABC & 123** (younger) — audio recognition: Ash *speaks* a letter/number, the
    child jumps to the matching balloon. 5 levels (1–10 / A–M / N–Z / 11–20 / A–Z),
    talking/celebrating Ash portrait, **Easy** (hold-lane) / **Tricky** (timed)
    toggle. Same Pokémon bosses.
- **Scoring requires the *chosen* lane** (`player.lane === correctLane` + height
  overlap) — passing through a lane no longer scores. **Answer feedback:** correct
  card greens + gold sparkles; wrong card pops like a balloon.
- **L1 Gyarados (lake) & L2 Lucario (dojo)** are full **action duels**: directional
  dodge (low → JUMP ▲ / high → ROLL ◀▶), projectiles that travel to Pikachu, **super
  moves** (Pikachu Thunderbolt 30% / per-boss heavy 30%, both charged + i-frames),
  **heart-based retries**, Ash voice calls ("be careful" / "you did it").
- **L3–L5 are still the classic scrolling-maths boss** — *not yet* upgraded to the
  duel mechanics (top TODO).
- **Spark Friends gallery** (per-pack, saved); **pre-battle announcer** voice
  ("…has done his X… it's <Boss>!"); **3-stage volume** (full/low/mute).
- **Tooling:** `tools/selftest.js` headless guard (now incl. ABC pack + the
  pass-through exploit); `slice_speech.py`/`cutout_bg.py` asset tools;
  `#devjump` dev menu (`DEV` flag).

## Recent work (this session) — *detail → archive*
- **ABC & 123** younger game (audio recognition, content packs, difficulty toggle,
  talking/celebrating transparent Ash portrait); 46 `say_*.mp3` via `slice_speech.py`.
- **Spark Friends gallery** (per-pack saved, auto-show after a win).
- **Duel combat overhaul:** projectiles reach Pikachu, directional dodge, super
  moves (Thunderbolt / per-boss heavy, 30%), heart-based retries, Ash battle voice.
- **Pre-battle announcer** + per-boss "it's <Boss>!" + Pikachu/foe cries; intro
  simplified (dropped the Ash↔Pikachu coaching chatter).
- New **Ash battle poses** + new **Waterfall** animation (`cutout_bg.py`); **Lucario
  flip**; power-button icons preloaded.
- **Clearer right/wrong feedback** (green sparkle / balloon pop); **scoring lane-choice
  fix** (+ selftest guard). **3-stage volume**.

## Open items / TODO
**Next session (priority):**
- **Bring L3 / L4 / L5 battle scenes in line with L1 / L2.** Make the classic maths
  bosses (Venusaur, Scizor, Galarian Moltres) play as **action duels** with the same
  gameplay/mechanics: per-boss duel config (`cfg.duel` + a `drawXBack` scene,
  `atkSeqs`, `heavy`/`heavyName`, `roar`/`cry`, intro `lines`), directional dodge,
  travelling projectiles, super moves, retries. Needs each boss's duel scene + move
  / cry assets.
- **Spark Friends page** — add a couple of features (e.g. tap a caught Pokémon to
  hear its cry / preview its moves; nicer layout; drop-in `ACH_ANIM` strips).
- **More audio clips + general tidying.**

**Carried over:**
- **On-device tablet test pass** — controls scale to a ~46 CSS-px tap floor
  (`rowDiameter`/`RENDER_SCALE`); dodge arrows bottom-left, move bar bottom-right;
  `layoutTopButtons`. Confirm reach/size feel; also eyeball the new pixel-art Ash
  poses next to the vector scenes, and the prompt-box framing.
- **Balance tuning** — supers 30%, base hits 10/15, boss heavy ~25% of attacks,
  ~2s charge; Pikachu still out-DPSes the boss (attacks far more often). Dive heals
  45% at 30% HP; evade/dodge 28%; rile at 18%. All dial-by-feel.
- **Earthquake** sheet missing — Gyarados's 4th move falls back to a static image.
  Same for non-sequenced Pikachu moves (Charm, Reflect, G-Max) until 2×2 sheets land.
- **L4–L5 maths pools** — could get the curated 3-stage treatment like L1–L3 (L4 is
  still procedural ×, overlaps L3; L5 is the procedural +/−/× mix).
- Possible: weight the speed-run move mix; mid-level checkpoint.

## Layout quick-reference (in `sparkrunmath.html`)
- Content/packs: `PACKS`/`selectPack`, maths `LEVELS`/`L1..3_POOLS`/`makeChoices`,
  ABC `recogLevel`/`pickChoices`/`sayGlyph`/`SAY_CLIPS`.
- Scoring & feedback: the play/boss lock blocks (`touched`, `gate.result`),
  `overlapsBalloon`, `drawCard`, `cardCheer`/`cardPop`, `correctPop`/`oopsPuff`.
- Gallery: `drawDex`/`drawMonInSlot`, `openDex`/`closeDex`, `caught`/`catchMon`,
  `ACH_ANIM`, `dexBtnRect`.
- Duel logic: `enterBoss`(+retry)/`bossFail`, `buildIntro`/`tickIntro`,
  `castMove`/`applyPikaHit`, `foeAttack`/`bossFire`/`startHeavy`/`foeHit`/`doDodge`,
  `rileUp`, `updateDuel`; `BOSSES` (`duel`/`heavy`/`atkSeqs`/`roar`/`cry`).
- Duel/boss drawing: `drawDuel`/`drawDojoBack`, `drawBossSprite`, `drawDuelBars`,
  `drawMoveBar`, `drawDodgeButtons`/`drawDodgePrompt`, `drawFoeShots`/`drawShots`,
  `drawAsh`, `drawAshPrompt`.
- Pre-battle audio: `preBattleClip`/`BOSS_VS_CLIP`/`PRE_DUR`, `bossIntroQueue`,
  `bossHold`; Ash voice `ashWarn`/`ashSay`.
- Audio/volume: `Audio8` (`cycleVol`/`volMul`), `voice` (channels
  foe/pika/ash/prompt).
- Input: `onPress`, `keydown` (`MOVE_KEYS`); dev menu (`DEV`/`devJump`/`#devjump`).
