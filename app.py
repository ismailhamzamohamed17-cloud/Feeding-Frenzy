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
            <div id="sizeLabel">RANK: MINNOW (15)</div>
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

    let score = 0, gameActive = false, gamePaused = false, timeTick = 0, lastTimestamp = null;
    let player = { x: 190, y: 240, vx: 0, vy: 0, radius: 15, targetX: 190, targetY: 240, facingLeft: false, tailWag: 0, tiltAngle: 0 };
    let marineThreats = []; let environmentBubbles = []; let particles = []; let kelpFronds = [];
    let reefRocks = []; let reefCorals = []; let reefAnemones = [];
    // Volumetric god-ray definitions (offset from centre, width, drift speed, base alpha)
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

    // Painterly reef-fish species palettes — banded bodies + eye-mask stripe + bright fin tips, in the
    // spirit of a real angelfish/butterflyfish rather than a single flat cartoon hue. Expanded roster
    // so each chapter/biome can draw from its own believable palette pool instead of reusing everything.
    const FISH_SPECIES = [
        { bands: ["#eaf7ff", "#2f8fd1", "#0d3f6b"], finColor: "#ffcf4d", maskColor: "#0b1a2b" },   // blue tang
        { bands: ["#fff3d6", "#f2b23c", "#7a4c0c"], finColor: "#2f8fd1", maskColor: "#241505" },   // yellow butterflyfish
        { bands: ["#ffe7d9", "#ff8a4d", "#96350c"], finColor: "#ffffff", maskColor: "#160a04" },   // clownfish orange
        { bands: ["#eee9ff", "#8f7bff", "#33246e"], finColor: "#8be7ff", maskColor: "#140a2b" },   // violet damsel
        { bands: ["#e8fff3", "#33c48a", "#0e4a32"], finColor: "#ffe37a", maskColor: "#06231a" },   // parrotfish green
        { bands: ["#f4ffe8", "#9ad14a", "#3d5c14"], finColor: "#ffb84d", maskColor: "#16240a" },   // olive wrasse (kelp)
        { bands: ["#d9f4ff", "#4aa8c9", "#123a4a"], finColor: "#c9f2ff", maskColor: "#04141c" },   // silver-blue baitfish (rocky/open)
        { bands: ["#2a2540", "#4b3a78", "#120f24"], finColor: "#7de8d8", maskColor: "#050414" },   // bioluminescent deep-fish (twilight/abyss)
        { bands: ["#1c1230", "#33205c", "#0a0618"], finColor: "#ff5fb0", maskColor: "#04020a" },   // deep-sea anglerish cousin (abyss)
    ];
    const PLAYER_SPECIES = { bands: ["#eafff5", "#10b981", "#04351f"], finColor: "#facc15", maskColor: "#04120b" };

    /* ---------- 5 chapter maps ----------
       As the player grows, the game descends through 5 distinct biomes: brighter/shallower to
       darker/deeper, each with its own water colour, light strength, coral palette, fish pool and
       background "cast" (schooling fish, jellyfish, cruising megafauna, a landmark silhouette). */
    const CHAPTERS = [
        {
            name: "CORAL SHALLOWS", minRadius: 0,
            sky: ["#0a3a52", "#062338", "#01131f"], fog: "2, 24, 34", rayStrength: 1.15,
            coralAmberBias: 0.5, speciesPool: [0, 1, 2, 3, 4], kelpDensity: 0.4,
            schoolCount: 3, jellyfishCount: 0, megafauna: "turtle", megafaunaChance: 0.55, landmark: "none",
        },
        {
            name: "KELP FOREST", minRadius: 23,
            sky: ["#0a3a2e", "#062a24", "#010f14"], fog: "3, 30, 26", rayStrength: 0.95,
            coralAmberBias: 0.3, speciesPool: [0, 4, 5, 3, 1], kelpDensity: 1.6,
            schoolCount: 5, jellyfishCount: 1, megafauna: "turtle", megafaunaChance: 0.4, landmark: "none",
        },
        {
            name: "ROCKY DROP-OFF", minRadius: 32,
            sky: ["#0c2e4a", "#071b30", "#010a16"], fog: "3, 20, 32", rayStrength: 0.75,
            coralAmberBias: 0.35, speciesPool: [6, 0, 3, 5, 2], kelpDensity: 0.7,
            schoolCount: 6, jellyfishCount: 2, megafauna: "ray", megafaunaChance: 0.5, landmark: "shipwreck",
        },
        {
            name: "TWILIGHT TRENCH", minRadius: 42,
            sky: ["#141034", "#0a0a24", "#030312"], fog: "6, 10, 30", rayStrength: 0.4,
            coralAmberBias: 0.15, speciesPool: [7, 6, 3, 8], kelpDensity: 0.25,
            schoolCount: 4, jellyfishCount: 4, megafauna: "ray", megafaunaChance: 0.35, landmark: "shipwreck",
        },
        {
            name: "ABYSSAL DEEP", minRadius: 52,
            sky: ["#0a0620", "#050312", "#000006"], fog: "10, 4, 24", rayStrength: 0.15,
            coralAmberBias: 0.05, speciesPool: [7, 8], kelpDensity: 0.05,
            schoolCount: 2, jellyfishCount: 6, megafauna: "none", megafaunaChance: 0, landmark: "ruins",
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
    }
    function regenerateKelp() {
        kelpFronds = [];
        const density = CHAPTERS[currentChapter] ? CHAPTERS[currentChapter].kelpDensity : 0.4;
        const count = Math.max(2, Math.round((canvas.width / 140) * density));
        for (let i = 0; i < count; i++) {
            kelpFronds.push({ x: Math.random() * canvas.width, height: 70 + Math.random() * 110, sway: Math.random() * 12, phase: Math.random() * 100 });
        }
    }

    /* ---------- Procedural coral reef: rocks, branching/fan/tube corals, glowing anemones ----------
       Geometry is baked once per resize so the reef never flickers and the per-frame cost is just strokes. */
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
                depth: 0.35 + Math.random() * 0.65,             // 1 = foreground, small = hazier/further
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

    /* ---------- Ambient background life: schooling fish, jellyfish, cruising megafauna, landmarks ----------
       These never collide with the player — they're pure atmosphere that makes each chapter feel alive. */
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
                size: 14 + Math.random() * 20, phase: Math.random() * 100, driftSpeed: 0.08 + Math.random() * 0.1,
                hue: Math.random() < 0.5 ? "180, 240, 255" : "255, 130, 220",
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
            // Classic "feeding frenzy" bite: a short filtered noise burst (the crunch) layered over a low thump (the weight of the bite)
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
        // Snap the follow target to the fish so it doesn't lurch on resume
        player.targetX = player.x; player.targetY = player.y;
        lastTimestamp = null;
        if (!spawnIntervalId) spawnIntervalId = setInterval(generateMarineLife, 650);
        if (!animationFrameId) animationFrameId = requestAnimationFrame(runGameLoop);
    }
    function togglePause() { gamePaused ? resumeGame() : pauseGame(); }

    function exitToTitle() {
        gameActive = false; gamePaused = false;
        if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
        if (spawnIntervalId) { clearInterval(spawnIntervalId); spawnIntervalId = null; }
        pauseOverlay.style.display = "none";
        screenOverlay.style.display = "none";
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
    // Auto-pause if the player tabs away mid-dive
    document.addEventListener("visibilitychange", () => { if (document.hidden) pauseGame(); });
"""
# Part D: True fish-silhouette rendering — tapered body with snout + peduncle, scales, gills, pectoral fin
game_html += r"""
    /* ---------- Volumetric lighting: soft god-rays fading into dark water ---------- */
    function drawVolumetricLight(pulse) {
        const h = canvas.height, w = canvas.width;
        // surface shimmer band
        let surf = ctx.createLinearGradient(0, 0, 0, h * 0.3);
        surf.addColorStop(0, `rgba(150, 231, 233, ${0.14 + pulse * 2})`);
        surf.addColorStop(1, "rgba(6, 40, 60, 0)");
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
            g.addColorStop(0, `rgba(196, 244, 245, ${alpha})`);
            g.addColorStop(0.35, `rgba(94, 214, 199, ${alpha * 0.45})`);
            g.addColorStop(0.72, `rgba(30, 140, 150, ${alpha * 0.16})`);
            g.addColorStop(1, "rgba(10, 60, 80, 0)");
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

        // sediment bed
        let bed = ctx.createLinearGradient(0, h - 120, 0, h);
        bed.addColorStop(0, "rgba(3, 24, 34, 0)"); bed.addColorStop(1, "rgba(4, 30, 38, 0.85)");
        ctx.fillStyle = bed; ctx.fillRect(0, h - 120, w, 120);

        // rock mounds, hazier the further back they sit
        reefRocks.forEach(rk => {
            const fade = 0.3 + rk.depth * 0.45;
            ctx.fillStyle = `rgba(4, ${Math.round(26 + rk.depth * 18)}, ${Math.round(34 + rk.depth * 20)}, ${fade})`;
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

        // corals
        reefCorals.forEach(c => {
            const sway = Math.sin(timeTick * 0.012 + c.phase) * (3 + c.height * 0.03);
            ctx.save();
            ctx.translate(c.x, floorY);
            ctx.globalAlpha = 0.35 + c.depth * 0.5;
            const body = reefTint(c.hue, 0.35 + c.depth * 0.4);

            if (c.kind === "branch") {
                ctx.strokeStyle = body; ctx.lineCap = "round";
                c.segs.forEach(s => {
                    ctx.lineWidth = s.w * (0.6 + c.depth * 0.5);
                    ctx.beginPath();
                    ctx.moveTo(s.x1 + sway * (-s.y1 / c.height) * 0.5, s.y1);
                    ctx.lineTo(s.x2 + sway * (-s.y2 / c.height) * 0.6, s.y2);
                    ctx.stroke();
                });
                // luminous polyp tips
                ctx.fillStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.5)" : "rgba(52, 211, 153, 0.5)";
                c.segs.filter(s => s.tip).forEach(s => {
                    ctx.beginPath(); ctx.arc(s.x2 + sway * (-s.y2 / c.height) * 0.6, s.y2, Math.max(1.2, s.w * 0.7), 0, Math.PI * 2); ctx.fill();
                });
            } else if (c.kind === "fan") {
                // wide, flat sea fan (broader than tall) rather than a balloon shape
                const fh = c.height * 0.8, fw = c.height * 1.15;
                let fg = ctx.createLinearGradient(0, 0, 0, -fh);
                fg.addColorStop(0, body); fg.addColorStop(1, c.hue === "amber" ? "rgba(150, 92, 34, 0.16)" : "rgba(38, 160, 145, 0.16)");
                ctx.fillStyle = fg; ctx.globalAlpha *= 0.7;
                ctx.beginPath(); ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-fw * 0.55 + sway * 0.6, -fh * 0.35, -fw * 0.5 + sway, -fh * 0.92);
                ctx.quadraticCurveTo(0 + sway, -fh * 1.05, fw * 0.5 + sway, -fh * 0.92);
                ctx.quadraticCurveTo(fw * 0.55 + sway * 0.6, -fh * 0.35, 0, 0);
                ctx.closePath(); ctx.fill();
                // fan lattice ribs
                ctx.strokeStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.16)" : "rgba(190, 245, 240, 0.16)"; ctx.lineWidth = 1;
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
                    ctx.fillStyle = c.hue === "amber" ? "rgba(250, 204, 21, 0.28)" : "rgba(52, 211, 153, 0.28)";
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
            const rgb = a.hue === "amber" ? "250, 204, 21" : "52, 211, 153";
            const pulse = 0.55 + Math.sin(timeTick * 0.03 + a.phase) * 0.25;
            ctx.save();
            ctx.translate(a.x, floorY - a.lift);
            ctx.globalCompositeOperation = "lighter";
            let glow = ctx.createRadialGradient(0, 0, 1, 0, 0, a.base * 2.4);
            glow.addColorStop(0, `rgba(${rgb}, ${0.16 * pulse})`); glow.addColorStop(1, `rgba(${rgb}, 0)`);
            ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(0, 0, a.base * 2.4, 0, Math.PI * 2); ctx.fill();

            // soft curling tentacles — short, rounded and splayed outward, not a starburst
            ctx.lineCap = "round";
            for (let i = 0; i < a.tentacles; i++) {
                const spread = (i / (a.tentacles - 1) - 0.5) * Math.PI * 0.9;
                const wave = Math.sin(timeTick * 0.04 + a.phase + i * 0.7) * a.base * 0.22;
                const ex = Math.sin(spread) * a.base * 1.05 + wave;
                const ey = -a.base * (0.35 + Math.cos(spread) * 0.45);
                ctx.strokeStyle = `rgba(${rgb}, ${0.3 * pulse})`; ctx.lineWidth = Math.max(1.6, a.base * 0.14);
                ctx.beginPath(); ctx.moveTo(0, a.lift * 0.35);
                ctx.quadraticCurveTo(ex * 0.45, ey * 1.15, ex, ey);
                ctx.stroke();
                ctx.fillStyle = `rgba(${rgb}, ${0.34 * pulse})`;
                ctx.beginPath(); ctx.arc(ex, ey, Math.max(1.1, a.base * 0.1), 0, Math.PI * 2); ctx.fill();
            }
            ctx.globalCompositeOperation = "source-over";
            ctx.fillStyle = `rgba(4, 30, 38, 0.9)`; ctx.beginPath();
            ctx.ellipse(0, a.lift * 0.5, a.base * 0.55, a.base * 0.4, 0, 0, Math.PI * 2); ctx.fill();
            ctx.restore();
        });
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
                ctx.globalAlpha = 0.55;
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
            let glow = ctx.createRadialGradient(0, 0, 1, 0, 0, j.size * 2.2);
            glow.addColorStop(0, `rgba(${j.hue}, ${0.22 * pulse})`); glow.addColorStop(1, `rgba(${j.hue}, 0)`);
            ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(0, 0, j.size * 2.2, 0, Math.PI * 2); ctx.fill();

            const bellSquash = 1 + Math.sin(j.phase * 2) * 0.18;
            ctx.fillStyle = `rgba(${j.hue}, ${0.45 * pulse})`;
            ctx.beginPath(); ctx.ellipse(0, 0, j.size * 0.7, j.size * 0.55 * bellSquash, 0, Math.PI, 0); ctx.fill();
            ctx.strokeStyle = `rgba(${j.hue}, ${0.3 * pulse})`; ctx.lineWidth = Math.max(1, j.size * 0.05); ctx.lineCap = "round";
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
        ctx.globalAlpha = 0.5;
        if (m.kind === "ray") {
            const flap = Math.sin(m.phase * 4) * m.size * 0.28;
            ctx.fillStyle = "#2b3a4a";
            ctx.beginPath();
            ctx.moveTo(m.size * 1.1, 0);
            ctx.quadraticCurveTo(m.size * 0.3, -m.size * 0.5 + flap, -m.size * 0.9, -m.size * 0.15);
            ctx.quadraticCurveTo(-m.size * 0.4, 0, -m.size * 0.9, m.size * 0.15);
            ctx.quadraticCurveTo(m.size * 0.3, m.size * 0.5 - flap, m.size * 1.1, 0);
            ctx.closePath(); ctx.fill();
            ctx.strokeStyle = "rgba(148,163,184,0.4)"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(-m.size * 0.85, 0); ctx.lineTo(-m.size * 1.6, m.size * 0.35); ctx.stroke();
        } else if (m.kind === "turtle") {
            const paddle = Math.sin(m.phase * 3) * 0.35;
            ctx.fillStyle = "#3a5a3f";
            ctx.beginPath(); ctx.ellipse(0, 0, m.size * 0.62, m.size * 0.46, 0, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "rgba(6,20,10,0.4)"; ctx.lineWidth = 1.4;
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
        ctx.save(); ctx.translate(landmarkDecor.x, floorY); ctx.scale(s, s); ctx.globalAlpha = 0.5;
        ctx.fillStyle = "#0b1520";
        if (landmarkDecor.kind === "shipwreck") {
            ctx.beginPath();
            ctx.moveTo(-140, 0); ctx.lineTo(120, 0); ctx.lineTo(90, -46); ctx.lineTo(-40, -58); ctx.lineTo(-120, -34); ctx.closePath(); ctx.fill();
            ctx.strokeStyle = "rgba(148,163,184,0.25)"; ctx.lineWidth = 2;
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

    function drawAura(r, colorRgb, strong) {
        const outer = strong ? r * 1.5 : r * 1.3;
        const peakAlpha = strong ? 0.4 : 0.22;
        let g = ctx.createRadialGradient(0, 0, r * 0.7, 0, 0, outer);
        g.addColorStop(0, `rgba(${colorRgb}, ${peakAlpha})`); g.addColorStop(1, `rgba(${colorRgb}, 0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 0, outer * 1.12, outer * 0.82, 0, 0, Math.PI * 2); ctx.fill();
    }

    // Real fish outline: pointed snout at +x, full mid-body, tapering down to a narrow tail peduncle at -x.
    function traceFishBody(r) {
        ctx.beginPath();
        ctx.moveTo(r * 1.10, r * 0.06);                                                     // snout tip
        ctx.bezierCurveTo(r * 0.86, -r * 0.44, r * 0.42, -r * 0.92, -r * 0.06, -r * 0.90);  // forehead -> back
        ctx.bezierCurveTo(-r * 0.44, -r * 0.88, -r * 0.72, -r * 0.58, -r * 0.94, -r * 0.20);// back -> peduncle top
        ctx.quadraticCurveTo(-r * 1.00, 0, -r * 0.94, r * 0.20);                            // narrow peduncle
        ctx.bezierCurveTo(-r * 0.70, r * 0.60, -r * 0.38, r * 0.92, r * 0.06, r * 0.94);    // belly rear
        ctx.bezierCurveTo(r * 0.52, r * 0.96, r * 0.90, r * 0.52, r * 1.10, r * 0.06);      // belly -> chin -> snout
        ctx.closePath();
    }

    function drawRealisticFish(x, y, r, isLeft, species, fishType, pulseTick, speedMag, tiltAngle, depthScale, auraColorRgb) {
        ctx.save(); ctx.translate(x, y); ctx.scale(depthScale, depthScale); if (isLeft) ctx.scale(-1, 1);
        ctx.rotate(Math.max(-0.3, Math.min(0.3, tiltAngle)) * (isLeft ? -1 : 1));

        if (auraColorRgb) drawAura(r, auraColorRgb, auraColorRgb === "239, 68, 68");

        const wagSpeed = 0.1 + Math.min(0.28, speedMag * 0.2);
        const wag = Math.sin(pulseTick * wagSpeed) * (r * (0.2 + Math.min(0.15, speedMag * 0.1)));
        const tailWag = Math.sin(pulseTick * wagSpeed + 0.6) * (r * 0.34);
        // body depth by species build: 1 = deep/disc, 2 = slender torpedo, 3 = balanced
        const bodyYScale = fishType === 1 ? 1.02 : (fishType === 2 ? 0.60 : 0.80);

        // contact shadow (depth cue)
        ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = "#000814"; ctx.beginPath(); ctx.ellipse(r * 0.05, r * (0.95 * bodyYScale + 0.35), r * 0.95, r * 0.22, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        // ---- caudal (tail) fin: forked, swept, translucent membrane with ray lines ----
        const tx = -r * 0.92; // peduncle attach point
        let tailGrd = ctx.createLinearGradient(tx, 0, -r * 2.2, 0);
        tailGrd.addColorStop(0, species.bands[2]); tailGrd.addColorStop(0.55, species.bands[1]); tailGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = tailGrd; ctx.globalAlpha = 0.9;
        ctx.beginPath();
        if (fishType === 2) { // deep fork (fast swimmer)
            ctx.moveTo(tx, -r * 0.12 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.5, -r * 0.95 + tailWag, -r * 2.15, -r * 1.05 + tailWag);
            ctx.quadraticCurveTo(-r * 1.42, -r * 0.16 + tailWag * 0.7, -r * 1.30, tailWag * 0.6);
            ctx.quadraticCurveTo(-r * 1.42, r * 0.16 + tailWag * 0.7, -r * 2.15, r * 1.05 + tailWag);
            ctx.quadraticCurveTo(-r * 1.5, r * 0.95 + tailWag, tx, r * 0.12 * bodyYScale);
        } else { // fan / rounded caudal
            ctx.moveTo(tx, -r * 0.14 * bodyYScale);
            ctx.quadraticCurveTo(-r * 1.45, -r * 0.78 + tailWag, -r * 1.95, -r * 0.72 + tailWag);
            ctx.quadraticCurveTo(-r * 1.55, tailWag * 0.9, -r * 1.95, r * 0.72 + tailWag);
            ctx.quadraticCurveTo(-r * 1.45, r * 0.78 + tailWag, tx, r * 0.14 * bodyYScale);
        }
        ctx.closePath(); ctx.fill();
        // fin rays
        ctx.strokeStyle = "rgba(255,255,255,0.28)"; ctx.lineWidth = Math.max(0.6, r * 0.035); ctx.globalAlpha = 0.55;
        for (let i = -2; i <= 2; i++) {
            ctx.beginPath(); ctx.moveTo(tx, 0);
            ctx.quadraticCurveTo(-r * 1.4, i * r * 0.3 + tailWag * 0.8, -r * 1.9, i * r * 0.38 + tailWag);
            ctx.stroke();
        }
        ctx.globalAlpha = 1;

        // ---- dorsal fin: spiny ridge along the back with a soft trailing edge ----
        let dorsalGrd = ctx.createLinearGradient(0, -r * bodyYScale * 0.85, 0, -r * bodyYScale * 1.75);
        dorsalGrd.addColorStop(0, species.bands[1]); dorsalGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = dorsalGrd; ctx.globalAlpha = 0.94;
        ctx.beginPath();
        ctx.moveTo(-r * 0.72, -r * 0.55 * bodyYScale);
        ctx.quadraticCurveTo(-r * 0.30, -r * (1.45 * bodyYScale) + wag * 0.3, r * 0.16, -r * (1.22 * bodyYScale));
        ctx.quadraticCurveTo(r * 0.34, -r * (0.98 * bodyYScale), r * 0.42, -r * (0.72 * bodyYScale));
        ctx.quadraticCurveTo(-r * 0.10, -r * (0.86 * bodyYScale), -r * 0.72, -r * 0.55 * bodyYScale);
        ctx.closePath(); ctx.fill();
        ctx.globalAlpha = 1;

        // ---- anal fin (underside, rear) ----
        ctx.fillStyle = species.finColor; ctx.globalAlpha = 0.8;
        ctx.beginPath();
        ctx.moveTo(-r * 0.62, r * 0.52 * bodyYScale);
        ctx.quadraticCurveTo(-r * 0.42, r * (1.18 * bodyYScale) + wag * 0.35, -r * 0.02, r * (1.02 * bodyYScale));
        ctx.quadraticCurveTo(-r * 0.28, r * (0.80 * bodyYScale), -r * 0.62, r * 0.52 * bodyYScale);
        ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;

        // ---- body: clip to the fish silhouette, then paint bands, scales and volume shading ----
        ctx.save();
        ctx.scale(1, bodyYScale);
        ctx.save();
        traceFishBody(r); ctx.clip();

        ctx.fillStyle = species.bands[0]; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.fillStyle = species.bands[1];
        ctx.beginPath(); ctx.moveTo(-r * 0.18, -r * 1.3); ctx.lineTo(r * 0.22, -r * 1.3); ctx.lineTo(-r * 0.08, r * 1.3); ctx.lineTo(-r * 0.48, r * 1.3); ctx.closePath(); ctx.fill();
        ctx.fillStyle = species.bands[2];
        ctx.beginPath(); ctx.moveTo(r * 0.30, -r * 1.3); ctx.lineTo(r * 0.64, -r * 1.3); ctx.lineTo(r * 0.38, r * 1.3); ctx.lineTo(r * 0.04, r * 1.3); ctx.closePath(); ctx.fill();
        // tail-end darkening toward the peduncle
        let pedGrd = ctx.createLinearGradient(-r * 0.45, 0, -r * 1.0, 0);
        pedGrd.addColorStop(0, "rgba(0,0,0,0)"); pedGrd.addColorStop(1, "rgba(2,6,14,0.45)");
        ctx.fillStyle = pedGrd; ctx.fillRect(-r * 1.3, -r * 1.3, r * 1.3, r * 2.6);

        // scale rows — embossed overlapping arcs (dark crease + light catch) for a real scaled texture
        const scaleStep = Math.max(3.2, r * 0.24);
        ctx.lineWidth = Math.max(0.5, r * 0.028);
        for (let pass = 0; pass < 2; pass++) {
            ctx.strokeStyle = pass === 0 ? "rgba(2,8,18,0.22)" : "rgba(255,255,255,0.22)";
            const shift = pass === 0 ? scaleStep * 0.12 : 0;
            for (let sy = -r * 0.9; sy < r * 0.9; sy += scaleStep) {
                for (let sx = -r * 0.9; sx < r * 1.0; sx += scaleStep) {
                    const off = (Math.round((sy + r) / scaleStep) % 2) * scaleStep * 0.5;
                    ctx.beginPath(); ctx.arc(sx + off, sy + shift, scaleStep * 0.52, Math.PI * 0.15, Math.PI * 0.85); ctx.stroke();
                }
            }
        }
        // lateral line
        ctx.strokeStyle = "rgba(0,0,0,0.20)"; ctx.lineWidth = Math.max(0.6, r * 0.04);
        ctx.beginPath(); ctx.moveTo(r * 0.72, -r * 0.06); ctx.quadraticCurveTo(0, r * 0.10, -r * 0.88, r * 0.02); ctx.stroke();

        // eye-mask stripe — the dark diagonal band real reef fish wear through the eye
        ctx.save(); ctx.globalAlpha = 0.85; ctx.fillStyle = species.maskColor;
        ctx.beginPath(); ctx.moveTo(r * 0.62, -r * 1.3); ctx.lineTo(r * 0.82, -r * 1.3); ctx.lineTo(r * 0.50, r * 1.3); ctx.lineTo(r * 0.30, r * 1.3); ctx.closePath(); ctx.fill(); ctx.restore();

        // gill plate (operculum) crease
        ctx.strokeStyle = "rgba(2,10,20,0.35)"; ctx.lineWidth = Math.max(0.8, r * 0.055);
        ctx.beginPath(); ctx.moveTo(r * 0.30, -r * 0.66); ctx.quadraticCurveTo(r * 0.10, 0, r * 0.34, r * 0.62); ctx.stroke();

        // volume shading: rim light on the back, ambient occlusion on the belly
        let shadeGrd = ctx.createRadialGradient(r * 0.25, -r * 0.42, r * 0.08, 0, 0, r * 1.25);
        shadeGrd.addColorStop(0, "rgba(255,255,255,0.85)"); shadeGrd.addColorStop(0.45, "rgba(255,255,255,0.16)"); shadeGrd.addColorStop(1, "rgba(8,12,24,0.6)");
        ctx.globalCompositeOperation = "multiply"; ctx.fillStyle = shadeGrd; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.globalCompositeOperation = "source-over";
        // pale countershaded belly (real fish are light underneath)
        let bellyGrd = ctx.createLinearGradient(0, r * 0.2, 0, r * 1.0);
        bellyGrd.addColorStop(0, "rgba(255,255,255,0)"); bellyGrd.addColorStop(1, "rgba(255,255,255,0.34)");
        ctx.fillStyle = bellyGrd; ctx.fillRect(-r * 1.3, 0, r * 2.7, r * 1.3);

        // ---- premium 3D pass: layered radial sheens + specular hotspots ----
        ctx.globalCompositeOperation = "screen";
        // broad wet sheen wrapping the upper flank
        let sheen = ctx.createRadialGradient(r * 0.34, -r * 0.5, r * 0.04, r * 0.05, -r * 0.05, r * 1.3);
        sheen.addColorStop(0, "rgba(226, 250, 255, 0.5)");
        sheen.addColorStop(0.34, "rgba(140, 210, 235, 0.18)");
        sheen.addColorStop(1, "rgba(120, 190, 220, 0)");
        ctx.fillStyle = sheen; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        // secondary iridescent bounce light from the water below
        let bounce = ctx.createRadialGradient(-r * 0.25, r * 0.6, r * 0.03, -r * 0.2, r * 0.55, r * 1.0);
        bounce.addColorStop(0, "rgba(94, 234, 212, 0.28)");
        bounce.addColorStop(1, "rgba(94, 234, 212, 0)");
        ctx.fillStyle = bounce; ctx.fillRect(-r * 1.3, -r * 1.3, r * 2.7, r * 2.6);
        ctx.globalCompositeOperation = "source-over";

        // tight specular hotspot (the glossy 3D "kick") plus a smaller snout highlight
        let spec = ctx.createRadialGradient(r * 0.4, -r * 0.44, 0, r * 0.4, -r * 0.44, r * 0.52);
        spec.addColorStop(0, "rgba(255,255,255,0.9)"); spec.addColorStop(0.45, "rgba(255,255,255,0.22)"); spec.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = spec; ctx.beginPath(); ctx.ellipse(r * 0.4, -r * 0.42, r * 0.5, r * 0.26, -0.35, 0, Math.PI * 2); ctx.fill();
        let spec2 = ctx.createRadialGradient(r * 0.86, -r * 0.1, 0, r * 0.86, -r * 0.1, r * 0.26);
        spec2.addColorStop(0, "rgba(255,255,255,0.6)"); spec2.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = spec2; ctx.beginPath(); ctx.ellipse(r * 0.86, -r * 0.1, r * 0.24, r * 0.16, 0, 0, Math.PI * 2); ctx.fill();

        // wet scale sparkle — a couple of tiny twinkling glints that drift across the flank as it swims
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

        ctx.restore(); // drop clip

        // silhouette edge: dark outline + top rim highlight so the shape reads clearly underwater
        traceFishBody(r);
        ctx.strokeStyle = "rgba(1,6,14,0.55)"; ctx.lineWidth = Math.max(1, r * 0.06); ctx.stroke();
        ctx.save(); ctx.clip();
        ctx.strokeStyle = "rgba(255,255,255,0.45)"; ctx.lineWidth = Math.max(1, r * 0.10);
        ctx.beginPath(); ctx.moveTo(r * 0.92, -r * 0.30); ctx.bezierCurveTo(r * 0.45, -r * 0.92, -r * 0.10, -r * 0.95, -r * 0.60, -r * 0.62); ctx.stroke();
        ctx.restore();

        // pectoral fin — sits on the flank, above the body edge, semi-transparent
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

        // mouth line at the snout
        ctx.strokeStyle = "rgba(2,8,16,0.6)"; ctx.lineWidth = Math.max(0.8, r * 0.05);
        ctx.beginPath(); ctx.moveTo(r * 1.06, r * 0.10); ctx.quadraticCurveTo(r * 0.90, r * 0.20, r * 0.78, r * 0.16); ctx.stroke();

        ctx.restore(); // undo bodyYScale

        // eye — drawn after the y-scale is undone so it stays perfectly round
        let eyeX = r * 0.66; let eyeY = -r * 0.28 * bodyYScale; let eyeRadius = Math.max(2.5, r * 0.17);
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius * 1.18, 0, Math.PI * 2); ctx.fill();
        let eyeGrd = ctx.createRadialGradient(eyeX - eyeRadius * 0.2, eyeY - eyeRadius * 0.2, 1, eyeX, eyeY, eyeRadius);
        eyeGrd.addColorStop(0, "#fdfdff"); eyeGrd.addColorStop(1, "#b9c6d4");
        ctx.fillStyle = eyeGrd; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#020617"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.12, eyeY, eyeRadius * 0.52, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.34, eyeY - eyeRadius * 0.24, eyeRadius * 0.17, 0, Math.PI * 2); ctx.fill();

        ctx.restore();
    }

    function spawnParticles(x, y, hue, count) {
        for (let i = 0; i < count; i++) particles.push({ x, y, vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3, life: 1, hue });
    }
"""
# Part E: Faster, frame-rate-independent physics; capped/targeted spawning (max 8 fish, ~3 edible + ~3 not); game loop
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; gamePaused = false; player.radius = 15;
        player.x = canvas.width / 2; player.y = canvas.height / 2; player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; environmentBubbles = []; particles = []; screenShake = 0; lastTimestamp = null;
        currentChapter = 0; regenerateKelp(); regenerateReef();
        screenOverlay.style.display = "none"; pauseOverlay.style.display = "none"; titleScreen.style.display = "none"; hud.style.display = "flex";
        chapterLabel.style.display = "block";
        scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "RANK: MINNOW (15)";
        showChapterBanner(0);
        if (spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 650);
        if (animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }

    // Keeps roughly 3 edible + 3 not-yet-edible fish on screen at once, hard-capped at 8 total —
    // spawns one at a time so the screen never gets flooded in a single burst.
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
        const sizeRadius = makeEdible ? Math.max(6, player.radius - (Math.random() * 12 + 5)) : player.radius + (Math.random() * 16 + 6);
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
        else { sound("boom"); screenShake = 14; overlayTitle.innerText = "🐋 CONSUMED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You became organic mass in ${CHAPTERS[currentChapter].name}. Final Score: ${score}`; actionBtn.innerText = "REDEPLOY DESCENT 🔄"; }
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
        // Volumetric god-rays replace the old hard caustic wedges (same centre-line drift variables)
        drawVolumetricLight(causticPulse);
        void midX;

        // Distant background cast (megafauna + far schools) drawn before the reef so foreground reads on top
        drawMegafauna(dt);
        drawSchoolFish(dt);

        // Reef silhouettes sit behind the kelp; depth fog pushes them back into the dark water
        drawCoralReef();
        drawLandmark();
        let depthFog = ctx.createLinearGradient(0, canvas.height * 0.55, 0, canvas.height);
        depthFog.addColorStop(0, `rgba(${theme.fog}, 0)`); depthFog.addColorStop(1, `rgba(${theme.fog}, 0.55)`);
        ctx.fillStyle = depthFog; ctx.fillRect(0, canvas.height * 0.55, canvas.width, canvas.height * 0.45);

        kelpFronds.forEach(k => {
            const sway = Math.sin(timeTick * 0.015 + k.phase) * k.sway;
            ctx.strokeStyle = "rgba(6, 78, 59, 0.35)"; ctx.lineWidth = 6; ctx.beginPath();
            ctx.moveTo(k.x, canvas.height); ctx.quadraticCurveTo(k.x + sway, canvas.height - k.height * 0.5, k.x + sway * 1.6, canvas.height - k.height); ctx.stroke();
        });

        drawAnemones();
        drawJellyfish(dt);

        if (chapterBannerTimer > 0) { chapterBannerTimer -= dt; if (chapterBannerTimer <= 0) chapterBanner.classList.remove("show"); }

        if (Math.random() < 0.06 * dt) environmentBubbles.push({ x: Math.random() * canvas.width, y: canvas.height + 20, r: Math.random() * 2.5 + 1, speed: Math.random() * 0.8 + 0.4, drift: (Math.random() - 0.5) * 0.4 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed * dt; b.x += b.drift * dt; ctx.fillStyle = "rgba(52, 211, 153, 0.12)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });

        particles.forEach((p, i) => {
            p.x += p.vx * dt; p.y += p.vy * dt; p.life -= 0.04 * dt;
            if (p.life <= 0) { particles.splice(i, 1); return; }
            ctx.fillStyle = `hsla(${p.hue}, 90%, 65%, ${p.life})`; ctx.beginPath(); ctx.arc(p.x, p.y, 2.5 * p.life, 0, Math.PI * 2); ctx.fill();
        });

        // Player physics — same momentum feel, tuned to a normal/quicker pace
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
            const auraColor = isTargetEdible ? "74, 222, 128" : "239, 68, 68";
            const tSpeedMag = Math.abs(t.vx);
            const tDepth = 0.85 + (t.y / canvas.height) * 0.3;
            drawRealisticFish(t.x, t.y, t.radius, t.vx < 0, FISH_SPECIES[t.speciesIdx], t.fishType, t.wagPhase, tSpeedMag, 0, tDepth, auraColor);
            let distance = Math.hypot(player.x - t.x, player.y - t.y);
            if (distance < player.radius + t.radius * 0.75) {
                if (isTargetEdible) {
                    sound("crunch"); score += Math.floor(t.radius * 12); player.radius += t.radius * 0.11;
                    spawnParticles(t.x, t.y, 150, 8);
                    marineThreats.splice(index, 1);
                    scoreLabel.innerText = "SCORE: " + String(score).padStart(5, '0');
                    sizeLabel.innerText = `RANK: ${getRankName(player.radius)} (${Math.floor(player.radius)})`;
                    checkChapterTransition();
                    if (player.radius >= WIN_RADIUS) terminateGameEngine(true);
                } else { terminateGameEngine(false); }
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
