#!/usr/bin/env node
/*
 * Headless self-test for sparkrunmath.html.
 *
 * The game is a single HTML file with one inline <script>. There's no build and
 * no browser here, so this harness:
 *   1. Extracts the inline script and EXECUTES it under DOM/canvas/Audio stubs
 *      (a plain parse misses load-time errors like "use before initialization").
 *   2. Drives the REAL update() loop to assert the core scoring rule still holds:
 *      a timed jump onto the correct answer balloon registers a hit, and never
 *      jumping for a raised-lane answer misses.
 *
 * Run:  node tools/selftest.js     (exit 0 = pass, 1 = fail)
 *
 * Why this exists: two scoring regressions shipped because earlier checks only
 * parsed the script instead of running it. Run this before pushing gameplay or
 * load-order changes.
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const HTML = path.join(__dirname, '..', 'sparkrunmath.html');
const noop = () => {};
let failures = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  PASS  ' + name); }
  else { console.log('  FAIL  ' + name + (detail ? '  — ' + detail : '')); failures++; }
}

// ---- DOM / canvas / WebAudio stubs (just enough for top-level load + update()) ----
function ctxStub() {
  return new Proxy({}, { get(t, p) {
    if (p in t) return t[p];
    if (p === 'measureText') return () => ({ width: 0 });
    if (p === 'createRadialGradient' || p === 'createLinearGradient') return () => ({ addColorStop: noop });
    if (p === 'getImageData') return () => ({ data: new Uint8ClampedArray(4), width: 1, height: 1 });
    return noop;
  }, set(t, p, v) { t[p] = v; return true; } });
}
function canvasStub() {
  return { width: 960, height: 540, style: {}, getContext: () => ctxStub(), addEventListener: noop,
           getBoundingClientRect: () => ({ width: 960, height: 540, left: 0, top: 0 }), toDataURL: () => '' };
}
function imageStub() { return new Proxy({}, { get(t, p) { return p in t ? t[p] : undefined; }, set(t, p, v) { t[p] = v; return true; } }); }
function elStub() {
  return new Proxy({ style: {}, hidden: false, classList: { add: noop, remove: noop }, textContent: '' },
                   { get(t, p) { return p in t ? t[p] : noop; }, set(t, p, v) { t[p] = v; return true; } });
}
function audioParam() { return new Proxy({ value: 1 }, { get(t, p) { return p in t ? t[p] : noop; }, set(t, p, v) { t[p] = v; return true; } }); }
function audioCtx() {
  return new Proxy({
    destination: {}, currentTime: 0, state: 'running',
    createGain: () => ({ gain: audioParam(), connect: noop, disconnect: noop }),
    createOscillator: () => ({ frequency: audioParam(), detune: audioParam(), type: '', connect: noop, start: noop, stop: noop }),
    createBuffer: () => ({ getChannelData: () => new Float32Array(1) }),
    createBufferSource: () => ({ buffer: null, playbackRate: audioParam(), connect: noop, start: noop, stop: noop }),
    createBiquadFilter: () => ({ frequency: audioParam(), Q: audioParam(), type: '', connect: noop }),
    resume: () => Promise.resolve(),
  }, { get(t, p) { return p in t ? t[p] : noop; }, set(t, p, v) { t[p] = v; return true; } });
}

function buildSandbox() {
  const els = { game: canvasStub(), fsbtn: elStub() };
  const documentStub = {
    getElementById: id => els[id] || elStub(),
    createElement: tag => tag === 'canvas' ? canvasStub() : elStub(),
    addEventListener: noop, removeEventListener: noop, body: elStub(), documentElement: elStub(),
    fullscreenElement: null, exitFullscreen: noop,
  };
  const sb = {
    console, document: documentStub,
    Image: function () { return imageStub(); },
    Audio: function () { return new Proxy({ play: () => Promise.resolve(), pause: noop }, { get(t, p) { return p in t ? t[p] : noop; }, set(t, p, v) { t[p] = v; return true; } }); },
    AudioContext: audioCtx, webkitAudioContext: audioCtx,
    requestAnimationFrame: () => 0, cancelAnimationFrame: noop,
    setTimeout: () => 0, clearTimeout: noop, setInterval: () => 0, clearInterval: noop,
    performance: { now: () => 0 },
    navigator: { standalone: false, userAgent: 'node' },
    matchMedia: () => ({ matches: false, addEventListener: noop, addListener: noop }),
    addEventListener: noop, removeEventListener: noop,
    localStorage: { getItem: () => null, setItem: noop },
    Math, Date, JSON, parseInt, parseFloat, isNaN, isFinite,
    Uint8ClampedArray, Float32Array, Uint8Array,
  };
  sb.window = sb; sb.globalThis = sb; sb.self = sb;
  return sb;
}

// ---- load ----
const html = fs.readFileSync(HTML, 'utf8');
let code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n;\n');
// expose the let/const-scoped game internals so the harness can drive a real game
code += `\n;globalThis.__g = {
  get state(){return state;}, get score(){return score;}, get hearts(){return hearts;}, get gate(){return gate;}, get player(){return player;},
  get packId(){return packId;}, get PACK(){return PACK;}, selectPack,
  update, hop, startLevel, overlapsBalloon, PLAYER_X, CARD_W, PIKA_HALF_W };`;

const sb = buildSandbox();
vm.createContext(sb);

console.log('sparkrunmath self-test');
console.log('[1] load (execute inline script under stubs)');
let g = null;
try {
  vm.runInContext(code, sb, { filename: 'sparkrunmath-inline.js' });
  g = sb.__g;
  check('script executes with no load-time error', true);
} catch (e) {
  check('script executes with no load-time error', false, e.constructor.name + ': ' + e.message);
  console.log('\nFAILED (load error) — ' + failures + ' failure(s)');
  process.exit(1);
}

console.log('[2] lane hit-test (laneFromY via overlapsBalloon)');
// 430 = ground, 318 = mid centre, 206 = high centre
check('grounded reads ground', g.overlapsBalloon(430, 1) === false && g.overlapsBalloon(430, 2) === false);
check('mid park overlaps mid', g.overlapsBalloon(318, 1) === true);
check('high park overlaps high', g.overlapsBalloon(206, 2) === true);

console.log('[3] scoring — drive the real update() loop');
const dt = 1 / 60;
// Run one question: tap the correct number of times (=correctLane) once the balloon
// centre reaches jumpAtCardCx; null = never jump. Returns {correct, scored}.
function trial(jumpAtCardCx) {
  g.startLevel(0);
  const correct = g.gate.correctLane;
  const need = correct;            // 0 ground (no jump), 1 mid (1 tap), 2 high (2 taps)
  let taps = 0; const s0 = g.score;
  for (let f = 0; f < 800 && g.state === 'play'; f++) {
    const cardCx = g.gate.x + g.CARD_W / 2;
    if (jumpAtCardCx !== null && taps < need && cardCx <= jumpAtCardCx) { g.hop(); taps++; }
    g.update(dt);
  }
  return { correct, scored: g.score > s0 };
}
// retry helper to land on a specific correct lane despite randomness
function trialForLane(lane, jumpAtCardCx) {
  for (let i = 0; i < 60; i++) { const r = trial(jumpAtCardCx); if (r.correct === lane) return r; }
  return null;
}

// pre-positioned (jump early) should score for whatever random lane comes up
let prePass = 0; for (let i = 0; i < 8; i++) if (trial(360).scored) prePass++;
check('pre-positioned jump scores (8/8 random lanes)', prePass === 8, prePass + '/8');

// the regression we just fixed: a mid answer caught on-arrival and reaction-late
const midOn = trialForLane(1, 232), midLate = trialForLane(1, 180);
check('mid answer, on-arrival jump scores', midOn && midOn.scored);
check('mid answer, reaction-late jump scores', midLate && midLate.scored);

// high answer (needs a double-jump) scores when started early enough
const hi = trialForLane(2, 300);
check('high answer, double-jump scores', hi && hi.scored);

// skill preserved: never jumping for a raised-lane answer must miss
const noJump = (function () { for (let i = 0; i < 60; i++) { const r = trial(null); if (r.correct !== 0) return r; } return null; })();
check('raised-lane answer with no jump misses', noJump && noJump.scored === false);

// exploit guard: overshoot to HIGH (2 taps) on a MID answer, then fall back through
// mid — must NOT score (you only score the lane you actually chose, not pass-through).
const overshoot = (function () {
  for (let i = 0; i < 120; i++) {
    g.startLevel(0);
    if (g.gate.correctLane !== 1) continue;                 // need a mid (lane 1) answer
    let taps = 0; const s0 = g.score;
    for (let f = 0; f < 800 && g.state === 'play'; f++) {
      const cardCx = g.gate.x + g.CARD_W / 2;
      if (taps < 2 && cardCx <= 380) { g.hop(); taps++; }   // double-jump to HIGH early, then arc down through mid
      g.update(dt);
    }
    return { scored: g.score > s0 };
  }
  return null;
})();
check('overshoot to high then fall through mid does NOT score', overshoot && overshoot.scored === false);

console.log('[4] younger (audio) pack — recognition content + same scoring');
g.selectPack('abc');
check('selectPack switches active pack', g.packId === 'abc' && g.PACK.audio === true);
g.startLevel(0);
const aq = g.gate;
const okShape = aq && Array.isArray(aq.choices) && aq.choices.length === 3
  && aq.choices.includes(aq.ans) && aq.correctLane === aq.choices.indexOf(aq.ans)
  && aq.audio === aq.ans && /^([1-9]|1[0-9]|20|[a-z])$/i.test(String(aq.ans));
check('audio gate has 3 choices incl. answer + matching audio key', okShape,
      aq && JSON.stringify({choices:aq.choices, ans:aq.ans, audio:aq.audio, lane:aq.correctLane}));
const abcScore = trial(360);
check('younger pack: jump-to-match still scores', abcScore.scored);
g.selectPack('maths');   // restore for any later checks

console.log('\n' + (failures === 0 ? 'ALL PASS' : 'FAILED — ' + failures + ' failure(s)'));
process.exit(failures === 0 ? 0 : 1);
