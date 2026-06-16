# Progress / status

Working notes for **Spark Run** (a two-game maths/literacy adventure). All game
code lives in `sparkrunmath.html` (single inline `<script>`). Working branch:
`claude/pokemon-runner-review-kugpr9`.

Full implemented-feature detail lives in
[`PROGRESS_ARCHIVE.md`](PROGRESS_ARCHIVE.md). This file is the *living* doc:
current status, recent work, open items.

_Last updated: 2026-06-16._

## Current status (snapshot)
- **Two games on one engine**, picked on the start screen (`PACKS`/`selectPack`):
  - **Maths** (older) — written sums, 5 levels × 25 questions, timed-jump skill,
    2-D overlap scoring, speed-run, hearts/pause.
  - **ABC & 123** (younger) — audio recognition: Ash *speaks* a letter/number, the
    child jumps to the matching balloon. 5 levels, talking/celebrating Ash, **Easy**
    (hold-lane) / **Tricky** (timed) toggle. Same Pokémon bosses.
- **Scoring requires the *chosen* lane** (`player.lane === correctLane` + height
  overlap). Correct card greens + sparkles; wrong card pops.
- **ALL FIVE bosses are now full action duels** (no-maths, directional dodge: low →
  JUMP ▲ / high → ROLL ◀▶, travelling projectiles, charged supers + i-frames,
  heart-based retries, Ash voice calls). Each boss has its own scene, evade style,
  low-HP trick, signature heavy and **real projectile art**:
  | L | Boss | Scene (`cfg.duel`) | Evade | Low-HP | Heavy | Notes |
  |---|------|------|------|------|------|------|
  | 1 | Gyarados | `lake` (`drawLairBack`+`drawLakeFront`) | submerge | heal (dive) | Waterfall | rises from the water on entry |
  | 2 | Lucario | `dojo` (`drawDojoBack`) | sidestep | enrage | Aura Sphere | real projectiles `luca_proj_*` |
  | 3 | Venusaur | `grove` (`drawGroveBack`) | sidestep | heal (Synthesis, in place) | Frenzy Plant | real projectiles `venu_proj_*` |
  | 4 | Scizor | `crystal` (`drawCrystalBack`) | sidestep | enrage (Swords Dance) | **X-Scissor — melee LUNGE** | `sciz_proj_*`; the body charges in |
  | 5 | Galarian Moltres | `summit` = volcanic perch (`drawSummitBack`) | **soar** (flies higher) | enrage (Fiery Wrath flare) | Dark Pulse | **air boss**: hovers + descends to the perch to attack; `moltres_proj_*` |
- **Pikachu fires real projectile art** too: Quick Attack (the dash sprite **is** the
  lunge), Thunderbolt (beam), Electro Ball + Electroweb (orbs) — `pika_proj_*`.
  Iron Tail / Charm / Reflect / G-Max still use the procedural fallback (no art yet).
- **Spark Friends gallery** (per-pack, saved); **pre-battle announcer**; **3-stage
  volume** (full/low/mute).
- **Tooling:** `tools/selftest.js` headless guard; a family of `extract_*.py` sprite
  tools (see below); `#devjump` dev menu incl. **scene previews** (`scenePreview`).

## Recent work (this session) — *detail → archive*
- **Promoted L3–L5 to full action duels** (the previous top TODO), so all five
  bosses now match L1/L2. Added three new duel scenes — **Venusaur grove**,
  **Scizor crystal cavern**, **Galarian Moltres volcanic perch** (a reworked
  twilight-summit: dark sky, hazy red moon, glowing lava-crater perch, embers).
- **Generalised the duel config** so behaviours mix freely instead of being keyed on
  `dojo`/`lake`: `cfg.evade` (`submerge`|`sidestep`|`soar`), `cfg.lowhp`
  (`heal`|`enrage`), per-scene `duelDrop()`. Existing bosses kept their behaviour
  (fixed a latent bug where the grove foe rose from underground on entry).
- **Real projectiles everywhere.** Wired Pikachu + every boss to fly their actual
  move art via `drawShots`/`drawFoeShots` (sprite + glow tail, `spin`/`flip` flags),
  replacing the procedural blobs. Damage path unchanged (visuals only).
- **Two new mechanics:**
  - **Boss melee lunge** (`bossLunge`/`boss.lungeX`) — Scizor's X-Scissor charges in
    during the wind-up, strikes as the dodge window closes, then retreats; the dash
    sprite *is* the attack.
  - **Air boss** (`cfg.air`, `boss.hoverY`, `HOVER_H`) — Moltres hovers with a
    wing-flap idle (`cfg.fly` = `moltres_fly0/1.png`) and **descends to the perch**
    whenever it winds up / charges / fires, then rises; **soar** evade darts higher.
    `hoverY` feeds the sprite, aim point and projectile origin.
- **Cast-strip width cap** (`W*0.62`) so Moltres's huge Hurricane/Air-Slash FX stay
  on screen.
- **Redid all Lucario cast strips** from clean white-bg sheets, plus full Scizor and
  Galarian Moltres cast sets; added **Scizor + Moltres battle cries** (intro now,
  dodge/attack in-duel).
- **Asset-pipeline hardening** (see below): shared cell geometry per character,
  **feet recovery**, **tight white-only flood** (keeps pale/white FX + white
  bellies), **belly recovery**, **green QA previews** for dark sprites.

### Sprite-extraction pipeline (`tools/`)
All move/projectile art comes from **white-background 2×2 (or single) sheets**,
cut to transparent PNGs by per-character scripts. Key lessons baked in:
- **Tight white-only flood** (`|crop-255| < ~18`, **no** global near-white key):
  edge-flood removes only the flat sheet, so pale wind/cloud FX (Hurricane, Air
  Slash, Vacuum Wave) and near-white markings survive. The old global key was
  deleting white FX and punching holes through bodies.
- **Shared geometry per character** — all of a boss's cast strips are scaled by the
  prep-pose body height and built to ONE cell height, so the boss renders the same
  size across every move (in-game maps cell-height → `BOSS_H*1.3`).
- **Feet recovery** (Lucario/Scizor) — saturated-blob boxes stop at the legs, so the
  box is grown downward (clamped to the cell) to keep the dark paws.
- **Belly recovery** (Moltres fly poses) — his pure-white belly = sheet colour and
  opens through the leg gap, so the slit is morphologically closed and the large
  enclosed region added back.
- Scripts: `extract_lucario.py`, `extract_scizor.py`, `extract_moltres.py` (cast
  strips); `extract_luca_proj.py`, `extract_sciz_proj.py`, `extract_moltres_proj.py`,
  `extract_pika_proj.py`, `extract_venu_proj.py` (projectiles); `extract_moltres_fly.py`
  (hover flap); `extract_venusaur.py`. Source sheets in `tools/<mon>_sheets/` (and
  `tools/lucario_redo/`). Previews → `/tmp/*_preview.png` (green bg for dark sprites).

## Open items / TODO
**Playtest pass (this session's output — needs in-game eyes):**
- **Projectile orientation/`flip`** per move — only obviously-directional ones were
  set (Venusaur Earth Power, Lucario Aura Sphere/Dragon Pulse, Moltres Hurricane was
  pre-rotated). Others left un-flipped; confirm none fly backwards.
- **Scizor X-Scissor lunge** — reach/speed feel (`reach = BOSS_X-PLAYER_X-210`).
- **Moltres** — hover height (`HOVER_H=110`) + descend ease (`dt*4`), wing-flap speed
  (~0.42s/frame), and that the volcano/lava-perch reads well.
- General: scene moods, boss on-screen sizes vs Pikachu, feet/baselines.

**Art still outstanding:**
- **Pikachu Iron Tail / Charm / Reflect / G-Max** — no projectile/anim art yet
  (procedural fallback). Quick Attack/Thunderbolt/Electro Ball/Electroweb done.
- **Gyarados Earthquake** sheet missing — 4th move falls back to a static image.
- Gyarados has **no projectile art** yet (still procedural water blasts); could get
  the same `*_proj_*` treatment if sheets arrive.

**Carried over:**
- **On-device tablet test pass** — controls scale to a ~46 CSS-px tap floor; confirm
  reach/size feel; eyeball pixel-art Ash vs the vector scenes.
- **Balance tuning** — supers 30%, base hits, heavy ~25% of attacks, ~2s charge;
  heal 45% at 30% HP; evade 28%; rile at 18%. New knobs: lunge reach, `HOVER_H`,
  descend ease, FX width cap. All dial-by-feel.
- **Spark Friends page** extras (tap to hear a cry / preview moves; nicer layout).
- **L4–L5 runner maths pools** still procedural (the *runner* leading to the boss;
  the boss itself is now a no-maths duel). Could get the curated 3-stage treatment.

## Layout quick-reference (in `sparkrunmath.html`)
- Content/packs: `PACKS`/`selectPack`, maths `LEVELS`/`L1..3_POOLS`/`makeChoices`,
  ABC `recogLevel`/`pickChoices`/`sayGlyph`/`SAY_CLIPS`.
- Scoring & feedback: play/boss lock blocks, `overlapsBalloon`, `drawCard`,
  `correctPop`/`oopsPuff`.
- Gallery: `drawDex`/`drawMonInSlot`, `openDex`/`closeDex`, `caught`/`catchMon`.
- **Boss config:** `BOSSES` — per boss `duel` (scene key), `evade`, `lowhp`, `air`,
  `fly`, `atkSeqs`, `powerSeq`, `heavy`/`heavyName`, `roar`/`cry`/`roar2`, `lines`,
  and `moves[]` (`proj`/`spin`/`flip`/`lunge`/`col`). Cast strips registered in
  `BOSS_SEQ` (keyed on the move file → `*_seq_*.png`, `cw`/`ch`).
- **Duel logic:** `enterBoss`(+retry)/`bossFail`, `buildIntro`/`tickIntro`,
  `castMove`/`applyPikaHit`/`pikaFire`, `foeAttack`/`bossFire`/`startHeavy`/`foeHit`/
  `doDodge`, `rileUp`, `updateDuel` (evade / low-HP / **lunge** / **air hover-descend**
  / charge / cadence). State: `boss.subY`/`sideX`/`lungeX`/`hoverY`/`diveState`,
  `bossLunge`, `dodgeWin`/`dodgeMax`, `HOVER_H`, `duelDrop()`.
- **Duel/boss drawing:** `drawDuel` (scene switch via `cfg.duel || scenePreview`),
  scenes `drawLairBack`/`drawLakeFront`/`drawDojoBack`/`drawGroveBack`/`drawCrystalBack`/
  `drawSummitBack`; `drawBossSprite` (idle / `cfg.fly` flap / cast `aseq` w/ width cap /
  lunge sprite, all `cfg.flip`-aware, `hoverY`-aware); `drawShots`/`drawFoeShots`
  (sprite + glow tail), `drawDuelBars`, `drawMoveBar`/`drawPikaDash`,
  `drawDodgeButtons`/`drawDodgeWave`/`drawDodgePrompt`, `drawAsh`.
- Pre-battle audio: `preBattleClip`/`BOSS_VS_CLIP`/`PRE_DUR`, `bossIntroQueue`.
- Audio/volume: `Audio8` (`cycleVol`/`volMul`), `voice` (foe/pika/ash/prompt).
- Input/dev: `onPress`, `keydown` (`MOVE_KEYS`); `DEV`/`devJump`/`#devjump` incl.
  `scene:<n>` previews + `DUEL_SCENE_BY_LEVEL`.
