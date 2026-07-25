import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Feeding Frenzy", layout="wide", initial_sidebar_state="collapsed")

# Strip Streamlit's own chrome (menu, footer, header, padding) so the game owns the whole viewport —
# the game now has its own loading screen + title screen instead of a Streamlit page header.
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div.block-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
        .stApp {background: #01040a;}
        iframe {display: block;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Part A: Full-screen deep-sea canvas layout + top-left pause control styling
game_html = r"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        html, body { margin: 0; padding: 0; height: 100%; width: 100%; background: #01040a; font-family: monospace; user-select: none; -webkit-user-select: none; overflow: hidden; }
        #gameContainer { position: relative; width: 100vw; height: 100vh; height: 100dvh; margin: 0; overflow: hidden; touch-action: none; }
        canvas { display: block; background: #020b18; width: 100%; height: 100%; }

        /* Top bar: pause button + score on the left, rank on the right */
        #hud { position: absolute; top: max(14px, env(safe-area-inset-top)); left: 18px; right: 18px; display: flex; justify-content: space-between; align-items: center; color: #34d399; font-size: 16px; font-weight: bold; pointer-events: none; z-index: 10; text-shadow: 0 0 8px #047857; letter-spacing: 1px; }
        #hudLeft { display: flex; align-items: center; gap: 12px; }

        #pauseBtn { pointer-events: auto; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 10px; border: 1px solid rgba(52,211,153,0.55); background: rgba(2, 20, 30, 0.72); color: #34d399; cursor: pointer; padding: 0; backdrop-filter: blur(4px); transition: transform 0.1s, background 0.15s; }
        #pauseBtn:hover { background: rgba(16, 185, 129, 0.22); }
        #pauseBtn:active { transform: scale(0.92); }
        #pauseBtn svg { width: 16px; height: 16px; display: block; }

        #loadingScreen { position: absolute; inset: 0; background: radial-gradient(circle at 50% 40%, #062338, #010509); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 40; color: #cbd5e1; }
        #loadingBarTrack { width: 240px; height: 10px; border-radius: 6px; background: rgba(255,255,255,0.08); overflow: hidden; margin-top: 22px; border: 1px solid rgba(52,211,153,0.35); }
        #loadingBarFill { width: 0%; height: 100%; background: linear-gradient(90deg, #10b981, #34d399); transition: width 0.12s linear; }
        #loadingPercent { margin-top: 10px; font-size: 13px; letter-spacing: 2px; color: #34d399; }
        #loadingLabel { font-size: 12px; letter-spacing: 3px; color: #64748b; }

        #titleScreen { position: absolute; inset: 0; background: linear-gradient(180deg, #052f4a 0%, #021320 55%, #01050d 100%); display: none; flex-direction: column; align-items: center; justify-content: center; z-index: 30; text-align: center; cursor: pointer; }
        #titleHeading { color: #ffffff; font-size: 40px; font-weight: 900; letter-spacing: 4px; margin: 0; text-shadow: 0 0 22px #10b981, 0 0 6px #ffffff; }
        #titleHeading span { color: #34d399; }
        #titleSub { color: #94a3b8; font-size: 12px; max-width: 320px; line-height: 1.7; margin-top: 14px; letter-spacing: 1px; }
        #tapPrompt { margin-top: 32px; padding: 14px 34px; border: 2px solid #10b981; border-radius: 30px; color: #34d399; font-size: 13px; letter-spacing: 3px; font-weight: bold; animation: pulseTap 1.4s ease-in-out infinite; }
        @keyframes pulseTap { 0%,100% { opacity: 1; transform: scale(1);} 50% { opacity: 0.55; transform: scale(1.05);} }

        #screenOverlay { position: absolute; inset: 0; background: rgba(2, 8, 20, 0.92); display: none; flex-direction: column; align-items: center; justify-content: center; z-index: 20; color: white; text-align: center; }

        /* Chapter map label under the score, and the big banner shown when entering a new chapter */
        #chapterLabel { position: absolute; top: 46px; left: 18px; font-size: 10px; letter-spacing: 2px; color: #7dd3c8; opacity: 0.85; pointer-events: none; z-index: 10; text-shadow: 0 0 6px #047857; }
        #chapterBanner { position: absolute; top: 18%; left: 50%; transform: translate(-50%, -12px); z-index: 15; text-align: center; pointer-events: none; opacity: 0; transition: opacity 0.5s ease, transform 0.5s ease; }
        #chapterBanner.show { opacity: 1; transform: translate(-50%, 0); }
        #chapterBannerEyebrow { font-size: 11px; letter-spacing: 5px; color: #34d399; text-shadow: 0 0 10px #047857; }
        #chapterBannerTitle { font-size: 26px; font-weight: 900; letter-spacing: 3px; color: #ffffff; text-shadow: 0 0 16px rgba(52,211,153,0.8); margin-top: 4px; }

        /* Pause menu — sits above the frozen game frame */
        #pauseOverlay { position: absolute; inset: 0; background: rgba(1, 8, 16, 0.78); backdrop-filter: blur(6px); display: none; flex-direction: column; align-items: center; justify-content: center; z-index: 25; text-align: center; }
        #pauseCard { background: rgba(4, 22, 34, 0.9); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 18px; padding: 32px 30px; box-shadow: 0 18px 50px rgba(0,0,0,0.55); min-width: 260px; }
        #pauseTitle { color: #34d399; letter-spacing: 5px; font-size: 22px; margin: 0 0 6px; text-shadow: 0 0 14px #047857; }
        #pauseHint { color: #64748b; font-size: 11px; letter-spacing: 1px; margin: 0 0 22px; }
        .menu-btn { display: block; width: 100%; margin-top: 10px; padding: 13px 22px; border-radius: 10px; font-family: monospace; font-size: 13px; font-weight: bold; letter-spacing: 2px; cursor: pointer; border: 1px solid transparent; transition: transform 0.1s, filter 0.15s; }
        .menu-btn:active { transform: scale(0.96); }
        .menu-btn.primary { background: #10b981; color: #01040a; box-shadow: 0 4px 14px rgba(16,185,129,0.35); }
        .menu-btn.primary:hover { filter: brightness(1.1); }
        .menu-btn.ghost { background: rgba(52, 211, 153, 0.08); color: #34d399; border-color: rgba(52,211,153,0.45); }
        .menu-btn.ghost:hover { background: rgba(52, 211, 153, 0.18); }
        .menu-btn.danger { background: rgba(239, 68, 68, 0.12); color: #f87171; border-color: rgba(239,68,68,0.5); }
        .menu-btn.danger:hover { background: rgba(239, 68, 68, 0.24); }

        .arcade-btn { margin-top: 20px; padding: 14px 30px; background: #10b981; color: #01040a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); font-family: monospace; font-size: 14px; letter-spacing: 1px; transition: transform 0.1s; }
        .arcade-btn:active { transform: scale(0.95); }
        #overlayExitBtn { margin-top: 12px; background: none; border: 1px solid rgba(148,163,184,0.4); color: #94a3b8; padding: 10px 24px; border-radius: 8px; font-family: monospace; font-size: 12px; letter-spacing: 2px; cursor: pointer; }
        #overlayExitBtn:hover { color: #cbd5e1; border-color: rgba(203,213,225,0.6); }
    </style>
</head>
"""
# Part B: Loading screen, title/tap-to-play screen, pause menu, and the game-over overlay
game_html += r"""
<body>
    <div id="gameContainer">
        <div id="hud" style="display:none;">
            <div id="hudLeft">
                <button id="pauseBtn" aria-label="Pause game" title="Pause (Esc)">
                    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg>
                </button>
                <div id="scoreLabel">SCORE: 00000</div>
            </div>
            <div id="sizeLabel">SIZE: SMALL  0/10</div>
            <div id="livesLabel" style="color:#f87171; text-shadow:0 0 8px #7f1d1d; letter-spacing:2px;">LIVES ♥ ♥ ♥</div>
        </div>
        <div id="chapterLabel" style="display:none;">MAP 1 / 5 — CORAL SHALLOWS</div>

        <div id="chapterBanner">
            <div id="chapterBannerEyebrow">CHAPTER <span id="chapterBannerNum">1</span> OF 5</div>
            <div id="chapterBannerTitle">CORAL SHALLOWS</div>
        </div>

        <div id="loadingScreen">
            <div id="loadingLabel">DESCENDING INTO THE DEEP</div>
            <div id="loadingBarTrack"><div id="loadingBarFill"></div></div>
            <div id="loadingPercent">0%</div>
        </div>

        <div id="titleScreen">
            <h1 id="titleHeading">3D FEEDING <span>FRENZY</span></h1>
            <p id="titleSub">Consume smaller reef life to grow. Avoid anything bigger — until you're big enough to eat that too.</p>
            <div id="tapPrompt">TAP OR CLICK TO PLAY</div>
        </div>

        <div id="pauseOverlay">
            <div id="pauseCard">
                <h2 id="pauseTitle">PAUSED</h2>
                <p id="pauseHint">PRESS ESC OR P TO RESUME</p>
                <button class="menu-btn primary" id="resumeBtn">▶ RESUME</button>
                <button class="menu-btn ghost" id="restartBtn">🔄 RESTART</button>
                <button class="menu-btn danger" id="exitBtn">✕ EXIT GAME</button>
            </div>
        </div>

        <div id="screenOverlay">
            <h2 id="overlayTitle" style="color: #10b981; letter-spacing: 3px; font-size: 26px; margin: 0;">GAME OVER</h2>
            <p id="overlaySub" style="color: #64748b; font-size: 12px; max-width: 320px; line-height: 1.6; margin-top: 10px;"></p>
            <button class="arcade-btn" id="actionBtn">REDEPLOY DESCENT 🔄</button>
            <button id="overlayExitBtn">EXIT TO TITLE</button>
        </div>

        <div id="lifeLostOverlay" style="position:absolute; inset:0; background:rgba(16,2,2,0.82); backdrop-filter:blur(6px); display:none; flex-direction:column; align-items:center; justify-content:center; z-index:27; text-align:center;">
            <div style="background:rgba(34,6,6,0.94); border:1px solid rgba(248,113,113,0.45); border-radius:18px; padding:34px 32px; box-shadow:0 18px 50px rgba(0,0,0,0.6); min-width:290px;">
                <div style="font-size:11px; letter-spacing:5px; color:#f87171; text-shadow:0 0 10px #7f1d1d;">CONSUMED</div>
                <h2 id="lifeLostTitle" style="color:#ffffff; letter-spacing:2px; font-size:24px; margin:8px 0 6px; text-shadow:0 0 16px rgba(248,113,113,0.8);">YOU GOT 2 LIVES LEFT</h2>
                <div id="lifeLostHearts" style="font-size:22px; letter-spacing:6px; color:#f87171; margin:6px 0 2px;">♥ ♥</div>
                <p id="lifeLostSub" style="color:#fca5a5; font-size:12px; max-width:300px; line-height:1.6; margin:6px auto 4px;">Respawning in the same chapter — keep your progress!</p>
                <button class="menu-btn primary" id="lifeContinueBtn" style="margin-top:22px;">CONTINUE ▶</button>
            </div>
        </div>

        <div id="chapterCompleteOverlay" style="position:absolute; inset:0; background:rgba(1,8,16,0.82); backdrop-filter:blur(6px); display:none; flex-direction:column; align-items:center; justify-content:center; z-index:26; text-align:center;">
            <div style="background:rgba(4,22,34,0.92); border:1px solid rgba(52,211,153,0.4); border-radius:18px; padding:34px 32px; box-shadow:0 18px 50px rgba(0,0,0,0.55); min-width:280px;">
                <div style="font-size:11px; letter-spacing:5px; color:#34d399; text-shadow:0 0 10px #047857;">CHAPTER COMPLETED</div>
                <h2 id="chapterCompleteTitle" style="color:#ffffff; letter-spacing:2px; font-size:24px; margin:8px 0 6px; text-shadow:0 0 16px rgba(52,211,153,0.8);">CORAL SHALLOWS</h2>
                <p id="chapterCompleteSub" style="color:#94a3b8; font-size:12px; max-width:300px; line-height:1.6; margin:0 auto 4px;">You devoured every fish. Move on to the next chapter!</p>
                <button class="menu-btn primary" id="continueBtn" style="margin-top:22px;">PRESS TO CONTINUE ▶</button>
            </div>
        </div>

        <canvas id="aquariumCanvas"></canvas>
    </div>

<script>
    const canvas = document.getElementById("aquariumCanvas"); const ctx = canvas.getContext("2d");
    const container = document.getElementById("gameContainer"); const hud = document.getElementById("hud");
    const scoreLabel = document.getElementById("scoreLabel"); const sizeLabel = document.getElementById("sizeLabel");
    const screenOverlay = document.getElementById("screenOverlay"); const overlayTitle = document.getElementById("overlayTitle"); const overlaySub = document.getElementById("overlaySub"); const actionBtn = document.getElementById("actionBtn");
    const loadingScreen = document.getElementById("loadingScreen"); const loadingBarFill = document.getElementById("loadingBarFill"); const loadingPercent = document.getElementById("loadingPercent");
    const titleScreen = document.getElementById("titleScreen");
    const pauseBtn = document.getElementById("pauseBtn"); const pauseOverlay = document.getElementById("pauseOverlay");
    const resumeBtn = document.getElementById("resumeBtn"); const restartBtn = document.getElementById("restartBtn"); const exitBtn = document.getElementById("exitBtn");
    const overlayExitBtn = document.getElementById("overlayExitBtn");
    const chapterLabel = document.getElementById("chapterLabel");
    const chapterBanner = document.getElementById("chapterBanner");
    const chapterBannerNum = document.getElementById("chapterBannerNum");
    const chapterBannerTitle = document.getElementById("chapterBannerTitle");
    const chapterCompleteOverlay = document.getElementById("chapterCompleteOverlay");
    const chapterCompleteTitle = document.getElementById("chapterCompleteTitle");
    const chapterCompleteSub = document.getElementById("chapterCompleteSub");
    const continueBtn = document.getElementById("continueBtn");
    const livesLabel = document.getElementById("livesLabel");
    const lifeLostOverlay = document.getElementById("lifeLostOverlay");
    const lifeLostTitle = document.getElementById("lifeLostTitle");
    const lifeLostHearts = document.getElementById("lifeLostHearts");
    const lifeLostSub = document.getElementById("lifeLostSub");
    const lifeContinueBtn = document.getElementById("lifeContinueBtn");

    // ---- Lives system ----
    const MAX_LIVES = 3;
    let lives = MAX_LIVES;

    // ---- Discrete fish-size progression ----
    const TIER_RADII = [15, 24, 34, 46];                 // small, medium, big, large
    const TIER_NAMES = ["SMALL", "MEDIUM", "BIG", "LARGE"];
    const FISH_PER_TIER = 10;
    const FISH_SIZE_CLASSES = [10, 19, 29, 41];

    let score = 0, gameActive = false, gamePaused = false, timeTick = 0, lastTimestamp = null;
    let player = { x: 190, y: 240, vx: 0, vy: 0, radius: 15, targetX: 190, targetY: 240, facingLeft: false, tailWag: 0, tiltAngle: 0, tier: 0, eatenThisTier: 0 };
    let marineThreats = []; let environmentBubbles = []; let particles = []; let kelpFronds = [];
    let reefRocks = []; let reefCorals = []; let reefAnemones = [];
    let driftPlankton = [];
    const LIGHT_RAYS = [
        { o: -0.34, w: 0.085, s: 0.0055, a: 0.16 },
        { o: -0.16, w: 0.130, s: 0.0038, a: 0.12 },
        { o:  0.02, w: 0.060, s: 0.0072, a: 0.20 },
        { o:  0.19, w: 0.115, s: 0.0045, a: 0.11 },
        { o:  0.36, w: 0.075, s: 0.0062, a: 0.15 },
    ];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;
    let screenShake = 0;
    const MAX_FISH_ON_SCREEN = 8;
    const TARGET_PER_SIDE = 3;

    // Bioluminescent reef-fish species palettes — deep, moody body tones with a glowing "hot core"
    // near the head/gills (the `glow` field) so every fish reads like it's lit from within, matching
    // a dark abyssal aquarium look. `shape` still drives silhouette + fins + animation per species.
    const FISH_SPECIES = [
        { name: "SEA FISH",       bands: ["#dff2ff", "#3f7fc9", "#0c2a4a"], finColor: "#8fd8ff", maskColor: "#04101f", glow: "94, 190, 255",
          shape: { profile: "balanced", yScale: 0.82, tail: "fan",    dorsal: "low",   wag: 1.0, extra: null } },
        { name: "GOLD FISH",      bands: ["#fff0e0", "#f2b23c", "#5a2f0c"], finColor: "#ffb84d", maskColor: "#1c0f04", glow: "255, 176, 96",
          shape: { profile: "disc",     yScale: 1.05, tail: "flow",   dorsal: "sail",  wag: 0.7, extra: null } },
        { name: "CLOWN FISH",     bands: ["#ffe0e8", "#ff6f8f", "#5a0c22"], finColor: "#ff9fc0", maskColor: "#160308", glow: "255, 110, 150",
          shape: { profile: "tall",     yScale: 0.98, tail: "fan",    dorsal: "spiny", wag: 1.1, extra: null } },
        { name: "SPAR FISH",      bands: ["#efe9ff", "#8f7bff", "#2a1e5c"], finColor: "#c1a8ff", maskColor: "#12082b", glow: "170, 140, 255",
          shape: { profile: "slim",     yScale: 0.66, tail: "fork",   dorsal: "low",   wag: 1.3, extra: null } },
        { name: "YELLOWFIN TUNA", bands: ["#e2fff5", "#2f8fc9", "#0c2438"], finColor: "#ffe37a", maskColor: "#051c16", glow: "255, 220, 130",
          shape: { profile: "torpedo",  yScale: 0.70, tail: "lunate", dorsal: "sail",  wag: 1.5, extra: "finlets" } },
        { name: "KELP WRASSE",    bands: ["#eafff0", "#5fd1a0", "#0e3d2c"], finColor: "#8effc2", maskColor: "#031f14", glow: "110, 255, 190",
          shape: { profile: "slim",     yScale: 0.70, tail: "fan",    dorsal: "spiny", wag: 1.15, extra: null } },
        { name: "SILVER BAITFISH",bands: ["#dff7ff", "#5fc4e8", "#0e3040"], finColor: "#bdf2ff", maskColor: "#031722", glow: "140, 225, 255",
          shape: { profile: "torpedo",  yScale: 0.64, tail: "fork",   dorsal: "low",   wag: 1.4, extra: null } },
        { name: "LANTERN FISH",   bands: ["#241c3c", "#4b3a78", "#0c081c"], finColor: "#7de8d8", maskColor: "#040310", glow: "125, 232, 216",
          shape: { profile: "balanced", yScale: 0.80, tail: "fork",   dorsal: "low",   wag: 1.0, extra: "barbel" } },
        { name: "ANGLERFISH",     bands: ["#1c1230", "#33205c", "#0a0618"], finColor: "#ff5fb0", maskColor: "#04020a", glow: "255, 95, 176",
          shape: { profile: "bulb",     yScale: 1.02, tail: "fan",    dorsal: "spiny", wag: 0.8, extra: "lure" } },
    ];
    // Player fish: a glowing rose/red bioluminescent centerpiece (matching the reference look) with a
    // pale white-pink head so the "hot core" glow reads clearly against dark water.
    const PLAYER_SPECIES = { bands: ["#fff0f0", "#ff6b6b", "#5c0f14"], finColor: "#ff8f9e", maskColor: "#1a0406", glow: "255, 90, 110",
          shape: { profile: "balanced", yScale: 0.80, tail: "fork", dorsal: "spiny", wag: 1.0, extra: null } };

    /* ---------- 5 chapter maps ----------
       Darker, more saturated abyssal water than before — brighter/shallower still up top, but every
       chapter now sits deeper into inky blue-black so the bioluminescent glow effects pop. */
    const CHAPTERS = [
        {
            name: "CORAL SHALLOWS", minRadius: 0,
            sky: ["#052032", "#02121f", "#000810"], fog: "1, 12, 20", rayStrength: 0.9,
            coralAmberBias: 0.5, speciesPool: [0, 1, 2, 3, 4], kelpDensity: 0.4,
            schoolCount: 3, jellyfishCount: 2, megafauna: "turtle", megafaunaChance: 0.55, landmark: "none",
        },
        {
            name: "KELP FOREST", minRadius: 23,
            sky: ["#051f1c", "#031714", "#00080a"], fog: "2, 18, 16", rayStrength: 0.7,
            coralAmberBias: 0.3, speciesPool: [0, 4, 5, 3, 1], kelpDensity: 1.6,
            schoolCount: 5, jellyfishCount: 3, megafauna: "turtle", megafaunaChance: 0.4, landmark: "none",
        },
        {
            name: "ROCKY DROP-OFF", minRadius: 32,
            sky: ["#071b2e", "#04101f", "#00050c"], fog: "2, 12, 22", rayStrength: 0.55,
            coralAmberBias: 0.35, speciesPool: [6, 0, 3, 5, 2], kelpDensity: 0.7,
            schoolCount: 6, jellyfishCount: 4, megafauna: "ray", megafaunaChance: 0.5, landmark: "shipwreck",
        },
        {
            name: "TWILIGHT TRENCH", minRadius: 42,
            sky: ["#0c0924", "#070718", "#01010a"], fog: "4, 6, 20", rayStrength: 0.3,
            coralAmberBias: 0.15, speciesPool: [7, 6, 3, 8], kelpDensity: 0.25,
            schoolCount: 4, jellyfishCount: 6, megafauna: "ray", megafaunaChance: 0.35, landmark: "shipwreck",
        },
        {
            name: "ABYSSAL DEEP", minRadius: 52,
            sky: ["#070414", "#03020c", "#000003"], fog: "6, 2, 16", rayStrength: 0.1,
            coralAmberBias: 0.05, speciesPool: [7, 8], kelpDensity: 0.05,
            schoolCount: 2, jellyfishCount: 8, megafauna: "none", megafaunaChance: 0, landmark: "ruins",
        },
    ];
    const WIN_RADIUS = 65;
    let currentChapter = 0;
    let chapterBannerTimer = 0;
    let schoolFish = []; let jellyfish = []; let megafaunaCreature = null; let landmarkDecor = null;

    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width; canvas.height = rect.height;
        player.x = Math.min(player.x, canvas.width - 15); player.y = Math.min(player.y, canvas.height - 15);
        player.targetX = player.x; player.targetY = player.y;
        regenerateKelp();
        regenerateReef();
        regeneratePlankton();
    }
    function regenerateKelp() {
        kelpFronds = [];
        const density = CHAPTERS[currentChapter] ? CHAPTERS[currentChapter].kelpDensity : 0.4;
        const count = Math.max(2, Math.round((canvas.width / 140) * density));
        for (let i = 0; i < count; i++) {
            kelpFronds.push({ x: Math.random() * canvas.width, height: 70 + Math.random() * 110, sway: Math.random() * 12, phase: Math.random() * 100 });
        }
    }
    // Fine drifting plankton / marine-snow specks — the tiny glinting dust visible throughout the
    // reference image. Purely decorative, drawn as soft additive dots.
    function regeneratePlankton() {
        driftPlankton = [];
        const count = Math.max(30, Math.round((canvas.width * canvas.height) / 9000));
        for (let i = 0; i < count; i++) {
            driftPlankton.push({
                x: Math.random() * canvas.width, y: Math.random() * canvas.height,
                r: 0.5 + Math.random() * 1.4, phase: Math.random() * 100,
                speed: 0.03 + Math.random() * 0.06, drift: (Math.random() - 0.5) * 0.04,
            });
        }
    }

    /* ---------- Procedural coral reef: rocks, branching/fan/tube corals, glowing anemones ---------- */
    function makeCoralBranches(height, spread) {
        const segs = [];
        (function grow(x, y, ang, len, wid, depth) {
            const nx = x + Math.cos(ang) * len, ny = y + Math.sin(ang) * len;
            segs.push({ x1: x, y1: y, x2: nx, y2: ny, w: Math.max(1.2, wid), tip: depth === 0 });
            if (depth <= 0) return;
            grow(nx, ny, ang - spread * (0.55 + Math.random() * 0.6), len * 0.74, wid * 0.66, depth - 1);
            grow(nx, ny, ang + spread * (0.55 + Math.random() * 0.6), len * 0.74, wid * 0.66, depth - 1);
            if (Math.random() < 0.4) grow(nx, ny, ang + (Math.random() - 0.5) * spread * 0.5, len * 0.6, wid * 0.5, depth - 1);
        })(0, 0, -Math.PI / 2, height * 0.4, height * 0.14, 3);
        return segs;
    }
    function regenerateReef() {
        const w = canvas.width, h = canvas.height;
        reefRocks = []; reefCorals = []; reefAnemones = [];

        const rockCount = Math.max(3, Math.round(w / 240));
        for (let i = 0; i < rockCount; i++) {
            reefRocks.push({
                x: (i + 0.5) * (w / rockCount) + (Math.random() - 0.5) * (w / rockCount) * 0.6,
                rw: 70 + Math.random() * 130, rh: 26 + Math.random() * 58,
                depth: Math.random(), bumps: 2 + Math.floor(Math.random() * 3),
            });
        }

        const chapterTheme = CHAPTERS[currentChapter] || CHAPTERS[0];
        const amberBias = chapterTheme.coralAmberBias;

        const coralCount = Math.max(5, Math.round(w / 130));
        for (let i = 0; i < coralCount; i++) {
            const kind = Math.random();
            const height = 44 + Math.random() * 82;
            reefCorals.push({
                x: Math.random() * w,
                height,
                depth: 0.35 + Math.random() * 0.65,
                kind: kind < 0.45 ? "branch" : (kind < 0.75 ? "fan" : "tube"),
                segs: kind < 0.45 ? makeCoralBranches(height, 0.55 + Math.random() * 0.3) : null,
                tubes: Array.from({ length: 4 + Math.floor(Math.random() * 4) }, () => ({
                    dx: (Math.random() - 0.5) * height * 0.6, len: height * (0.3 + Math.random() * 0.4), wid: 5 + Math.random() * 6,
                })),
                hue: Math.random() < amberBias ? "amber" : "teal",
                phase: Math.random() * 100,
            });
        }

        const anemoneCount = Math.max(2, Math.round(w / 320));
        for (let i = 0; i < anemoneCount; i++) {
            reefAnemones.push({
                x: (i + 0.5) * (w / anemoneCount) + (Math.random() - 0.5) * 90,
                base: 14 + Math.random() * 16, lift: 10 + Math.random() * 26,
                tentacles: 9 + Math.floor(Math.random() * 7),
                phase: Math.random() * 100, hue: Math.random() < (1 - amberBias) ? "teal" : "amber",
            });
        }

        regenerateSchoolFish(); regenerateJellyfish(); regenerateMegafauna(); regenerateLandmark();
    }

    function regenerateSchoolFish() {
        schoolFish = [];
        const theme = CHAPTERS[currentChapter] || CHAPTERS[0];
        for (let s = 0; s < theme.schoolCount; s++) {
            const memberCount = 4 + Math.floor(Math.random() * 5);
            const originX = Math.random() * canvas.width, originY = canvas.height * (0.15 + Math.random() * 0.55);
            const dir = Math.random() > 0.5 ? 1 : -1;
            const speciesIdx = theme.speciesPool[Math.floor(Math.random() * theme.speciesPool.length)];
            const members = [];
            for (let m = 0; m < memberCount; m++) {
                members.push({ ox: (Math.random() - 0.5) * 46, oy: (Math.random() - 0.5) * 30, phase: Math.random() * 100 });
            }
            schoolFish.push({ x: originX, y: originY, vx: dir * (0.25 + Math.random() * 0.25), radius: 3.5 + Math.random() * 2.5, speciesIdx, members, bobPhase: Math.random() * 100 });
        }
    }
    function regenerateJellyfish() {
        jellyfish = [];
        const theme = CHAPTERS[currentChapter] || CHAPTERS[0];
        for (let j = 0; j < theme.jellyfishCount; j++) {
            jellyfish.push({
                x: Math.random() * canvas.width, y: canvas.height * (0.1 + Math.random() * 0.75),
                size: 14 + Math.random() * 22, phase: Math.random() * 100, driftSpeed: 0.08 + Math.random() * 0.1,
                hue: Math.random() < 0.5 ? "196, 130, 255" : "255, 120, 210",
            });
        }
    }
    function regenerateMegafauna() {
        const theme = CHAPTERS[currentChapter] || CHAPTERS[0];
        if (theme.megafauna === "none" || Math.random() > theme.megafaunaChance) { megafaunaCreature = null; return; }
        const dir = Math.random() > 0.5 ? 1 : -1;
        megafaunaCreature = {
            kind: theme.megafauna, x: dir > 0 ? -120 : canvas.width + 120, y: canvas.height * (0.2 + Math.random() * 0.4),
            vx: dir * (0.18 + Math.random() * 0.1), size: theme.megafauna === "ray" ? 46 + Math.random() * 20 : 30 + Math.random() * 10,
            phase: Math.random() * 100,
        };
    }
    function regenerateLandmark() {
        const theme = CHAPTERS[currentChapter] || CHAPTERS[0];
        if (theme.landmark === "none") { landmarkDecor = null; return; }
        landmarkDecor = { kind: theme.landmark, x: canvas.width * (0.55 + Math.random() * 0.35), scale: 0.85 + Math.random() * 0.4 };
    }
    window.addEventListener("resize", resizeCanvas);
    window.addEventListener("orientationchange", () => setTimeout(resizeCanvas, 250));
    resizeCanvas();

    function setupAudio() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
    function sound(type) {
        setupAudio(); if (!audioCtx) return; let osc = audioCtx.createOscillator(), gain = audioCtx.createGain(); osc.connect(gain); gain.connect(audioCtx.destination);
        if (type === "zap") { osc.type = "sawtooth"; osc.frequency.setValueAtTime(420, audioCtx.currentTime); osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.12); gain.gain.setValueAtTime(0.3, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.12); }
        else if (type === "ding") { osc.type = "sine"; osc.frequency.setValueAtTime(880, audioCtx.currentTime); osc.frequency.linearRampToValueAtTime(1200, audioCtx.currentTime + 0.06); gain.gain.setValueAtTime(0.15, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.06); }
        else if (type === "boom") { osc.type = "sawtooth"; osc.frequency.setValueAtTime(90, audioCtx.currentTime); osc.frequency.exponentialRampToValueAtTime(15, audioCtx.currentTime + 0.4); gain.gain.setValueAtTime(0.6, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.4); }
        else if (type === "level") { osc.type = "sine"; osc.frequency.setValueAtTime(440, audioCtx.currentTime); osc.frequency.setValueAtTime(554.37, audioCtx.currentTime + 0.08); osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.16); gain.gain.setValueAtTime(0.2, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.35); }
        else if (type === "crunch") {
            osc.disconnect(); gain.disconnect();
            const now = audioCtx.currentTime;
            const bufferSize = Math.floor(audioCtx.sampleRate * 0.14);
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                const decay = Math.pow(1 - i / bufferSize, 2.6);
                data[i] = (Math.random() * 2 - 1) * decay;
            }
            const noise = audioCtx.createBufferSource(); noise.buffer = buffer;
            const bandpass = audioCtx.createBiquadFilter(); bandpass.type = "bandpass"; bandpass.frequency.value = 1500 + Math.random() * 500; bandpass.Q.value = 0.7;
            const noiseGain = audioCtx.createGain(); noiseGain.gain.setValueAtTime(0.55, now); noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.13);
            noise.connect(bandpass); bandpass.connect(noiseGain); noiseGain.connect(audioCtx.destination);
            noise.start(now); noise.stop(now + 0.14);

            const thumpOsc = audioCtx.createOscillator(); const thumpGain = audioCtx.createGain();
            thumpOsc.type = "sine"; thumpOsc.frequency.setValueAtTime(170, now); thumpOsc.frequency.exponentialRampToValueAtTime(48, now + 0.09);
            thumpGain.gain.setValueAtTime(0.4, now); thumpGain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
            thumpOsc.connect(thumpGain); thumpGain.connect(audioCtx.destination);
            thumpOsc.start(now); thumpOsc.stop(now + 0.1);
        }
    }

    function updateInputCoordinates(clientX, clientY) {
        if (!gameActive || gamePaused) return; const rect = container.getBoundingClientRect();
        player.targetX = Math.max(15, Math.min(clientX - rect.left, rect.width - 15));
        player.targetY = Math.max(15, Math.min(clientY - rect.top, rect.height - 15));
    }
    container.addEventListener("mousemove", (e) => updateInputCoordinates(e.clientX, e.clientY));
    container.addEventListener("touchstart", (e) => { if (gameActive && !gamePaused && e.touches && e.touches.length > 0) { updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: true });
    container.addEventListener("touchmove", (e) => { if (gameActive && !gamePaused) { e.preventDefault(); if (e.touches && e.touches.length > 0) updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: false });
"""
# Part C: Loading sequence + tap-to-play title screen + pause / restart / exit menu wiring
game_html += r"""
    let loadProgress = 0;
    function runLoadingSequence() {
        const timer = setInterval(() => {
            loadProgress += Math.random() * 16 + 8;
            if (loadProgress >= 100) {
                loadProgress = 100; clearInterval(timer);
                setTimeout(() => { loadingScreen.style.display = "none"; titleScreen.style.display = "flex"; }, 300);
            }
            loadingBarFill.style.width = loadProgress + "%";
            loadingPercent.innerText = Math.floor(loadProgress) + "%";
        }, 140);
    }
    function beginFromTitle() {
        titleScreen.style.display = "none"; setupAudio(); initiateArcadeGame();
    }
    titleScreen.addEventListener("click", beginFromTitle);
    titleScreen.addEventListener("touchstart", (e) => { e.preventDefault(); beginFromTitle(); }, { passive: false });
    runLoadingSequence();

    /* ---------- Pause / Restart / Exit ---------- */
    function pauseGame() {
        if (!gameActive || gamePaused) return;
        gamePaused = true;
        if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
        if (spawnIntervalId) { clearInterval(spawnIntervalId); spawnIntervalId = null; }
        pauseOverlay.style.display = "flex";
    }
    function resumeGame() {
        if (!gameActive || !gamePaused) return;
        gamePaused = false;
        pauseOverlay.style.display = "none";
        player.targetX = player.x; player.targetY = player.y;
        lastTimestamp = null;
        if (!spawnIntervalId) spawnIntervalId = setInterval(generateMarineLife, 650);
        if (!animationFrameId) animationFrameId = requestAnimationFrame(runGameLoop);
    }
    function togglePause() {
        if (chapterCompleteOverlay.style.display === "flex") return;
        if (lifeLostOverlay.style.display === "flex") return;
        gamePaused ? resumeGame() : pauseGame();
    }

    function exitToTitle() {
        gameActive = false; gamePaused = false;
        if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
        if (spawnIntervalId) { clearInterval(spawnIntervalId); spawnIntervalId = null; }
        pauseOverlay.style.display = "none";
        screenOverlay.style.display = "none";
        chapterCompleteOverlay.style.display = "none";
        lifeLostOverlay.style.display = "none";
        hud.style.display = "none";
        chapterLabel.style.display = "none";
        chapterBanner.classList.remove("show");
        marineThreats = []; particles = []; environmentBubbles = [];
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        titleScreen.style.display = "flex";
    }
    function restartGame() { pauseOverlay.style.display = "none"; gamePaused = false; initiateArcadeGame(); }

    pauseBtn.addEventListener("click", (e) => { e.stopPropagation(); togglePause(); });
    resumeBtn.addEventListener("click", (e) => { e.stopPropagation(); resumeGame(); });
    restartBtn.addEventListener("click", (e) => { e.stopPropagation(); restartGame(); });
    exitBtn.addEventListener("click", (e) => { e.stopPropagation(); exitToTitle(); });
    actionBtn.addEventListener("click", (e) => { e.stopPropagation(); initiateArcadeGame(); });
    overlayExitBtn.addEventListener("click", (e) => { e.stopPropagation(); exitToTitle(); });

    window.addEventListener("keydown", (e) => {
        const k = e.key.toLowerCase();
        if (k === "escape" || k === "p") { if (gameActive) { e.preventDefault(); togglePause(); } }
    });
    document.addEventListener("visibilitychange", () => { if (document.hidden) pauseGame(); });
"""
# Part D: True fish-silhouette rendering — tapered body with snout + peduncle, scales, gills, pectoral fin
# Now with a bioluminescent glow pass so every fish reads as lit-from-within against dark water.
game_html += r"""
    /* ---------- Volumetric lighting: soft god-rays fading into dark water ---------- */
    function drawVolumetricLight(pulse) {
        const h = canvas.height, w = canvas.width;
        let surf = ctx.createLinearGradient(0, 0, 0, h * 0.3);
        surf.addColorStop(0, `rgba(120, 190, 220, ${0.10 + pulse * 2})`);
        surf.addColorStop(1, "rgba(4, 20, 40, 0)");
        ctx.fillStyle = surf; ctx.fillRect(0, 0, w, h * 0.3);

        ctx.save();
        ctx.globalCompositeOperation = "lighter";
        const canBlur = typeof ctx.filter === "string";
        if (canBlur) ctx.filter = "blur(15px)";
        LIGHT_RAYS.forEach((ray, i) => {
            const topX = w * (0.5 + ray.o) + Math.sin(timeTick * ray.s + i * 1.7) * w * 0.035;
            const rw = w * ray.w;
            const skew = w * 0.09 + Math.sin(timeTick * ray.s * 1.6 + i) * w * 0.025;
            const alpha = ray.a + pulse * 1.2;
            let g = ctx.createLinearGradient(0, 0, 0, h * 0.95);
            g.addColorStop(0, `rgba(150, 200, 230, ${alpha * 0.6})`);
            g.addColorStop(0.35, `rgba(80, 130, 190, ${alpha * 0.3})`);
            g.addColorStop(0.72, `rgba(30, 60, 110, ${alpha * 0.1})`);
            g.addColorStop(1, "rgba(10, 20, 60, 0)");
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.moveTo(topX - rw * 0.5, -20); ctx.lineTo(topX + rw * 0.5, -20);
            ctx.lineTo(topX + skew + rw * 1.15, h * 0.98); ctx.lineTo(topX + skew - rw * 0.35, h * 0.98);
            ctx.closePath(); ctx.fill();
        });
        if (canBlur) ctx.filter = "none";
        ctx.restore();
    }

    /* ---------- Reef floor: sediment mound, layered rock and coral silhouettes ---------- */
    function reefTint(kind, lightness) {
        if (kind === "amber") return `rgba(${Math.round(150 * lightness + 40)}, ${Math.round(96 * lightness + 30)}, ${Math.round(38 * lightness + 18)}, 1)`;
        return `rgba(${Math.round(24 * lightness + 6)}, ${Math.round(120 * lightness + 26)}, ${Math.round(112 * lightness + 34)}, 1)`;
    }
    function drawCoralReef() {
        const w = canvas.width, h = canvas.height;
        const floorY = h + 6;

        let bed = ctx.createLinearGradient(0, h - 120, 0, h);
        bed.addColorStop(0, "rgba(1, 10, 18, 0)"); bed.addColorStop(1, "rgba(2, 14, 20, 0.9)");
        ctx.fillStyle = bed; ctx.fillRect(0, h - 120, w, 120);

        reefRocks.forEach(rk => {
            const fade = 0.3 + rk.depth * 0.45;
            ctx.fillStyle = `rgba(2, ${Math.round(14 + rk.depth * 12)}, ${Math.round(20 + rk.depth * 14)}, ${fade})`;
            ctx.beginPath(); ctx.moveTo(rk.x - rk.rw, floorY);
            for (let b = 0; b <= rk.bumps; b++) {
                const t0 = b / rk.bumps, t1 = (b + 0.5) / rk.bumps, t2 = (b + 1) / rk.bumps;
                ctx.quadraticCurveTo(
                    rk.x - rk.rw + rk.rw * 2 * t1, floorY - rk.rh * (0.7 + ((b % 2) ? 0.45 : 0.15)),
                    rk.x - rk.rw + rk.rw * 2 * Math.min(1, t2), floorY - rk.rh * (b === rk.bumps ? 0 : 0.5)
                );
                void t0;
            }
            ctx.lineTo(rk.x + rk.rw, floorY); ctx.closePath(); ctx.fill();
        });

        reefCorals.forEach(c => {
            const sway = Math.sin(timeTick * 0.012 + c.phase) * (3 + c.height * 0.03);
            ctx.save();
            ctx.translate(c.x, floorY);
            ctx.globalAlpha = 0.32 + c.depth * 0.45;
            const body = reefTint(c.hue, 0.28 + c.depth * 0.35);

            if (c.kind === "branch") {
                ctx.strokeStyle = body; ctx.lineCap = "round";
                c.segs.forEach(s => {
                    ctx.lineWidth = s.w * (0.6 + c.depth * 0.5);
                    ctx.beginPath();
                    ctx.moveTo(s.x1 + sway * (-s.y1 / c.height) * 0.5, s.y1);
                    ctx.lineTo(s.x2 + sway * (-s.y2 / c.height) * 0.6, s.y2);
                    ctx.stroke();
                });
                ctx.fillStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.45)" : "rgba(94, 234, 212, 0.5)";
                c.segs.filter(s => s.tip).forEach(s => {
                    ctx.beginPath(); ctx.arc(s.x2 + sway * (-s.y2 / c.height) * 0.6, s.y2, Math.max(1.2, s.w * 0.7), 0, Math.PI * 2); ctx.fill();
                });
            } else if (c.kind === "fan") {
                const fh = c.height * 0.8, fw = c.height * 1.15;
                let fg = ctx.createLinearGradient(0, 0, 0, -fh);
                fg.addColorStop(0, body); fg.addColorStop(1, c.hue === "amber" ? "rgba(150, 92, 34, 0.14)" : "rgba(38, 160, 145, 0.14)");
                ctx.fillStyle = fg; ctx.globalAlpha *= 0.7;
                ctx.beginPath(); ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-fw * 0.55 + sway * 0.6, -fh * 0.35, -fw * 0.5 + sway, -fh * 0.92);
                ctx.quadraticCurveTo(0 + sway, -fh * 1.05, fw * 0.5 + sway, -fh * 0.92);
                ctx.quadraticCurveTo(fw * 0.55 + sway * 0.6, -fh * 0.35, 0, 0);
                ctx.closePath(); ctx.fill();
                ctx.strokeStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.14)" : "rgba(190, 245, 240, 0.14)"; ctx.lineWidth = 1;
                for (let i = -4; i <= 4; i++) {
                    ctx.beginPath(); ctx.moveTo(0, 0);
                    ctx.quadraticCurveTo(i * fw * 0.09 + sway * 0.5, -fh * 0.5, i * fw * 0.115 + sway, -fh * 0.9); ctx.stroke();
                }
            } else {
                ctx.strokeStyle = body; ctx.lineCap = "round";
                c.tubes.forEach((t, i) => {
                    ctx.lineWidth = t.wid * (0.6 + c.depth * 0.5);
                    const lean = t.dx * 0.35;
                    ctx.beginPath(); ctx.moveTo(t.dx, 0);
                    ctx.quadraticCurveTo(t.dx + lean * 0.5 + sway * 0.4, -t.len * 0.65, t.dx + lean + sway, -t.len); ctx.stroke();
                    ctx.fillStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.25)" : "rgba(94, 234, 212, 0.28)";
                    ctx.beginPath(); ctx.ellipse(t.dx + lean + sway, -t.len, t.wid * 0.6, t.wid * 0.35, 0, 0, Math.PI * 2); ctx.fill();
                    void i;
                });
            }
            ctx.restore();
        });
    }

    /* ---------- Glowing sea anemones (front layer, additive bloom) ---------- */
    function drawAnemones() {
        const floorY = canvas.height + 4;
        reefAnemones.forEach(a => {
            const rgb = a.hue === "amber" ? "250, 204, 21" : "94, 234, 212";
            const pulse = 0.55 + Math.sin(timeTick * 0.03 + a.phase) * 0.25;
            ctx.save();
            ctx.translate(a.x, floorY - a.lift);
            ctx.globalCompositeOperation = "lighter";
            let glow = ctx.createRadialGradient(0, 0, 1, 0, 0, a.base * 2.4);
            glow.addColorStop(0, `rgba(${rgb}, ${0.18 * pulse})`); glow.addColorStop(1, `rgba(${rgb}, 0)`);
            ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(0, 0, a.base * 2.4, 0, Math.PI * 2); ctx.fill();

            ctx.lineCap = "round";
            for (let i = 0; i < a.tentacles; i++) {
                const spread = (i / (a.tentacles - 1) - 0.5) * Math.PI * 0.9;
                const wave = Math.sin(timeTick * 0.04 + a.phase + i * 0.7) * a.base * 0.22;
                const ex = Math.sin(spread) * a.base * 1.05 + wave;
                const ey = -a.base * (0.35 + Math.cos(spread) * 0.45);
                ctx.strokeStyle = `rgba(${rgb}, ${0.32 * pulse})`; ctx.lineWidth = Math.max(1.6, a.base * 0.14);
                ctx.beginPath(); ctx.moveTo(0, a.lift * 0.35);
                ctx.quadraticCurveTo(ex * 0.45, ey * 1.15, ex, ey);
                ctx.stroke();
                ctx.fillStyle = `rgba(${rgb}, ${0.36 * pulse})`;
                ctx.beginPath(); ctx.arc(ex, ey, Math.max(1.1, a.base * 0.1), 0, Math.PI * 2); ctx.fill();
            }
            ctx.globalCompositeOperation = "source-over";
            ctx.fillStyle = `rgba(2, 16, 22, 0.9)`; ctx.beginPath();
            ctx.ellipse(0, a.lift * 0.5, a.base * 0.55, a.base * 0.4, 0, 0, Math.PI * 2); ctx.fill();
            ctx.restore();
        });
    }

    /* ---------- Fine drifting plankton / marine snow ---------- */
    function drawPlankton(dt) {
        ctx.save(); ctx.globalCompositeOperation = "lighter";
        driftPlankton.forEach(p => {
            p.y -= p.speed * dt; p.x += p.drift * dt;
            if (p.y < -5) p.y = canvas.height + 5; if (p.x < -5) p.x = canvas.width + 5; if (p.x > canvas.width + 5) p.x = -5;
            const tw = 0.35 + 0.4 * Math.sin(timeTick * 0.03 + p.phase);
            ctx.fillStyle = `rgba(190, 220, 255, ${Math.max(0.05, tw)})`;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
        });
        ctx.restore();
    }

    /* ---------- Lightweight background schooling fish (pure atmosphere, no collision) ---------- */
    function drawSchoolFish(dt) {
        schoolFish.forEach(school => {
            school.x += school.vx * dt; school.bobPhase += dt * 0.05;
            const bob = Math.sin(school.bobPhase) * 14;
            if (school.x > canvas.width + 80) school.x = -80; if (school.x < -80) school.x = canvas.width + 80;
            const species = FISH_SPECIES[school.speciesIdx];
            school.members.forEach(m => {
                const mx = school.x + m.ox, my = school.y + m.oy + bob;
                const wag = Math.sin(timeTick * 0.15 + m.phase) * school.radius * 0.5;
                ctx.save();
                ctx.globalCompositeOperation = "lighter";
                ctx.globalAlpha = 0.35;
                let sg = ctx.createRadialGradient(mx, my, 0, mx, my, school.radius * 3);
                sg.addColorStop(0, `rgba(${species.glow}, 0.5)`); sg.addColorStop(1, `rgba(${species.glow}, 0)`);
                ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(mx, my, school.radius * 3, 0, Math.PI * 2); ctx.fill();
                ctx.globalCompositeOperation = "source-over";
                ctx.globalAlpha = 0.6;
                ctx.translate(mx, my);
                if (school.vx < 0) ctx.scale(-1, 1);
                ctx.fillStyle = species.bands[1];
                ctx.beginPath();
                ctx.moveTo(school.radius * 1.3, 0);
                ctx.quadraticCurveTo(0, -school.radius * 0.8, -school.radius * 1.1, wag * 0.2);
                ctx.quadraticCurveTo(0, school.radius * 0.8, school.radius * 1.3, 0);
                ctx.closePath(); ctx.fill();
                ctx.fillStyle = species.finColor;
                ctx.beginPath(); ctx.moveTo(-school.radius * 1.0, 0); ctx.lineTo(-school.radius * 1.9, wag); ctx.lineTo(-school.radius * 1.0, school.radius * 0.5); ctx.closePath(); ctx.fill();
                ctx.restore();
            });
        });
    }

    /* ---------- Drifting bioluminescent jellyfish ---------- */
    function drawJellyfish(dt) {
        jellyfish.forEach(j => {
            j.phase += dt * j.driftSpeed;
            j.y += Math.sin(j.phase * 0.4) * 0.12 * dt;
            j.x += Math.cos(j.phase * 0.15) * 0.08 * dt;
            if (j.y < -40) j.y = canvas.height + 40; if (j.y > canvas.height + 40) j.y = -40;
            const pulse = 0.6 + Math.sin(j.phase * 2) * 0.4;
            ctx.save();
            ctx.translate(j.x, j.y);
            ctx.globalCompositeOperation = "lighter";
            let glow = ctx.createRadialGradient(0, 0, 1, 0, 0, j.size * 2.6);
            glow.addColorStop(0, `rgba(${j.hue}, ${0.30 * pulse})`); glow.addColorStop(1, `rgba(${j.hue}, 0)`);
            ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(0, 0, j.size * 2.6, 0, Math.PI * 2); ctx.fill();

            const bellSquash = 1 + Math.sin(j.phase * 2) * 0.18;
            ctx.fillStyle = `rgba(${j.hue}, ${0.5 * pulse})`;
            ctx.beginPath(); ctx.ellipse(0, 0, j.size * 0.7, j.size * 0.55 * bellSquash, 0, Math.PI, 0); ctx.fill();
            ctx.strokeStyle = `rgba(${j.hue}, ${0.34 * pulse})`; ctx.lineWidth = Math.max(1, j.size * 0.05); ctx.lineCap = "round";
            for (let t = -3; t <= 3; t++) {
                const sway = Math.sin(j.phase * 1.6 + t) * j.size * 0.25;
                ctx.beginPath(); ctx.moveTo(t * j.size * 0.16, j.size * 0.05);
                ctx.quadraticCurveTo(t * j.size * 0.16 + sway * 0.5, j.size * 0.9, t * j.size * 0.16 + sway, j.size * 1.6);
                ctx.stroke();
            }
            ctx.globalCompositeOperation = "source-over";
            ctx.restore();
        });
    }

    /* ---------- Cruising megafauna: sea turtle or manta ray silhouettes, purely decorative ---------- */
    function drawMegafauna(dt) {
        if (!megafaunaCreature) return;
        const m = megafaunaCreature;
        m.x += m.vx * dt; m.phase += dt * 0.05;
        m.y += Math.sin(m.phase * 2) * 0.15;
        if (m.x > canvas.width + 140 || m.x < -140) { regenerateMegafauna(); return; }
        ctx.save();
        ctx.translate(m.x, m.y);
        if (m.vx < 0) ctx.scale(-1, 1);
        ctx.globalAlpha = 0.42;
        if (m.kind === "ray") {
            const flap = Math.sin(m.phase * 4) * m.size * 0.28;
            ctx.fillStyle = "#1a222e";
            ctx.beginPath();
            ctx.moveTo(m.size * 1.1, 0);
            ctx.quadraticCurveTo(m.size * 0.3, -m.size * 0.5 + flap, -m.size * 0.9, -m.size * 0.15);
            ctx.quadraticCurveTo(-m.size * 0.4, 0, -m.size * 0.9, m.size * 0.15);
            ctx.quadraticCurveTo(m.size * 0.3, m.size * 0.5 - flap, m.size * 1.1, 0);
            ctx.closePath(); ctx.fill();
            ctx.strokeStyle = "rgba(148,163,184,0.3)"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(-m.size * 0.85, 0); ctx.lineTo(-m.size * 1.6, m.size * 0.35); ctx.stroke();
        } else if (m.kind === "turtle") {
            const paddle = Math.sin(m.phase * 3) * 0.35;
            ctx.fillStyle = "#233a26";
            ctx.beginPath(); ctx.ellipse(0, 0, m.size * 0.62, m.size * 0.46, 0, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "rgba(4,14,8,0.4)"; ctx.lineWidth = 1.4;
            for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.moveTo(i * m.size * 0.24, -m.size * 0.4); ctx.lineTo(i * m.size * 0.24, m.size * 0.4); ctx.stroke(); }
            ctx.beginPath(); ctx.ellipse(m.size * 0.72, 0, m.size * 0.2, m.size * 0.14, 0, 0, Math.PI * 2); ctx.fill();
            ctx.save(); ctx.rotate(paddle * 0.5);
            ctx.beginPath(); ctx.ellipse(-m.size * 0.1, -m.size * 0.55, m.size * 0.32, m.size * 0.14, 0.4, 0, Math.PI * 2); ctx.fill();
            ctx.restore();
            ctx.save(); ctx.rotate(-paddle * 0.5);
            ctx.beginPath(); ctx.ellipse(-m.size * 0.1, m.size * 0.55, m.size * 0.32, m.size * 0.14, -0.4, 0, Math.PI * 2); ctx.fill();
            ctx.restore();
        }
        ctx.restore();
    }

    /* ---------- Landmark silhouettes: a shipwreck for mid-depth chapters, ruins for the abyss ---------- */
    function drawLandmark() {
        if (!landmarkDecor) return;
        const floorY = canvas.height + 4; const s = landmarkDecor.scale;
        ctx.save(); ctx.translate(landmarkDecor.x, floorY); ctx.scale(s, s); ctx.globalAlpha = 0.45;
        ctx.fillStyle = "#050b12";
        if (landmarkDecor.kind === "shipwreck") {
            ctx.beginPath();
            ctx.moveTo(-140, 0); ctx.lineTo(120, 0); ctx.lineTo(90, -46); ctx.lineTo(-40, -58); ctx.lineTo(-120, -34); ctx.closePath(); ctx.fill();
            ctx.strokeStyle = "rgba(148,163,184,0.2)"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(-10, -58); ctx.lineTo(-10, -140); ctx.moveTo(-10, -110); ctx.lineTo(46, -96); ctx.stroke();
            for (let i = -100; i < 100; i += 26) { ctx.beginPath(); ctx.moveTo(i, -6); ctx.lineTo(i + 14, -34); ctx.stroke(); }
        } else if (landmarkDecor.kind === "ruins") {
            for (let i = 0; i < 3; i++) {
                const px = -110 + i * 110;
                ctx.fillRect(px - 12, -90, 24, 90);
                ctx.beginPath(); ctx.ellipse(px, -90, 18, 8, 0, 0, Math.PI * 2); ctx.fill();
            }
            ctx.beginPath(); ctx.moveTo(-130, -84); ctx.lineTo(130, -84); ctx.lineTo(110, -100); ctx.lineTo(-110, -100); ctx.closePath(); ctx.fill();
        }
        ctx.restore();
    }

    // Bioluminescent halo drawn around every fish (not just threats) — a soft radial glow using the
    // species' own glow color, plus an extra hot inner core near the head for that "lit from within" look.
    function drawBioGlow(r, glowRgb, intensity) {
        const outer = r * 2.3;
        let g = ctx.createRadialGradient(r * 0.15, 0, r * 0.3, 0, 0, outer);
        g.addColorStop(0, `rgba(${glowRgb}, ${0.32 * intensity})`);
        g.addColorStop(0.4, `rgba(${glowRgb}, ${0.14 * intensity})`);
        g.addColorStop(1, `rgba(${glowRgb}, 0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, outer * 1.1, outer * 0.8, 0, 0, Math.PI * 2); ctx.fill();
    }
    function drawAura(r, colorRgb, strong) {
        const outer = strong ? r * 1.5 : r * 1.3;
        const peakAlpha = strong ? 0.4 : 0.22;
        let g = ctx.createRadialGradient(0, 0, r * 0.7, 0, 0, outer);
        g.addColorStop(0, `rgba(${colorRgb}, ${peakAlpha})`); g.addColorStop(1, `rgba(${colorRgb}, 0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, outer * 1.12, outer * 0.82, 0, 0, Math.PI * 2); ctx.fill();
    }
"""
game_html += r"""
    // Real fish outline: pointed snout at +x, full mid-body, tapering down to a narrow tail peduncle at -x.
    function traceFishBody(r, profile) {
        ctx.beginPath();
        switch (profile) {
            case "disc":
                ctx.moveTo(r * 1.02, r * 0.10);
                ctx.bezierCurveTo(r * 0.78, -r * 0.70, r * 0.26, -r * 1.12, -r * 0.18, -r * 1.02);
                ctx.bezierCurveTo(-r * 0.50, -r * 0.94, -r * 0.78, -r * 0.60, -r * 0.92, -r * 0.22);
                ctx.quadraticCurveTo(-r * 0.98, 0, -r * 0.92, r * 0.22);
                ctx.bezierCurveTo(-r * 0.74, r * 0.70, -r * 0.44, r * 1.12, r * 0.06, r * 1.10);
                ctx.bezierCurveTo(r * 0.54, r * 1.06, r * 0.86, r * 0.60, r * 1.02, r * 0.10);
                break;
            case "tall":
                ctx.moveTo(r * 1.06, r * 0.08);
                ctx.bezierCurveTo(r * 0.80, -r * 0.78, r * 0.30, -r * 1.16, -r * 0.10, -r * 1.10);
                ctx.bezierCurveTo(-r * 0.48, -r * 1.04, -r * 0.76, -r * 0.60, -r * 0.94, -r * 0.20);
                ctx.quadraticCurveTo(-r * 1.00, 0, -r * 0.94, r * 0.20);
                ctx.bezierCurveTo(-r * 0.72, r * 0.62, -r * 0.40, r * 1.14, r * 0.06, r * 1.12);
                ctx.bezierCurveTo(r * 0.56, r * 1.10, r * 0.90, r * 0.62, r * 1.06, r * 0.08);
                break;
            case "torpedo":
                ctx.moveTo(r * 1.22, r * 0.04);
                ctx.bezierCurveTo(r * 0.90, -r * 0.34, r * 0.30, -r * 0.72, -r * 0.20, -r * 0.70);
                ctx.bezierCurveTo(-r * 0.56, -r * 0.68, -r * 0.82, -r * 0.44, -r * 1.02, -r * 0.14);
                ctx.quadraticCurveTo(-r * 1.08, 0, -r * 1.02, r * 0.14);
                ctx.bezierCurveTo(-r * 0.80, r * 0.46, -r * 0.50, r * 0.70, r * 0.06, r * 0.72);
                ctx.bezierCurveTo(r * 0.58, r * 0.74, r * 0.96, r * 0.42, r * 1.22, r * 0.04);
                break;
            case "slim":
                ctx.moveTo(r * 1.14, r * 0.05);
                ctx.bezierCurveTo(r * 0.86, -r * 0.40, r * 0.40, -r * 0.74, -r * 0.10, -r * 0.72);
                ctx.bezierCurveTo(-r * 0.48, -r * 0.70, -r * 0.76, -r * 0.48, -r * 0.98, -r * 0.16);
                ctx.quadraticCurveTo(-r * 1.04, 0, -r * 0.98, r * 0.16);
                ctx.bezierCurveTo(-r * 0.74, r * 0.50, -r * 0.42, r * 0.74, r * 0.06, r * 0.76);
                ctx.bezierCurveTo(r * 0.56, r * 0.78, r * 0.92, r * 0.44, r * 1.14, r * 0.05);
                break;
            case "bulb":
                ctx.moveTo(r * 1.14, r * 0.28);
                ctx.bezierCurveTo(r * 1.02, -r * 0.60, r * 0.50, -r * 1.06, -r * 0.02, -r * 0.96);
                ctx.bezierCurveTo(-r * 0.44, -r * 0.88, -r * 0.74, -r * 0.52, -r * 0.94, -r * 0.18);
                ctx.quadraticCurveTo(-r * 1.00, 0, -r * 0.94, r * 0.18);
                ctx.bezierCurveTo(-r * 0.72, r * 0.54, -r * 0.40, r * 0.92, r * 0.10, r * 1.00);
                ctx.bezierCurveTo(r * 0.62, r * 1.06, r * 1.04, r * 0.86, r * 1.14, r * 0.28);
                break;
            default:
                ctx.moveTo(r * 1.10, r * 0.06);
                ctx.bezierCurveTo(r * 0.86, -r * 0.44, r * 0.42, -r * 0.92, -r * 0.06, -r * 0.90);
                ctx.bezierCurveTo(-r * 0.44, -r * 0.88, -r * 0.72, -r * 0.58, -r * 0.94, -r * 0.20);
                ctx.quadraticCurveTo(-r * 1.00, 0, -r * 0.94, r * 0.20);
                ctx.bezierCurveTo(-r * 0.70, r * 0.60, -r * 0.38, r * 0.92, r * 0.06, r * 0.94);
                ctx.bezierCurveTo(r * 0.52, r * 0.96, r * 0.90, r * 0.52, r * 1.10, r * 0.06);
        }
        ctx.closePath();
    }

    function drawRealisticFish(x, y, r, isLeft, species, fishType, pulseTick, speedMag, tiltAngle, depthScale, auraColorRgb) {
        ctx.save(); ctx.translate(x, y); ctx.scale(depthScale, depthScale); if (isLeft) ctx.scale(-1, 1);
        ctx.rotate(Math.max(-0.3, Math.min(0.3, tiltAngle)) * (isLeft ? -1 : 1));

        // Bioluminescent halo — every fish glows with its own species color; threats/edibles get an
        // extra colored ring layered on top so the gameplay signal still reads clearly.
        if (species && species.glow) {
            ctx.save(); ctx.globalCompositeOperation = "lighter";
            drawBioGlow(r, species.glow, 1);
            ctx.restore();
        }
        if (auraColorRgb) drawAura(r, auraColorRgb, auraColorRgb === "239, 68, 68");

        const shape = (species && species.shape) ? species.shape : { profile: "balanced", yScale: 0.80, tail: "fan", dorsal: "low", wag: 1.0, extra: null };

        const wagSpeed = (0.1 + Math.min(0.28, speedMag * 0.2)) * shape.wag;
        const wag = Math.sin(pulseTick * wagSpeed) * (r * (0.2 + Math.min(0.15, speedMag * 0.1)));
        const tailWag = Math.sin(pulseTick * wagSpeed + 0.6) * (r * 0.34);
        const bodyYScale = shape.yScale;

        ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = "#000208"; ctx.beginPath(); ctx.ellipse(r * 0.05, r * (0.95 * bodyYScale + 0.35), r * 0.95, r * 0.22, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        const tx = -r * 0.92;
        let tailGrd = ctx.createLinearGradient(tx, 0, -r * 2.2, 0);
        tailGrd.addColorStop(0, species.bands[2]); tailGrd.addColorStop(0.55, species.bands[1]); tailGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = tailGrd; ctx.globalAlpha = 0.9;
        ctx.beginPath();
        if (shape.tail === "fork") {
            ctx.moveTo(tx, -r * 0.12 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.5, -r * 0.95 + tailWag, -r * 2.15, -r * 1.05 + tailWag);
            ctx.quadraticCurveTo(-r * 1.42, -r * 0.16 + tailWag * 0.7, -r * 1.30, tailWag * 0.6);
            ctx.quadraticCurveTo(-r * 1.42, r * 0.16 + tailWag * 0.7, -r * 2.15, r * 1.05 + tailWag);
            ctx.quadraticCurveTo(-r * 1.5, r * 0.95 + tailWag, tx, r * 0.12 * bodyYScale);
        } else if (shape.tail === "lunate") {
            ctx.moveTo(tx, -r * 0.10 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.7, -r * 1.02 + tailWag, -r * 2.35, -r * 1.16 + tailWag);
            ctx.quadraticCurveTo(-r * 1.9, -r * 0.4 + tailWag, -r * 1.28, tailWag * 0.5);
            ctx.quadraticCurveTo(-r * 1.9, r * 0.4 + tailWag, -r * 2.35, r * 1.16 + tailWag);
            ctx.quadraticCurveTo(-r * 1.7, r * 1.02 + tailWag, tx, r * 0.10 * bodyYScale);
        } else if (shape.tail === "flow") {
            ctx.moveTo(tx, -r * 0.16 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.7, -r * 1.35 + tailWag * 1.3, -r * 2.35, -r * 0.55 + tailWag * 1.5);
            ctx.quadraticCurveTo(-r * 1.55, -r * 0.25 + tailWag, -r * 1.4, tailWag * 0.8);
            ctx.quadraticCurveTo(-r * 1.55, r * 0.25 + tailWag, -r * 2.35, r * 0.55 + tailWag * 1.5);
            ctx.quadraticCurveTo(-r * 1.7, r * 1.35 + tailWag * 1.3, tx, r * 0.16 * bodyYScale);
        } else {
            ctx.moveTo(tx, -r * 0.14 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.45, -r * 0.78 + tailWag, -r * 1.95, -r * 0.72 + tailWag);
            ctx.quadraticCurveTo(-r * 1.55, tailWag * 0.9, -r * 1.95, r * 0.72 + tailWag);
            ctx.quadraticCurveTo(-r * 1.45, r * 0.78 + tailWag, tx, r * 0.14 * bodyYScale);
        }
        ctx.closePath(); ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.28)"; ctx.lineWidth = Math.max(0.6, r * 0.035); ctx.globalAlpha = 0.55;
        for (let i = -2; i <= 2; i++) {
            ctx.beginPath(); ctx.moveTo(tx, 0);
            ctx.quadraticCurveTo(-r * 1.4, i * r * 0.3 + tailWag * 0.8, -r * 1.9, i * r * 0.38 + tailWag);
            ctx.stroke();
        }
        ctx.globalAlpha = 1;

        const dorsalH = shape.dorsal === "sail" ? 1.95 : (shape.dorsal === "spiny" ? 1.55 : 1.45);
        let dorsalGrd = ctx.createLinearGradient(0, -r * bodyYScale * 0.85, 0, -r * bodyYScale * (dorsalH + 0.3));
        dorsalGrd.addColorStop(0, species.bands[1]); dorsalGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = dorsalGrd; ctx.globalAlpha = 0.94;
        ctx.beginPath();
        ctx.moveTo(-r * 0.72, -r * 0.55 * bodyYScale);
        ctx.quadraticCurveTo(-r * 0.30, -r * (dorsalH * bodyYScale) + wag * 0.3, r * 0.16, -r * ((dorsalH - 0.23) * bodyYScale));
        ctx.quadraticCurveTo(r * 0.34, -r * (0.98 * bodyYScale), r * 0.42, -r * (0.72 * bodyYScale));
        ctx.quadraticCurveTo(-r * 0.10, -r * (0.86 * bodyYScale), -r * 0.72, -r * 0.55 * bodyYScale);
        ctx.closePath(); ctx.fill();
        if (shape.dorsal === "spiny") {
            ctx.strokeStyle = "rgba(255,255,255,0.30)"; ctx.lineWidth = Math.max(0.5, r * 0.03);
            for (let i = 0; i <= 4; i++) {
                const fx = -r * 0.5 + i * r * 0.22;
                ctx.beginPath(); ctx.moveTo(fx, -r * 0.6 * bodyYScale);
                ctx.lineTo(fx + r * 0.04, -r * (dorsalH - 0.35) * bodyYScale + wag * 0.2); ctx.stroke();
            }
        }
        ctx.globalAlpha = 1;

        ctx.fillStyle = species.finColor; ctx.globalAlpha = 0.8;
        ctx.beginPath();
        ctx.moveTo(-r * 0.62, r * 0.52 * bodyYScale);
        ctx.quadraticCurveTo(-r * 0.42, r * (1.18 * bodyYScale) + wag * 0.35, -r * 0.02, r * (1.02 * bodyYScale));
        ctx.quadraticCurveTo(-r * 0.28, r * (0.80 * bodyYScale), -r * 0.62, r * 0.52 * bodyYScale);
        ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;

        ctx.save();
        ctx.scale(1, bodyYScale);
        ctx.save();
        traceFishBody(r, shape.profile); ctx.clip();

        ctx.fillStyle = species.bands[0]; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.fillStyle = species.bands[1];
        ctx.beginPath(); ctx.moveTo(-r * 0.18, -r * 1.3); ctx.lineTo(r * 0.22, -r * 1.3); ctx.lineTo(-r * 0.08, r * 1.3); ctx.lineTo(-r * 0.48, r * 1.3); ctx.closePath(); ctx.fill();
        ctx.fillStyle = species.bands[2];
        ctx.beginPath(); ctx.moveTo(r * 0.30, -r * 1.3); ctx.lineTo(r * 0.64, -r * 1.3); ctx.lineTo(r * 0.38, r * 1.3); ctx.lineTo(r * 0.04, r * 1.3); ctx.closePath(); ctx.fill();
        let pedGrd = ctx.createLinearGradient(-r * 0.45, 0, -r * 1.0, 0);
        pedGrd.addColorStop(0, "rgba(0,0,0,0)"); pedGrd.addColorStop(1, "rgba(1,3,10,0.55)");
        ctx.fillStyle = pedGrd; ctx.fillRect(-r * 1.3, -r * 1.3, r * 1.3, r * 2.6);

        const scaleStep = Math.max(3.2, r * 0.24);
        ctx.lineWidth = Math.max(0.5, r * 0.028);
        for (let pass = 0; pass < 2; pass++) {
            ctx.strokeStyle = pass === 0 ? "rgba(1,4,12,0.28)" : "rgba(255,255,255,0.20)";
            const shift = pass === 0 ? scaleStep * 0.12 : 0;
            for (let sy = -r * 0.9; sy < r * 0.9; sy += scaleStep) {
                for (let sx = -r * 0.9; sx < r * 1.0; sx += scaleStep) {
                    const off = (Math.round((sy + r) / scaleStep) % 2) * scaleStep * 0.5;
                    ctx.beginPath(); ctx.arc(sx + off, sy + shift, scaleStep * 0.52, Math.PI * 0.15, Math.PI * 0.85); ctx.stroke();
                }
            }
        }
        ctx.strokeStyle = "rgba(0,0,0,0.22)"; ctx.lineWidth = Math.max(0.6, r * 0.04);
        ctx.beginPath(); ctx.moveTo(r * 0.72, -r * 0.06); ctx.quadraticCurveTo(0, r * 0.10, -r * 0.88, r * 0.02); ctx.stroke();

        ctx.save(); ctx.globalAlpha = 0.85; ctx.fillStyle = species.maskColor;
        ctx.beginPath(); ctx.moveTo(r * 0.62, -r * 1.3); ctx.lineTo(r * 0.82, -r * 1.3); ctx.lineTo(r * 0.50, r * 1.3); ctx.lineTo(r * 0.30, r * 1.3); ctx.closePath(); ctx.fill(); ctx.restore();

        ctx.strokeStyle = "rgba(1,4,10,0.4)"; ctx.lineWidth = Math.max(0.8, r * 0.055);
        ctx.beginPath(); ctx.moveTo(r * 0.30, -r * 0.66); ctx.quadraticCurveTo(r * 0.10, 0, r * 0.34, r * 0.62); ctx.stroke();

        let shadeGrd = ctx.createRadialGradient(r * 0.25, -r * 0.42, r * 0.08, 0, 0, r * 1.25);
        shadeGrd.addColorStop(0, "rgba(255,255,255,0.85)"); shadeGrd.addColorStop(0.45, "rgba(255,255,255,0.16)"); shadeGrd.addColorStop(1, "rgba(4,6,16,0.7)");
        ctx.globalCompositeOperation = "multiply"; ctx.fillStyle = shadeGrd; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.globalCompositeOperation = "source-over";
        let bellyGrd = ctx.createLinearGradient(0, r * 0.2, 0, r * 1.0);
        bellyGrd.addColorStop(0, "rgba(255,255,255,0)"); bellyGrd.addColorStop(1, "rgba(255,255,255,0.30)");
        ctx.fillStyle = bellyGrd; ctx.fillRect(-r * 1.3, 0, r * 2.7, r * 1.3);

        // Bioluminescent "hot core" near the head/gill — the signature glow-from-within look.
        ctx.globalCompositeOperation = "screen";
        let core = ctx.createRadialGradient(r * 0.32, -r * 0.05, 0, r * 0.32, -r * 0.05, r * 0.85);
        core.addColorStop(0, `rgba(${species.glow || "255,255,255"}, 0.55)`);
        core.addColorStop(0.5, `rgba(${species.glow || "255,255,255"}, 0.18)`);
        core.addColorStop(1, `rgba(${species.glow || "255,255,255"}, 0)`);
        ctx.fillStyle = core; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);

        let sheen = ctx.createRadialGradient(r * 0.34, -r * 0.5, r * 0.04, r * 0.05, -r * 0.05, r * 1.3);
        sheen.addColorStop(0, "rgba(226, 250, 255, 0.45)");
        sheen.addColorStop(0.34, "rgba(140, 210, 235, 0.16)");
        sheen.addColorStop(1, "rgba(120, 190, 220, 0)");
        ctx.fillStyle = sheen; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        let bounce = ctx.createRadialGradient(-r * 0.25, r * 0.6, r * 0.03, -r * 0.2, r * 0.55, r * 1.0);
        bounce.addColorStop(0, `rgba(${species.glow || "94,234,212"}, 0.22)`);
        bounce.addColorStop(1, `rgba(${species.glow || "94,234,212"}, 0)`);
        ctx.fillStyle = bounce; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.globalCompositeOperation = "source-over";

        let spec = ctx.createRadialGradient(r * 0.4, -r * 0.44, 0, r * 0.4, -r * 0.44, r * 0.52);
        spec.addColorStop(0, "rgba(255,255,255,0.9)"); spec.addColorStop(0.45, "rgba(255,255,255,0.22)"); spec.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = spec; ctx.beginPath(); ctx.ellipse(r * 0.4, -r * 0.42, r * 0.5, r * 0.26, -0.35, 0, Math.PI * 2); ctx.fill();
        let spec2 = ctx.createRadialGradient(r * 0.86, -r * 0.1, 0, r * 0.86, -r * 0.1, r * 0.26);
        spec2.addColorStop(0, "rgba(255,255,255,0.6)"); spec2.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = spec2; ctx.beginPath(); ctx.ellipse(r * 0.86, -r * 0.1, r * 0.24, r * 0.16, 0, 0, Math.PI * 2); ctx.fill();

        ctx.globalCompositeOperation = "lighter";
        for (let sp = 0; sp < 3; sp++) {
            const twinkle = 0.4 + 0.6 * Math.max(0, Math.sin(pulseTick * 0.18 + sp * 2.4));
            if (twinkle < 0.55) continue;
            const spx = r * (-0.35 + sp * 0.42) + Math.sin(pulseTick * 0.05 + sp) * r * 0.06;
            const spy = -r * 0.15 + Math.cos(pulseTick * 0.07 + sp * 1.3) * r * 0.35;
            ctx.fillStyle = `rgba(255,255,255,${0.5 * twinkle})`;
            ctx.beginPath(); ctx.arc(spx, spy, Math.max(0.6, r * 0.045), 0, Math.PI * 2); ctx.fill();
        }
        ctx.globalCompositeOperation = "source-over";

        ctx.restore();

        traceFishBody(r, shape.profile);
        ctx.strokeStyle = "rgba(1,3,10,0.6)"; ctx.lineWidth = Math.max(1, r * 0.06); ctx.stroke();
        ctx.save(); ctx.clip();
        ctx.strokeStyle = `rgba(${species.glow || "255,255,255"}, 0.5)`; ctx.lineWidth = Math.max(1, r * 0.10);
        ctx.beginPath(); ctx.moveTo(r * 0.92, -r * 0.30); ctx.bezierCurveTo(r * 0.45, -r * 0.92, -r * 0.10, -r * 0.95, -r * 0.60, -r * 0.62); ctx.stroke();
        ctx.restore();

        ctx.save();
        ctx.globalAlpha = 0.62; ctx.fillStyle = species.finColor;
        const pecWag = Math.sin(pulseTick * (wagSpeed + 0.06)) * (r * 0.16);
        ctx.beginPath();
        ctx.moveTo(r * 0.24, r * 0.06);
        ctx.quadraticCurveTo(-r * 0.10, r * 0.52 + pecWag, -r * 0.34, r * 0.30 + pecWag);
        ctx.quadraticCurveTo(-r * 0.06, r * 0.16, r * 0.24, r * 0.06);
        ctx.closePath(); ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.35)"; ctx.lineWidth = Math.max(0.5, r * 0.03); ctx.stroke();
        ctx.restore();

        ctx.strokeStyle = "rgba(1,4,10,0.65)"; ctx.lineWidth = Math.max(0.8, r * 0.05);
        ctx.beginPath(); ctx.moveTo(r * 1.06, r * 0.10); ctx.quadraticCurveTo(r * 0.90, r * 0.20, r * 0.78, r * 0.16); ctx.stroke();

        ctx.restore();

        let eyeX = r * 0.66; let eyeY = -r * 0.28 * bodyYScale; let eyeRadius = Math.max(2.5, r * 0.17);
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius * 1.18, 0, Math.PI * 2); ctx.fill();
        let eyeGrd = ctx.createRadialGradient(eyeX - eyeRadius * 0.2, eyeY - eyeRadius * 0.2, 1, eyeX, eyeY, eyeRadius);
        eyeGrd.addColorStop(0, "#fdfdff"); eyeGrd.addColorStop(1, "#b9c6d4");
        ctx.fillStyle = eyeGrd; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#020617"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.12, eyeY, eyeRadius * 0.52, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.34, eyeY - eyeRadius * 0.24, eyeRadius * 0.17, 0, Math.PI * 2); ctx.fill();

        if (shape.extra === "finlets") {
            ctx.fillStyle = species.finColor; ctx.globalAlpha = 0.85;
            for (let i = 0; i < 4; i++) {
                const fx = -r * 0.5 - i * r * 0.16;
                ctx.beginPath(); ctx.moveTo(fx, -r * 0.42); ctx.lineTo(fx - r * 0.08, -r * 0.56); ctx.lineTo(fx - r * 0.12, -r * 0.42); ctx.closePath(); ctx.fill();
                ctx.beginPath(); ctx.moveTo(fx, r * 0.42); ctx.lineTo(fx - r * 0.08, r * 0.56); ctx.lineTo(fx - r * 0.12, r * 0.42); ctx.closePath(); ctx.fill();
            }
            ctx.globalAlpha = 1;
        } else if (shape.extra === "lure") {
            const bob = Math.sin(pulseTick * 0.09) * r * 0.12;
            const bx = r * 1.15, by = -r * 0.95 * bodyYScale + bob;
            ctx.strokeStyle = "rgba(220,220,235,0.6)"; ctx.lineWidth = Math.max(1, r * 0.06);
            ctx.beginPath(); ctx.moveTo(r * 0.5, -r * 0.7 * bodyYScale); ctx.quadraticCurveTo(r * 1.0, -r * 1.2 * bodyYScale, bx, by); ctx.stroke();
            const glow = ctx.createRadialGradient(bx, by, 0, bx, by, r * 0.45);
            glow.addColorStop(0, "rgba(255,240,180,0.95)"); glow.addColorStop(0.4, "rgba(255,210,120,0.5)"); glow.addColorStop(1, "rgba(255,200,90,0)");
            ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(bx, by, r * 0.45, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#fff6d6"; ctx.beginPath(); ctx.arc(bx, by, Math.max(1.5, r * 0.11), 0, Math.PI * 2); ctx.fill();
        } else if (shape.extra === "barbel") {
            ctx.strokeStyle = "rgba(200,220,225,0.5)"; ctx.lineWidth = Math.max(0.6, r * 0.03);
            const bw = Math.sin(pulseTick * 0.12) * r * 0.1;
            ctx.beginPath(); ctx.moveTo(r * 1.02, r * 0.18); ctx.quadraticCurveTo(r * 1.4, r * 0.4 + bw, r * 1.55, r * 0.7 + bw); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(r * 1.0, r * 0.24); ctx.quadraticCurveTo(r * 1.32, r * 0.5 + bw, r * 1.42, r * 0.82 + bw); ctx.stroke();
        }

        ctx.restore();
    }

    function spawnParticles(x, y, hue, count) {
        for (let i = 0; i < count; i++) particles.push({ x, y, vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3, life: 1, hue });
    }
"""
# Part E: Faster, frame-rate-independent physics; capped/targeted spawning (max 8 fish, ~3 edible + ~3 not); game loop
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; gamePaused = false; lives = MAX_LIVES;
        player.tier = 0; player.eatenThisTier = 0; player.radius = TIER_RADII[0];
        player.x = canvas.width / 2; player.y = canvas.height / 2; player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; environmentBubbles = []; particles = []; screenShake = 0; lastTimestamp = null;
        currentChapter = 0; regenerateKelp(); regenerateReef(); regeneratePlankton();
        screenOverlay.style.display = "none"; pauseOverlay.style.display = "none"; titleScreen.style.display = "none"; chapterCompleteOverlay.style.display = "none"; lifeLostOverlay.style.display = "none"; hud.style.display = "flex";
        chapterLabel.style.display = "block";
        scoreLabel.innerText = "SCORE: 00000"; updateSizeHud(); updateLivesHud();
        showChapterBanner(0);
        if (spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 650);
        if (animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }

    function updateSizeHud() {
        sizeLabel.innerText = `SIZE: ${TIER_NAMES[player.tier]}  ${player.eatenThisTier}/${FISH_PER_TIER}`;
    }

    function updateLivesHud() {
        const hearts = "♥ ".repeat(Math.max(0, lives)).trim();
        livesLabel.innerText = lives > 0 ? `LIVES ${hearts}` : "LIVES —";
    }

    function handlePlayerDeath() {
        lives--;
        updateLivesHud();
        if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
        if (spawnIntervalId) { clearInterval(spawnIntervalId); spawnIntervalId = null; }
        sound("boom"); screenShake = 14;

        if (lives <= 0) { terminateGameEngine(false); return; }

        gamePaused = true;
        const hearts = "♥ ".repeat(lives).trim();
        lifeLostHearts.innerText = hearts;
        if (lives === 1) {
            lifeLostTitle.innerText = "YOU'RE ON YOUR LAST LIFE";
            lifeLostSub.innerText = "One mistake left — respawning in the same chapter, progress kept!";
        } else {
            lifeLostTitle.innerText = `YOU GOT ${lives} LIVES LEFT`;
            lifeLostSub.innerText = "Respawning in the same chapter — keep your progress!";
        }
        lifeLostOverlay.style.display = "flex";
    }

    function respawnAfterLifeLost() {
        lifeLostOverlay.style.display = "none";
        player.x = canvas.width / 2; player.y = canvas.height / 2;
        player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; particles = []; lastTimestamp = null;
        gamePaused = false;
        if (spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 650);
        if (animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }
    lifeContinueBtn.addEventListener("click", (e) => { e.stopPropagation(); respawnAfterLifeLost(); });

    function showChapterCompleteMenu() {
        if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
        if (spawnIntervalId) { clearInterval(spawnIntervalId); spawnIntervalId = null; }
        gamePaused = true;
        const isFinal = currentChapter >= CHAPTERS.length - 1;
        chapterCompleteTitle.innerText = CHAPTERS[currentChapter].name;
        chapterCompleteSub.innerText = isFinal
            ? "You cleared the final chapter — you are the apex of the ocean!"
            : "You devoured every fish. Move on to the next chapter!";
        continueBtn.innerText = isFinal ? "FINISH ▶" : "PRESS TO CONTINUE ▶";
        chapterCompleteOverlay.style.display = "flex";
        sound("level");
    }

    function continueToNextChapter() {
        chapterCompleteOverlay.style.display = "none";
        if (currentChapter >= CHAPTERS.length - 1) { terminateGameEngine(true); return; }
        currentChapter++;
        player.tier = 0; player.eatenThisTier = 0; player.radius = TIER_RADII[0];
        player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; particles = []; lastTimestamp = null;
        regenerateKelp(); regenerateReef();
        updateSizeHud();
        showChapterBanner(currentChapter);
        gamePaused = false;
        if (spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 650);
        if (animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }
    continueBtn.addEventListener("click", (e) => { e.stopPropagation(); continueToNextChapter(); });

    function generateMarineLife() {
        if (!gameActive || gamePaused) return;
        if (marineThreats.length >= MAX_FISH_ON_SCREEN) return;
        let edibleCount = 0, inedibleCount = 0;
        marineThreats.forEach(t => { if (t.radius < player.radius) edibleCount++; else inedibleCount++; });
        const needEdible = edibleCount < TARGET_PER_SIDE; const needInedible = inedibleCount < TARGET_PER_SIDE;
        if (!needEdible && !needInedible) return;
        const makeEdible = needEdible && (!needInedible || Math.random() < 0.5);

        const spawnFromLeft = Math.random() > 0.5;
        const pool = (CHAPTERS[currentChapter] || CHAPTERS[0]).speciesPool;
        const speciesIdx = pool[Math.floor(Math.random() * pool.length)];
        const specificType = Math.floor(Math.random() * 3) + 1;
        const edibleSizes = FISH_SIZE_CLASSES.filter(s => s < player.radius);
        const threatSizes = FISH_SIZE_CLASSES.filter(s => s >= player.radius);
        let sizeRadius;
        if (makeEdible && edibleSizes.length) {
            sizeRadius = edibleSizes[Math.floor(Math.random() * edibleSizes.length)];
        } else if (threatSizes.length) {
            sizeRadius = threatSizes[Math.floor(Math.random() * threatSizes.length)];
        } else {
            sizeRadius = edibleSizes.length ? edibleSizes[Math.floor(Math.random() * edibleSizes.length)] : FISH_SIZE_CLASSES[0];
        }
        const chapterScale = 1 + currentChapter * 0.04;
        sizeRadius = sizeRadius * chapterScale * (0.9 + Math.random() * 0.2);
        if (sizeRadius < player.radius) sizeRadius = Math.min(sizeRadius, player.radius - 3);
        else sizeRadius = Math.max(sizeRadius, player.radius + 2);
        sizeRadius = Math.max(6, sizeRadius);
        const baseY = Math.random() * (canvas.height - 90) + 45;
        const baseSpeed = (Math.random() * 0.55 + 0.5) * (spawnFromLeft ? 1 : -1);
        marineThreats.push({ x: spawnFromLeft ? -60 : canvas.width + 60, y: baseY, radius: sizeRadius, vx: baseSpeed, vy: 0, fishType: specificType, speciesIdx, wagPhase: Math.random() * 100 });
    }

    function getRankName(r) { if (r < 23) return "MINNOW"; if (r < 32) return "BASS"; if (r < 42) return "TUNA"; if (r < 52) return "BARRACUDA"; return "APEX SHARK"; }

    function getChapterIndex(r) {
        let idx = 0;
        for (let i = 0; i < CHAPTERS.length; i++) { if (r >= CHAPTERS[i].minRadius) idx = i; }
        return idx;
    }
    function showChapterBanner(idx) {
        chapterBannerNum.innerText = String(idx + 1);
        chapterBannerTitle.innerText = CHAPTERS[idx].name;
        chapterLabel.innerText = `MAP ${idx + 1} / ${CHAPTERS.length} — ${CHAPTERS[idx].name}`;
        chapterBanner.classList.add("show");
        chapterBannerTimer = 150;
    }
    function checkChapterTransition() {
        const idx = getChapterIndex(player.radius);
        if (idx !== currentChapter) {
            currentChapter = idx;
            regenerateKelp(); regenerateReef();
            sound("level");
            showChapterBanner(idx);
        }
    }

    function terminateGameEngine(victory) {
        gameActive = false; gamePaused = false; clearInterval(spawnIntervalId); spawnIntervalId = null; cancelAnimationFrame(animationFrameId); animationFrameId = null;
        pauseOverlay.style.display = "none"; screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX OCEAN GOD 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution completed safely across all 5 chapters! Final Score: ${score}`; actionBtn.innerText = "RESTART EVOLUTION 🔄"; }
        else { sound("boom"); screenShake = 14; overlayTitle.innerText = "GAME OVER"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `All 3 lives are gone in ${CHAPTERS[currentChapter].name}. Final Score: ${score}`; actionBtn.innerText = "START NEW GAME 🔄"; }
    }

    function runGameLoop(timestamp) {
        if (!gameActive || gamePaused) return;
        if (lastTimestamp === null) lastTimestamp = timestamp;
        let dt = (timestamp - lastTimestamp) / (1000 / 60);
        dt = Math.max(0, Math.min(dt, 3));
        lastTimestamp = timestamp;
        timeTick += dt;

        ctx.save();
        if (screenShake > 0) { ctx.translate((Math.random() - 0.5) * screenShake, (Math.random() - 0.5) * screenShake); screenShake *= 0.9; if (screenShake < 0.3) screenShake = 0; }

        const theme = CHAPTERS[currentChapter] || CHAPTERS[0];
        let oceanBackground = ctx.createLinearGradient(0, 0, 0, canvas.height); oceanBackground.addColorStop(0, theme.sky[0]); oceanBackground.addColorStop(0.5, theme.sky[1]); oceanBackground.addColorStop(1, theme.sky[2]); ctx.fillStyle = oceanBackground; ctx.fillRect(0, 0, canvas.width, canvas.height);

        const causticPulse = (0.015 + Math.sin(timeTick * 0.02) * 0.008) * theme.rayStrength;
        const midX = canvas.width / 2;
        drawVolumetricLight(causticPulse);
        void midX;

        drawMegafauna(dt);
        drawSchoolFish(dt);

        drawCoralReef();
        drawLandmark();
        let depthFog = ctx.createLinearGradient(0, canvas.height * 0.55, 0, canvas.height);
        depthFog.addColorStop(0, `rgba(${theme.fog}, 0)`); depthFog.addColorStop(1, `rgba(${theme.fog}, 0.6)`);
        ctx.fillStyle = depthFog; ctx.fillRect(0, canvas.height * 0.55, canvas.width, canvas.height * 0.45);

        kelpFronds.forEach(k => {
            const sway = Math.sin(timeTick * 0.015 + k.phase) * k.sway;
            ctx.strokeStyle = "rgba(4, 50, 40, 0.4)"; ctx.lineWidth = 6; ctx.beginPath();
            ctx.moveTo(k.x, canvas.height); ctx.quadraticCurveTo(k.x + sway, canvas.height - k.height * 0.5, k.x + sway * 1.6, canvas.height - k.height); ctx.stroke();
        });

        drawAnemones();
        drawJellyfish(dt);
        drawPlankton(dt);

        if (chapterBannerTimer > 0) { chapterBannerTimer -= dt; if (chapterBannerTimer <= 0) chapterBanner.classList.remove("show"); }

        if (Math.random() < 0.06 * dt) environmentBubbles.push({ x: Math.random() * canvas.width, y: canvas.height + 20, r: Math.random() * 2.5 + 1, speed: Math.random() * 0.8 + 0.4, drift: (Math.random() - 0.5) * 0.4 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed * dt; b.x += b.drift * dt; ctx.fillStyle = "rgba(140, 200, 220, 0.14)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });

        particles.forEach((p, i) => {
            p.x += p.vx * dt; p.y += p.vy * dt; p.life -= 0.04 * dt;
            if (p.life <= 0) { particles.splice(i, 1); return; }
            ctx.fillStyle = `hsla(${p.hue}, 90%, 65%, ${p.life})`; ctx.beginPath(); ctx.arc(p.x, p.y, 2.5 * p.life, 0, Math.PI * 2); ctx.fill();
        });

        let dx = player.targetX - player.x; let dy = player.targetY - player.y; let dist = Math.hypot(dx, dy);
        const maxSpeed = 2.1 + player.radius * 0.016;
        const desiredSpeed = Math.min(dist * 0.085, maxSpeed);
        const desiredVX = dist > 0.5 ? (dx / dist) * desiredSpeed : 0;
        const desiredVY = dist > 0.5 ? (dy / dist) * desiredSpeed : 0;
        const agilityBase = Math.max(0.035, 0.13 - player.radius * 0.0011);
        const agility = Math.min(1, agilityBase * dt);
        player.vx += (desiredVX - player.vx) * agility; player.vy += (desiredVY - player.vy) * agility;
        player.x += player.vx * dt; player.y += player.vy * dt;
        player.x = Math.max(15, Math.min(player.x, canvas.width - 15)); player.y = Math.max(15, Math.min(player.y, canvas.height - 15));
        if (Math.abs(player.vx) > 0.1) player.facingLeft = player.vx < 0;
        player.tiltAngle += ((player.vy * 0.12) - player.tiltAngle) * Math.min(1, 0.15 * dt);
        player.tailWag += dt;
        const playerSpeedMag = Math.hypot(player.vx, player.vy);
        const playerDepth = 0.85 + (player.y / canvas.height) * 0.3;
        drawRealisticFish(player.x, player.y, player.radius, player.facingLeft, PLAYER_SPECIES, 3, player.tailWag, playerSpeedMag, player.tiltAngle, playerDepth, null);

        for (let index = marineThreats.length - 1; index >= 0; index--) {
            const t = marineThreats[index];
            t.x += t.vx * dt; t.wagPhase += dt;
            const isTargetEdible = t.radius < player.radius;
            const auraColor = isTargetEdible ? "94, 255, 170" : "255, 80, 80";
            const tSpeedMag = Math.abs(t.vx);
            const tDepth = 0.85 + (t.y / canvas.height) * 0.3;
            drawRealisticFish(t.x, t.y, t.radius, t.vx < 0, FISH_SPECIES[t.speciesIdx], t.fishType, t.wagPhase, tSpeedMag, 0, tDepth, auraColor);
            let distance = Math.hypot(player.x - t.x, player.y - t.y);
            if (distance < player.radius + t.radius * 0.75) {
                if (isTargetEdible) {
                    sound("crunch"); score += Math.floor(t.radius * 12);
                    spawnParticles(t.x, t.y, 150, 8);
                    marineThreats.splice(index, 1);
                    player.eatenThisTier++;
                    scoreLabel.innerText = "SCORE: " + String(score).padStart(5, '0');

                    if (player.eatenThisTier >= FISH_PER_TIER) {
                        if (player.tier < TIER_RADII.length - 1) {
                            player.tier++;
                            player.eatenThisTier = 0;
                            player.radius = TIER_RADII[player.tier];
                            spawnParticles(player.x, player.y, 150, 20);
                            sound("level");
                            updateSizeHud();
                        } else {
                            player.eatenThisTier = FISH_PER_TIER;
                            updateSizeHud();
                            showChapterCompleteMenu();
                            ctx.restore();
                            return;
                        }
                    } else {
                        updateSizeHud();
                    }
                } else { ctx.restore(); handlePlayerDeath(); return; }
            }
            if ((t.x > canvas.width + 60 && t.vx > 0) || (t.x < -60 && t.vx < 0)) marineThreats.splice(index, 1);
        }

        ctx.restore();
        animationFrameId = requestAnimationFrame(runGameLoop);
    }
</script>
</body>
</html>
"""

components.html(game_html, height=900, scrolling=False)
st.caption("Tip: for a true full-screen arcade feel, use your browser's fullscreen mode (F11 on PC, or 'Add to Home Screen' on mobile).")
