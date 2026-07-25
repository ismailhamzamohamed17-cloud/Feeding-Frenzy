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

# Part A: Full-screen deep-sea canvas layout
game_html = r"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        html, body { margin: 0; padding: 0; height: 100%; width: 100%; background: #01040a; font-family: monospace; user-select: none; -webkit-user-select: none; overflow: hidden; }
        #gameContainer { position: relative; width: 100vw; height: 100vh; height: 100dvh; margin: 0; overflow: hidden; touch-action: none; }
        canvas { display: block; background: #020b18; width: 100%; height: 100%; }
        #hud { position: absolute; top: max(14px, env(safe-area-inset-top)); left: 18px; right: 18px; display: flex; justify-content: space-between; color: #34d399; font-size: 16px; font-weight: bold; pointer-events: none; z-index: 10; text-shadow: 0 0 8px #047857; letter-spacing: 1px; }

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
        .arcade-btn { margin-top: 20px; padding: 14px 30px; background: #10b981; color: #01040a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); font-family: monospace; font-size: 14px; letter-spacing: 1px; transition: transform 0.1s; }
        .arcade-btn:active { transform: scale(0.95); }
    </style>
</head>
"""
# Part B: Loading screen, title/tap-to-play screen, and the game-over overlay
game_html += r"""
<body>
    <div id="gameContainer">
        <div id="hud" style="display:none;">
            <div id="scoreLabel">SCORE: 00000</div>
            <div id="sizeLabel">RANK: MINNOW (15)</div>
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

        <div id="screenOverlay">
            <h2 id="overlayTitle" style="color: #10b981; letter-spacing: 3px; font-size: 26px; margin: 0;">GAME OVER</h2>
            <p id="overlaySub" style="color: #64748b; font-size: 12px; max-width: 320px; line-height: 1.6; margin-top: 10px;"></p>
            <button class="arcade-btn" id="actionBtn" onclick="initiateArcadeGame()">REDEPLOY DESCENT 🔄</button>
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

    let score = 0, gameActive = false, timeTick = 0, lastTimestamp = null;
    let player = { x: 190, y: 240, vx: 0, vy: 0, radius: 15, targetX: 190, targetY: 240, facingLeft: false, tailWag: 0, tiltAngle: 0 };
    let marineThreats = []; let environmentBubbles = []; let particles = []; let kelpFronds = [];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;
    let screenShake = 0;
    const MAX_FISH_ON_SCREEN = 8;
    const TARGET_PER_SIDE = 3;

    // Painterly reef-fish species palettes — banded bodies + eye-mask stripe + bright fin tips, in the
    // spirit of a real angelfish/butterflyfish rather than a single flat cartoon hue.
    const FISH_SPECIES = [
        { bands: ["#eaf7ff", "#2f8fd1", "#0d3f6b"], finColor: "#ffcf4d", maskColor: "#0b1a2b" },
        { bands: ["#fff3d6", "#f2b23c", "#7a4c0c"], finColor: "#2f8fd1", maskColor: "#241505" },
        { bands: ["#ffe7d9", "#ff8a4d", "#96350c"], finColor: "#ffffff", maskColor: "#160a04" },
        { bands: ["#eee9ff", "#8f7bff", "#33246e"], finColor: "#8be7ff", maskColor: "#140a2b" },
        { bands: ["#e8fff3", "#33c48a", "#0e4a32"], finColor: "#ffe37a", maskColor: "#06231a" },
    ];
    const PLAYER_SPECIES = { bands: ["#eafff5", "#10b981", "#04351f"], finColor: "#facc15", maskColor: "#04120b" };

    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width; canvas.height = rect.height;
        player.x = Math.min(player.x, canvas.width - 15); player.y = Math.min(player.y, canvas.height - 15);
        player.targetX = player.x; player.targetY = player.y;
        regenerateKelp();
    }
    function regenerateKelp() {
        kelpFronds = [];
        const count = Math.max(4, Math.floor(canvas.width / 140));
        for (let i = 0; i < count; i++) {
            kelpFronds.push({ x: Math.random() * canvas.width, height: 70 + Math.random() * 110, sway: Math.random() * 12, phase: Math.random() * 100 });
        }
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
    }

    function updateInputCoordinates(clientX, clientY) {
        if (!gameActive) return; const rect = container.getBoundingClientRect();
        player.targetX = Math.max(15, Math.min(clientX - rect.left, rect.width - 15));
        player.targetY = Math.max(15, Math.min(clientY - rect.top, rect.height - 15));
    }
    container.addEventListener("mousemove", (e) => updateInputCoordinates(e.clientX, e.clientY));
    container.addEventListener("touchstart", (e) => { if (gameActive && e.touches && e.touches.length > 0) { updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: true });
    container.addEventListener("touchmove", (e) => { if (gameActive) { e.preventDefault(); if (e.touches && e.touches.length > 0) updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: false });
"""
# Part C: Loading sequence + tap-to-play title screen (replaces the old Streamlit page header entirely)
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
"""
# Part D: Painterly reef-fish rendering — banded body, eye-mask stripe, flowing fins, and a soft red/green edibility aura
game_html += r"""
    function drawAura(r, colorRgb, strong) {
        const outer = strong ? r * 1.32 : r * 1.15;
        const peakAlpha = strong ? 0.4 : 0.22;
        let g = ctx.createRadialGradient(0, 0, r * 0.65, 0, 0, outer);
        g.addColorStop(0, `rgba(${colorRgb}, ${peakAlpha})`); g.addColorStop(1, `rgba(${colorRgb}, 0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, outer, 0, Math.PI * 2); ctx.fill();
    }

    function drawRealisticFish(x, y, r, isLeft, species, fishType, pulseTick, speedMag, tiltAngle, depthScale, auraColorRgb) {
        ctx.save(); ctx.translate(x, y); ctx.scale(depthScale, depthScale); if (isLeft) ctx.scale(-1, 1);
        ctx.rotate(Math.max(-0.3, Math.min(0.3, tiltAngle)) * (isLeft ? -1 : 1));

        if (auraColorRgb) drawAura(r, auraColorRgb, auraColorRgb === "239, 68, 68");

        const wagSpeed = 0.1 + Math.min(0.28, speedMag * 0.2);
        const wag = Math.sin(pulseTick * wagSpeed) * (r * (0.2 + Math.min(0.15, speedMag * 0.1)));
        const tailWag = Math.sin(pulseTick * wagSpeed + 0.6) * (r * 0.32);

        // contact shadow (depth cue)
        ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = "#000814"; ctx.beginPath(); ctx.ellipse(r * 0.1, r * 1.3, r * 0.9, r * 0.26, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        // flowing caudal (tail) fin — body color fading into the bright fin-tip color, like the reference art
        let tailGrd = ctx.createLinearGradient(-r * 0.8, 0, -r * 2.3, 0);
        tailGrd.addColorStop(0, species.bands[2]); tailGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = tailGrd; ctx.globalAlpha = 0.92;
        ctx.beginPath();
        if (fishType === 2) {
            ctx.moveTo(-r * 0.8, 0); ctx.quadraticCurveTo(-r * 1.6, -r * 0.9 + tailWag, -r * 2.3, -r * 1.0 + tailWag); ctx.lineTo(-r * 1.6, tailWag); ctx.lineTo(-r * 2.3, r * 1.0 + tailWag); ctx.quadraticCurveTo(-r * 1.6, r * 0.9 + tailWag, -r * 0.8, 0);
        } else {
            ctx.moveTo(-r * 0.7, 0); ctx.lineTo(-r * 2.1, -r * 0.75 + tailWag); ctx.lineTo(-r * 1.5, tailWag); ctx.lineTo(-r * 2.1, r * 0.75 + tailWag);
        }
        ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;

        // flowing dorsal fin — long, trailing, bright tip
        let finGrd = ctx.createLinearGradient(0, -r * 0.8, 0, -r * 1.6);
        finGrd.addColorStop(0, species.bands[1]); finGrd.addColorStop(1, species.finColor);
        ctx.fillStyle = finGrd;
        ctx.beginPath(); ctx.moveTo(-r * 0.25, -r * 0.85); ctx.quadraticCurveTo(r * 0.05, -r * 1.7 + wag * 0.35, r * 0.55, -r * 0.75); ctx.quadraticCurveTo(r * 0.1, -r * 0.7, -r * 0.25, -r * 0.85); ctx.fill();

        // anal / pectoral fin, same bright-tip treatment
        ctx.beginPath(); ctx.moveTo(-r * 0.1, r * 0.3); ctx.quadraticCurveTo(r * 0.1, r * 1.0 + wag * 0.4, r * 0.4, r * 0.8 + wag * 0.4); ctx.quadraticCurveTo(r * 0.15, r * 0.5, -r * 0.1, r * 0.3); ctx.fill();

        // body: clip to the silhouette, paint diagonal color bands, then a soft multiply shading pass for roundness
        let bodyYScale = fishType === 1 ? 1.0 : (fishType === 2 ? 0.65 : 0.8);
        ctx.save();
        ctx.scale(1, bodyYScale);
        ctx.save();
        ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.clip();
        ctx.fillStyle = species.bands[0]; ctx.fillRect(-r * 1.2, -r * 1.2, r * 2.4, r * 2.4);
        ctx.fillStyle = species.bands[1];
        ctx.beginPath(); ctx.moveTo(-r * 0.15, -r * 1.2); ctx.lineTo(r * 0.25, -r * 1.2); ctx.lineTo(-r * 0.05, r * 1.2); ctx.lineTo(-r * 0.45, r * 1.2); ctx.closePath(); ctx.fill();
        ctx.fillStyle = species.bands[2];
        ctx.beginPath(); ctx.moveTo(r * 0.32, -r * 1.2); ctx.lineTo(r * 0.68, -r * 1.2); ctx.lineTo(r * 0.42, r * 1.2); ctx.lineTo(r * 0.06, r * 1.2); ctx.closePath(); ctx.fill();
        let shadeGrd = ctx.createRadialGradient(r * 0.2, -r * 0.35, r * 0.1, 0, 0, r * 1.15);
        shadeGrd.addColorStop(0, "rgba(255,255,255,0.85)"); shadeGrd.addColorStop(0.5, "rgba(255,255,255,0.15)"); shadeGrd.addColorStop(1, "rgba(10,10,20,0.55)");
        ctx.globalCompositeOperation = "multiply"; ctx.fillStyle = shadeGrd; ctx.fillRect(-r * 1.2, -r * 1.2, r * 2.4, r * 2.4); ctx.globalCompositeOperation = "source-over";
        ctx.restore(); // drop clip only

        // underside ambient occlusion + top rim light for volume
        ctx.save(); ctx.globalAlpha = 0.22; ctx.fillStyle = "#000308"; ctx.beginPath(); ctx.ellipse(0, r * 0.55, r * 0.75, r * 0.4, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
        ctx.strokeStyle = "rgba(255,255,255,0.5)"; ctx.lineWidth = Math.max(1, r * 0.07); ctx.beginPath(); ctx.arc(0, 0, r * 0.97, Math.PI * 1.1, Math.PI * 1.75); ctx.stroke();

        // eye-mask stripe — the dark diagonal band real reef fish (angelfish/butterflyfish) wear through the eye
        ctx.save(); ctx.globalAlpha = 0.88; ctx.fillStyle = species.maskColor;
        ctx.beginPath(); ctx.moveTo(r * 0.28, -r * 1.2); ctx.lineTo(r * 0.5, -r * 1.2); ctx.lineTo(r * 0.14, r * 1.2); ctx.lineTo(-r * 0.08, r * 1.2); ctx.closePath(); ctx.fill(); ctx.restore();

        // gloss highlight
        ctx.save(); ctx.globalAlpha = 0.6; ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.ellipse(r * 0.12, -r * 0.4, r * 0.3, r * 0.15, -0.4, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        ctx.restore(); // undo bodyYScale

        // eye — drawn after the y-scale is undone so it stays perfectly round
        let eyeX = r * 0.52; let eyeY = -r * 0.25 * bodyYScale; let eyeRadius = Math.max(3, r * 0.2);
        let eyeGrd = ctx.createRadialGradient(eyeX - eyeRadius * 0.2, eyeY - eyeRadius * 0.2, 1, eyeX, eyeY, eyeRadius);
        eyeGrd.addColorStop(0, "#ffffff"); eyeGrd.addColorStop(1, "#cbd5e1");
        ctx.fillStyle = eyeGrd; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#020617"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.15, eyeY, eyeRadius * 0.5, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius * 0.32, eyeY - eyeRadius * 0.2, eyeRadius * 0.15, 0, Math.PI * 2); ctx.fill();

        ctx.restore();
    }

    function spawnParticles(x, y, hue, count) {
        for (let i = 0; i < count; i++) particles.push({ x, y, vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3, life: 1, hue });
    }
"""
# Part E: Faster, frame-rate-independent physics; capped/targeted spawning (max 8 fish, ~3 edible + ~3 not); game loop
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; player.radius = 15;
        player.x = canvas.width / 2; player.y = canvas.height / 2; player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; environmentBubbles = []; particles = []; screenShake = 0; lastTimestamp = null;
        screenOverlay.style.display = "none"; hud.style.display = "flex";
        scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "RANK: MINNOW (15)";
        if (spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 650);
        if (animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }

    // Keeps roughly 3 edible + 3 not-yet-edible fish on screen at once, hard-capped at 8 total —
    // spawns one at a time so the screen never gets flooded in a single burst.
    function generateMarineLife() {
        if (!gameActive) return;
        if (marineThreats.length >= MAX_FISH_ON_SCREEN) return;
        let edibleCount = 0, inedibleCount = 0;
        marineThreats.forEach(t => { if (t.radius < player.radius) edibleCount++; else inedibleCount++; });
        const needEdible = edibleCount < TARGET_PER_SIDE; const needInedible = inedibleCount < TARGET_PER_SIDE;
        if (!needEdible && !needInedible) return;
        const makeEdible = needEdible && (!needInedible || Math.random() < 0.5);

        const spawnFromLeft = Math.random() > 0.5;
        const speciesIdx = Math.floor(Math.random() * FISH_SPECIES.length);
        const specificType = Math.floor(Math.random() * 3) + 1;
        const sizeRadius = makeEdible ? Math.max(6, player.radius - (Math.random() * 12 + 5)) : player.radius + (Math.random() * 16 + 6);
        const baseY = Math.random() * (canvas.height - 90) + 45;
        const baseSpeed = (Math.random() * 0.55 + 0.5) * (spawnFromLeft ? 1 : -1);
        marineThreats.push({ x: spawnFromLeft ? -60 : canvas.width + 60, y: baseY, radius: sizeRadius, vx: baseSpeed, vy: 0, fishType: specificType, speciesIdx, wagPhase: Math.random() * 100 });
    }

    function getRankName(r) { if (r < 25) return "MINNOW"; if (r < 40) return "BASS"; if (r < 55) return "TUNA"; return "APEX SHARK"; }

    function terminateGameEngine(victory) {
        gameActive = false; clearInterval(spawnIntervalId); cancelAnimationFrame(animationFrameId); screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX OCEAN GOD 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution completed safely! Final Score: ${score}`; actionBtn.innerText = "RESTART EVOLUTION 🔄"; }
        else { sound("boom"); screenShake = 14; overlayTitle.innerText = "🐋 CONSUMED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You became organic mass. Final Score: ${score}`; actionBtn.innerText = "REDEPLOY DESCENT 🔄"; }
    }

    function runGameLoop(timestamp) {
        if (!gameActive) return;
        if (lastTimestamp === null) lastTimestamp = timestamp;
        let dt = (timestamp - lastTimestamp) / (1000 / 60);
        dt = Math.max(0, Math.min(dt, 3));
        lastTimestamp = timestamp;
        timeTick += dt;

        ctx.save();
        if (screenShake > 0) { ctx.translate((Math.random() - 0.5) * screenShake, (Math.random() - 0.5) * screenShake); screenShake *= 0.9; if (screenShake < 0.3) screenShake = 0; }

        let oceanBackground = ctx.createLinearGradient(0, 0, 0, canvas.height); oceanBackground.addColorStop(0, "#041628"); oceanBackground.addColorStop(0.5, "#020f1c"); oceanBackground.addColorStop(1, "#01050d"); ctx.fillStyle = oceanBackground; ctx.fillRect(0, 0, canvas.width, canvas.height);

        const causticPulse = 0.015 + Math.sin(timeTick * 0.02) * 0.008;
        const midX = canvas.width / 2;
        ctx.fillStyle = `rgba(16, 185, 129, ${causticPulse})`; ctx.beginPath(); ctx.moveTo(midX - 130, 0); ctx.lineTo(midX, canvas.height); ctx.lineTo(midX - 80, canvas.height); ctx.lineTo(midX - 170, 0); ctx.closePath(); ctx.fill();
        ctx.beginPath(); ctx.moveTo(midX + 30, 0); ctx.lineTo(midX + 150, canvas.height); ctx.lineTo(midX + 70, canvas.height); ctx.lineTo(midX - 20, 0); ctx.closePath(); ctx.fill();
        ctx.fillStyle = `rgba(52, 211, 153, ${causticPulse * 0.7})`; ctx.beginPath(); ctx.moveTo(midX - 40 + Math.sin(timeTick * 0.01) * 20, 0); ctx.lineTo(midX + 40, canvas.height); ctx.lineTo(midX, canvas.height); ctx.lineTo(midX - 100 + Math.sin(timeTick * 0.01) * 20, 0); ctx.closePath(); ctx.fill();

        kelpFronds.forEach(k => {
            const sway = Math.sin(timeTick * 0.015 + k.phase) * k.sway;
            ctx.strokeStyle = "rgba(6, 78, 59, 0.35)"; ctx.lineWidth = 6; ctx.beginPath();
            ctx.moveTo(k.x, canvas.height); ctx.quadraticCurveTo(k.x + sway, canvas.height - k.height * 0.5, k.x + sway * 1.6, canvas.height - k.height); ctx.stroke();
        });

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
                    sound("ding"); score += Math.floor(t.radius * 12); player.radius += t.radius * 0.11;
                    spawnParticles(t.x, t.y, 150, 8);
                    marineThreats.splice(index, 1);
                    scoreLabel.innerText = "SCORE: " + String(score).padStart(5, '0');
                    sizeLabel.innerText = `RANK: ${getRankName(player.radius)} (${Math.floor(player.radius)})`;
                    if (player.radius >= 55) terminateGameEngine(true);
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
