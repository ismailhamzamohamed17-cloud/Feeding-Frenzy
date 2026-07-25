import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Virtua Arcade: Feeding Frenzy 3D", layout="wide")
st.title("🐋 Virtua Arcade: Feeding Frenzy 3D Evolution")
st.caption("Drag your finger or cursor to navigate the depths. Consume green-tinted prey, avoid red alpha predators!")

# Part A: Full-screen deep-sea canvas layout (fills the viewport on both PC and mobile)
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
        #screenOverlay { position: absolute; inset: 0; background: rgba(2, 8, 20, 0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 20; color: white; text-align: center; }
        .arcade-btn { margin-top: 20px; padding: 14px 30px; background: #10b981; color: #01040a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); font-family: monospace; font-size: 14px; letter-spacing: 1px; transition: transform 0.1s; }
        .arcade-btn:active { transform: scale(0.95); }
    </style>
</head>
"""
# Part B: Menus and stabilized single-finger / mouse input interceptors
game_html += r"""
<body>
    <div id="gameContainer">
        <div id="hud">
            <div id="scoreLabel">SCORE: 00000</div>
            <div id="sizeLabel">RANK: MINNOW (15)</div>
        </div>
        <div id="screenOverlay">
            <h2 id="overlayTitle" style="color: #10b981; letter-spacing: 3px; font-size: 26px; margin: 0;">FEEDING FRENZY 3D</h2>
            <p id="overlaySub" style="color: #64748b; font-size: 12px; max-width: 320px; line-height: 1.6; margin-top: 10px;">Navigate deep abyssal cross-currents. Consume smaller bioluminescent lifeforms to trigger physical scaling growth.</p>
            <button class="arcade-btn" id="actionBtn" onclick="initiateArcadeGame()">DESCENT INTO DEEP 🌊</button>
        </div>
        <canvas id="aquariumCanvas"></canvas>
    </div>

<script>
    const canvas = document.getElementById("aquariumCanvas"); const ctx = canvas.getContext("2d");
    const container = document.getElementById("gameContainer"); const scoreLabel = document.getElementById("scoreLabel");
    const sizeLabel = document.getElementById("sizeLabel"); const screenOverlay = document.getElementById("screenOverlay");
    const overlayTitle = document.getElementById("overlayTitle"); const overlaySub = document.getElementById("overlaySub");
    const actionBtn = document.getElementById("actionBtn");

    let score = 0, gameActive = false, timeTick = 0, lastTimestamp = null;
    let player = { x: 190, y: 240, vx: 0, vy: 0, radius: 15, targetX: 190, targetY: 240, facingLeft: false, tailWag: 0, tiltAngle: 0 };
    let marineThreats = []; let environmentBubbles = []; let particles = []; let kelpFronds = [];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;
    let screenShake = 0;

    // Full-screen resize handling — canvas always matches the actual viewport on PC and mobile alike
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

    container.addEventListener("touchstart", (e) => {
        setupAudio();
        if(e.touches && e.touches.length > 0) { updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); }
    }, { passive: true });

    container.addEventListener("touchmove", (e) => {
        e.preventDefault();
        if(e.touches && e.touches.length > 0) { updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); }
    }, { passive: false });
"""
# Part C: More sculpted, glossier 3D-style fish rendering with depth-based perspective scaling
game_html += r"""
    function draw3DFishMesh(x, y, r, isLeft, baseHue, fishType, pulseTick, speedMag, tiltAngle, depthScale) {
        ctx.save(); ctx.translate(x, y); ctx.scale(depthScale, depthScale); if (isLeft) ctx.scale(-1, 1);
        ctx.rotate(Math.max(-0.3, Math.min(0.3, tiltAngle)) * (isLeft ? -1 : 1));

        const wagSpeed = 0.1 + Math.min(0.28, speedMag * 0.2);
        const wag = Math.sin(pulseTick * wagSpeed) * (r * (0.2 + Math.min(0.15, speedMag * 0.1)));
        const tailWag = Math.sin(pulseTick * wagSpeed + 0.6) * (r * 0.32);

        ctx.save(); ctx.globalAlpha = 0.18; ctx.fillStyle = "#000814"; ctx.beginPath(); ctx.ellipse(r * 0.1, r * 1.3, r * 0.9, r * 0.28, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        let finGrd = ctx.createLinearGradient(-r, 0, -r * 2, 0);
        finGrd.addColorStop(0, `hsl(${baseHue}, 85%, 35%)`); finGrd.addColorStop(1, `hsl(${(baseHue+40)%360}, 90%, 55%)`);
        ctx.fillStyle = finGrd;

        ctx.beginPath();
        if (fishType === 2) {
            ctx.moveTo(-r * 0.8, 0); ctx.quadraticCurveTo(-r * 1.5, -r * 0.8 + tailWag, -r * 2.1, -r * 0.9 + tailWag); ctx.lineTo(-r * 1.5, tailWag); ctx.lineTo(-r * 2.1, r * 0.9 + tailWag); ctx.quadraticCurveTo(-r * 1.5, r * 0.8 + tailWag, -r * 0.8, 0);
        } else {
            ctx.moveTo(-r * 0.7, 0); ctx.lineTo(-r * 1.9, -r * 0.7 + tailWag); ctx.lineTo(-r * 1.4, tailWag); ctx.lineTo(-r * 1.9, r * 0.7 + tailWag);
        }
        ctx.closePath(); ctx.fill();

        ctx.beginPath(); ctx.moveTo(-r * 0.1, -r * 0.85); ctx.quadraticCurveTo(r * 0.15, -r * 1.5 + wag * 0.3, r * 0.5, -r * 0.8); ctx.quadraticCurveTo(r * 0.15, -r * 0.75, -r * 0.1, -r * 0.85); ctx.fill();

        ctx.beginPath();
        ctx.moveTo(-r * 0.1, r * 0.3); ctx.quadraticCurveTo(r * 0.1, r * 0.9 + wag * 0.4, r * 0.35, r * 0.75 + wag * 0.4); ctx.quadraticCurveTo(r * 0.15, r * 0.5, -r * 0.1, r * 0.3);
        ctx.fill();

        let bodyYScale = fishType === 1 ? 1.0 : (fishType === 2 ? 0.65 : 0.8); ctx.scale(1, bodyYScale);
        let bodyGrd = ctx.createRadialGradient(r * 0.25, -r * 0.3, r * 0.05, r * 0.05, r * 0.1, r * 1.15);
        bodyGrd.addColorStop(0, `hsl(${(baseHue+25)%360}, 95%, 82%)`);
        bodyGrd.addColorStop(0.25, `hsl(${(baseHue+15)%360}, 90%, 55%)`);
        bodyGrd.addColorStop(0.55, `hsl(${baseHue}, 85%, 38%)`);
        bodyGrd.addColorStop(0.85, `hsl(${baseHue}, 90%, 18%)`);
        bodyGrd.addColorStop(1, '#01050e');
        ctx.fillStyle = bodyGrd; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

        ctx.save(); ctx.globalAlpha = 0.25; ctx.fillStyle = "#000308";
        ctx.beginPath(); ctx.ellipse(0, r * 0.55, r * 0.75, r * 0.4, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        ctx.save(); ctx.globalAlpha = 0.55; ctx.fillStyle = "#ffffff";
        ctx.beginPath(); ctx.ellipse(r * 0.15, -r * 0.4, r * 0.32, r * 0.16, -0.4, 0, Math.PI * 2); ctx.fill(); ctx.restore();

        ctx.strokeStyle = `hsla(${(baseHue+60)%360}, 90%, 75%, 0.5)`; ctx.lineWidth = Math.max(1, r * 0.08);
        ctx.beginPath(); ctx.arc(0, 0, r * 0.97, Math.PI * 1.1, Math.PI * 1.75); ctx.stroke();

        ctx.strokeStyle = `hsl(${baseHue}, 60%, 15%)`; ctx.lineWidth = Math.max(1, r*0.06);
        ctx.beginPath(); ctx.arc(-r * 0.2, 0, r * 0.5, -Math.PI*0.3, Math.PI*0.3); ctx.stroke();
        ctx.beginPath(); ctx.arc(-r * 0.5, 0, r * 0.35, -Math.PI*0.3, Math.PI*0.3); ctx.stroke();

        ctx.fillStyle = `hsl(${(baseHue+30)%360}, 80%, 40%)`; ctx.beginPath(); ctx.ellipse(-r*0.1, r*0.2, r*0.3, r*0.15, Math.PI*0.15, 0, Math.PI*2); ctx.fill();
        ctx.scale(1, 1 / bodyYScale); let eyeX = r * 0.5; let eyeY = -r * 0.25; let eyeRadius = Math.max(3, r * 0.22);
        let eyeGrd = ctx.createRadialGradient(eyeX - eyeRadius*0.2, eyeY - eyeRadius*0.2, 1, eyeX, eyeY, eyeRadius); eyeGrd.addColorStop(0, "#ffffff"); eyeGrd.addColorStop(1, "#94a3b8");
        ctx.fillStyle = eyeGrd; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#020617"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius*0.2, eyeY, eyeRadius * 0.5, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius*0.4, eyeY - eyeRadius*0.2, eyeRadius * 0.15, 0, Math.PI*2); ctx.fill(); ctx.restore();
    }

    function spawnParticles(x, y, hue, count) {
        for (let i = 0; i < count; i++) {
            particles.push({ x, y, vx: (Math.random()-0.5)*3, vy: (Math.random()-0.5)*3, life: 1, hue });
        }
    }
"""
# Part D: Frame-rate-independent physics (same speed on PC and mobile), slow straight horizontal fish traffic, and safe Streamlit injection
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; player.radius = 15;
        player.x = canvas.width / 2; player.y = canvas.height / 2; player.targetX = player.x; player.targetY = player.y; player.vx = 0; player.vy = 0;
        marineThreats = []; environmentBubbles = []; particles = []; screenShake = 0; lastTimestamp = null;
        screenOverlay.style.display = "none"; scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "RANK: MINNOW (15)";
        if(spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 1100);
        if(animationFrameId) cancelAnimationFrame(animationFrameId); animationFrameId = requestAnimationFrame(runGameLoop);
    }

    // Fish travel in slow, straight horizontal lines only — no vertical wander, no reversing direction
    function generateMarineLife() {
        if (!gameActive) return; const spawnFromLeft = Math.random() > 0.5;
        const schoolSize = Math.random() < 0.45 ? Math.floor(Math.random() * 3) + 2 : 1;
        const sizeRadius = Math.floor(Math.random() * (player.radius + 22 - Math.max(6, player.radius - 12))) + Math.max(6, player.radius - 12);
        const specificType = Math.floor(Math.random() * 3) + 1;
        const baseY = Math.random() * (canvas.height - 80) + 40;
        const baseSpeed = (Math.random() * 0.35 + 0.25) * (spawnFromLeft ? 1 : -1);
        for (let i = 0; i < schoolSize; i++) {
            marineThreats.push({
                x: (spawnFromLeft ? -60 : canvas.width + 60) - i * 34 * (spawnFromLeft ? 1 : -1),
                y: baseY + (Math.random() - 0.5) * 40,
                radius: Math.max(5, sizeRadius + (Math.random() - 0.5) * 5),
                vx: baseSpeed, vy: 0,
                fishType: specificType, wagPhase: Math.random() * 100
            });
        }
    }

    function getRankName(r) { if(r < 25) return "MINNOW"; if(r < 40) return "BASS"; if(r < 55) return "TUNA"; return "APEX SHARK"; }

    function terminateGameEngine(victory) {
        gameActive = false; clearInterval(spawnIntervalId); cancelAnimationFrame(animationFrameId); screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX OCEAN GOD 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution completed safely! Final Score: ${score}`; actionBtn.innerText = "RESTART EVOLUTION 🔄"; }
        else { sound("boom"); screenShake = 14; overlayTitle.innerText = "🐋 CONSUMED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You became organic mass. Final Score: ${score}`; actionBtn.innerText = "REDEPLOY DESCENT 🔄"; }
    }

    function runGameLoop(timestamp) {
        if (!gameActive) return;
        if (lastTimestamp === null) lastTimestamp = timestamp;
        // Normalize movement to a 60fps baseline so a 144Hz PC monitor doesn't run the sim faster than a 60Hz phone
        let dt = (timestamp - lastTimestamp) / (1000 / 60);
        dt = Math.max(0, Math.min(dt, 3));
        lastTimestamp = timestamp;
        timeTick += dt;

        ctx.save();
        if (screenShake > 0) { ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake); screenShake *= 0.9; if (screenShake < 0.3) screenShake = 0; }

        let oceanBackground = ctx.createLinearGradient(0, 0, 0, canvas.height); oceanBackground.addColorStop(0, "#041628"); oceanBackground.addColorStop(0.5, "#020f1c"); oceanBackground.addColorStop(1, "#01050d"); ctx.fillStyle = oceanBackground; ctx.fillRect(0, 0, canvas.width, canvas.height);

        const causticPulse = 0.015 + Math.sin(timeTick * 0.02) * 0.008;
        const midX = canvas.width / 2;
        ctx.fillStyle = `rgba(16, 185, 129, ${causticPulse})`; ctx.beginPath(); ctx.moveTo(midX - 130, 0); ctx.lineTo(midX, canvas.height); ctx.lineTo(midX - 80, canvas.height); ctx.lineTo(midX - 170, 0); ctx.closePath(); ctx.fill();
        ctx.beginPath(); ctx.moveTo(midX + 30, 0); ctx.lineTo(midX + 150, canvas.height); ctx.lineTo(midX + 70, canvas.height); ctx.lineTo(midX - 20, 0); ctx.closePath(); ctx.fill();
        ctx.fillStyle = `rgba(52, 211, 153, ${causticPulse * 0.7})`; ctx.beginPath(); ctx.moveTo(midX - 40 + Math.sin(timeTick*0.01)*20, 0); ctx.lineTo(midX + 40, canvas.height); ctx.lineTo(midX, canvas.height); ctx.lineTo(midX - 100 + Math.sin(timeTick*0.01)*20, 0); ctx.closePath(); ctx.fill();

        kelpFronds.forEach(k => {
            const sway = Math.sin(timeTick * 0.015 + k.phase) * k.sway;
            ctx.strokeStyle = "rgba(6, 78, 59, 0.35)"; ctx.lineWidth = 6; ctx.beginPath();
            ctx.moveTo(k.x, canvas.height); ctx.quadraticCurveTo(k.x + sway, canvas.height - k.height * 0.5, k.x + sway * 1.6, canvas.height - k.height); ctx.stroke();
        });

        if (Math.random() < 0.06 * dt) environmentBubbles.push({ x: Math.random() * canvas.width, y: canvas.height + 20, r: Math.random() * 2.5 + 1, speed: Math.random() * 0.8 + 0.4, drift: (Math.random()-0.5)*0.4 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed * dt; b.x += b.drift * dt; ctx.fillStyle = "rgba(52, 211, 153, 0.12)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });

        particles.forEach((p, i) => {
            p.x += p.vx * dt; p.y += p.vy * dt; p.life -= 0.04 * dt;
            if (p.life <= 0) { particles.splice(i, 1); return; }
            ctx.fillStyle = `hsla(${p.hue}, 90%, 65%, ${p.life})`; ctx.beginPath(); ctx.arc(p.x, p.y, 2.5 * p.life, 0, Math.PI*2); ctx.fill();
        });

        let dx = player.targetX - player.x; let dy = player.targetY - player.y; let dist = Math.hypot(dx, dy);
        const maxSpeed = 1.5 + player.radius * 0.012;
        const desiredSpeed = Math.min(dist * 0.07, maxSpeed);
        const desiredVX = dist > 0.5 ? (dx / dist) * desiredSpeed : 0;
        const desiredVY = dist > 0.5 ? (dy / dist) * desiredSpeed : 0;
        const agilityBase = Math.max(0.03, 0.1 - player.radius * 0.0009);
        const agility = Math.min(1, agilityBase * dt);
        player.vx += (desiredVX - player.vx) * agility; player.vy += (desiredVY - player.vy) * agility;
        player.x += player.vx * dt; player.y += player.vy * dt;
        player.x = Math.max(15, Math.min(player.x, canvas.width - 15)); player.y = Math.max(15, Math.min(player.y, canvas.height - 15));
        if (Math.abs(player.vx) > 0.1) player.facingLeft = player.vx < 0;
        player.tiltAngle += ((player.vy * 0.12) - player.tiltAngle) * Math.min(1, 0.15 * dt);
        player.tailWag += dt;
        const playerSpeedMag = Math.hypot(player.vx, player.vy);
        const playerDepth = 0.85 + (player.y / canvas.height) * 0.3;
        draw3DFishMesh(player.x, player.y, player.radius, player.facingLeft, 185, 3, player.tailWag, playerSpeedMag, player.tiltAngle, playerDepth);

        for (let index = marineThreats.length - 1; index >= 0; index--) {
            const t = marineThreats[index];
            t.x += t.vx * dt; t.wagPhase += dt;
            const isTargetEdible = t.radius < player.radius; const dynamicHue = isTargetEdible ? 140 : 0;
            const tSpeedMag = Math.abs(t.vx);
            const tDepth = 0.85 + (t.y / canvas.height) * 0.3;
            draw3DFishMesh(t.x, t.y, t.radius, t.vx < 0, dynamicHue, t.fishType, t.wagPhase, tSpeedMag, 0, tDepth);
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

components.html(game_html, height=800, scrolling=False)
st.info("Tip: for a true full-screen arcade feel, open this app and use your browser's fullscreen mode (F11 on PC, or 'Add to Home Screen' on mobile).")
