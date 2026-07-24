import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Virtua Arcade: Feeding Frenzy 3D", layout="centered")
st.title("🐋 Virtua Arcade: Feeding Frenzy 3D Evolution")
st.caption("Drag your finger or cursor to navigate the depths. Consume green-tinted prey, avoid red alpha predators!")

# Part A: Setup the structural HTML headers and abyssal theme stylings
game_html = r"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; padding: 0; background: #01040a; font-family: monospace; user-select: none; -webkit-user-select: none; overflow: hidden; }
        #gameContainer { position: relative; width: 380px; height: 480px; margin: auto; border: 4px solid #10b981; border-radius: 16px; overflow: hidden; box-shadow: 0 0 35px rgba(16, 185, 129, 0.25); touch-action: none; }
        canvas { display: block; background: #020b18; }
        #hud { position: absolute; top: 14px; left: 14px; right: 14px; display: flex; justify-content: space-between; color: #34d399; font-size: 15px; font-weight: bold; pointer-events: none; z-index: 10; text-shadow: 0 0 8px #047857; letter-spacing: 1px; }
        #screenOverlay { position: absolute; inset: 0; background: rgba(2, 8, 20, 0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 20; color: white; text-align: center; }
        .arcade-btn { margin-top: 20px; padding: 12px 28px; background: #10b981; color: #01040a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); font-family: monospace; font-size: 13px; letter-spacing: 1px; transition: transform 0.1s; }
        .arcade-btn:active { transform: scale(0.95); }
    </style>
</head>
"""
# Part B: Append layout nodes, interactive menus, and mouse/touch vector trackers
game_html += r"""
<body>
    <div id="gameContainer">
        <div id="hud">
            <div id="scoreLabel">SCORE: 00000</div>
            <div id="sizeLabel">RANK: MINNOW (15)</div>
        </div>
        <div id="screenOverlay">
            <h2 id="overlayTitle" style="color: #10b981; letter-spacing: 3px; font-size: 24px; margin: 0;">FEEDING FRENZY 3D</h2>
            <p id="overlaySub" style="color: #64748b; font-size: 11px; max-width: 290px; line-height: 1.6; margin-top: 10px;">Navigate deep abyssal cross-currents. Consume smaller bioluminescent lifeforms to trigger physical scaling growth.</p>
            <button class="arcade-btn" id="actionBtn" onclick="initiateArcadeGame()">DESCENT INTO DEEP 🌊</button>
        </div>
        <canvas id="aquariumCanvas" width="380" height="480"></canvas>
    </div>

<script>
    const canvas = document.getElementById("aquariumCanvas"); const ctx = canvas.getContext("2d");
    const container = document.getElementById("gameContainer"); const scoreLabel = document.getElementById("scoreLabel");
    const sizeLabel = document.getElementById("sizeLabel"); const screenOverlay = document.getElementById("screenOverlay");
    const overlayTitle = document.getElementById("overlayTitle"); const overlaySub = document.getElementById("overlaySub");
    const actionBtn = document.getElementById("actionBtn");

    let score = 0, gameActive = false;
    let player = { x: 190, y: 240, radius: 15, targetX: 190, targetY: 240, speed: 0.06, facingLeft: false, tailWag: 0 };
    let marineThreats = []; let environmentBubbles = [];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;

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
    container.addEventListener("touchstart", (e) => { setupAudio(); if(e.touches.length > 0) updateInputCoordinates(e.touches.clientX, e.touches.clientY); }, { passive: true });
    container.addEventListener("touchmove", (e) => { e.preventDefault(); if(e.touches.length > 0) updateInputCoordinates(e.touches.clientX, e.touches.clientY); }, { passive: false });
"""
# Part C: Inject the math vectors that render lighting reflections and organic fin movements
game_html += r"""
    function draw3DFishMesh(x, y, r, isLeft, baseHue, fishType, pulseTick) {
        ctx.save(); ctx.translate(x, y); if (isLeft) ctx.scale(-1, 1);
        const wag = Math.sin(pulseTick * 0.2) * (r * 0.25);
        let finGrd = ctx.createLinearGradient(-r, 0, -r * 2, 0);
        finGrd.addColorStop(0, `hsl(${baseHue}, 85%, 35%)`); finGrd.addColorStop(1, `hsl(${(baseHue+40)%360}, 90%, 55%)`);
        ctx.fillStyle = finGrd; ctx.beginPath();
        if (fishType === 2) {
            ctx.moveTo(-r * 0.8, 0); ctx.quadraticCurveTo(-r * 1.5, -r * 0.8 + wag, -r * 2, -r * 0.9 + wag); ctx.lineTo(-r * 1.5, wag); ctx.lineTo(-r * 2, r * 0.9 + wag); ctx.quadraticCurveTo(-r * 1.5, r * 0.8 + wag, -r * 0.8, 0);
        } else {
            ctx.moveTo(-r * 0.7, 0); ctx.lineTo(-r * 1.8, -r * 0.7 + wag); ctx.lineTo(-r * 1.4, wag); ctx.lineTo(-r * 1.8, r * 0.7 + wag);
        }
        ctx.closePath(); ctx.fill();
        let bodyYScale = fishType === 1 ? 1.0 : (fishType === 2 ? 0.65 : 0.8); ctx.scale(1, bodyYScale);
        let bodyGrd = ctx.createRadialGradient(r * 0.2, -r * 0.2, r * 0.1, 0, 0, r);
        bodyGrd.addColorStop(0, `hsl(${(baseHue+20)%360}, 90%, 75%)`); bodyGrd.addColorStop(0.3, `hsl(${baseHue}, 85%, 45%)`); bodyGrd.addColorStop(0.8, `hsl(${baseHue}, 95%, 20%)`); bodyGrd.addColorStop(1, '#01050e');
        ctx.fillStyle = bodyGrd; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = `hsl(${baseHue}, 60%, 15%)`; ctx.lineWidth = Math.max(1, r*0.06); ctx.beginPath(); ctx.arc(-r * 0.2, 0, r * 0.5, -Math.PI*0.3, Math.PI*0.3); ctx.stroke();
        ctx.fillStyle = `hsl(${(baseHue+30)%360}, 80%, 40%)`; ctx.beginPath(); ctx.ellipse(-r*0.1, r*0.2, r*0.3, r*0.15, Math.PI*0.15, 0, Math.PI*2); ctx.fill();
        ctx.scale(1, 1 / bodyYScale); let eyeX = r * 0.5; let eyeY = -r * 0.25; let eyeRadius = Math.max(3, r * 0.22);
        let eyeGrd = ctx.createRadialGradient(eyeX - eyeRadius*0.2, eyeY - eyeRadius*0.2, 1, eyeX, eyeY, eyeRadius); eyeGrd.addColorStop(0, "#ffffff"); eyeGrd.addColorStop(1, "#94a3b8");
        ctx.fillStyle = eyeGrd; ctx.beginPath(); ctx.arc(eyeX, eyeY, eyeRadius, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#020617"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius*0.2, eyeY, eyeRadius * 0.5, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX + eyeRadius*0.4, eyeY - eyeRadius*0.2, eyeRadius * 0.15, 0, Math.PI*2); ctx.fill(); ctx.restore();
    }
"""
# Part D: Manage state rules, collision detection logic, and load the component live into Streamlit
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; player.radius = 15; player.x = 190; player.y = 240; player.targetX = 190; player.targetY = 240;
        marineThreats = []; environmentBubbles = []; screenOverlay.style.display = "none"; scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "RANK: MINNOW (15)";
        if(spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 1000);
        if(animationFrameId) cancelAnimationFrame(animationFrameId); runGameLoop();
    }

    function generateMarineLife() {
        if (!gameActive) return; const spawnFromLeft = Math.random() > 0.5;
        const sizeRadius = Math.floor(Math.random() * (player.radius + 22 - Math.max(6, player.radius - 12))) + Math.max(6, player.radius - 12);
        const specificType = Math.floor(Math.random() * 3) + 1;
        marineThreats.push({ x: spawnFromLeft ? -60 : 440, y: Math.random() * (canvas.height - 60) + 30, radius: sizeRadius, speed: (Math.random() * 0.9 + 0.5) * (spawnFromLeft ? 1 : -1), fishType: specificType, loopSeed: Math.random() * 100 });
    }

    function getRankName(r) { if(r < 25) return "MINNOW"; if(r < 40) return "BASS"; if(r < 55) return "TUNA"; return "APEX SHARK"; }

    function terminateGameEngine(victory) {
        gameActive = false; clearInterval(spawnIntervalId); cancelAnimationFrame(animationFrameId); screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX OCEAN GOD 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution completed safely! Final Score: ${score}`; actionBtn.innerText = "RESTART EVOLUTION 🔄"; }
        else { sound("boom"); overlayTitle.innerText = "🐋 CONSUMED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You became organic mass. Final Score: ${score}`; actionBtn.innerText = "REDEPLOY DESCENT 🔄"; }
    }

    function runGameLoop() {
        if (!gameActive) return; player.tailWag++;
        let oceanBackground = ctx.createLinearGradient(0, 0, 0, canvas.height); oceanBackground.addColorStop(0, "#041628"); oceanBackground.addColorStop(0.5, "#020f1c"); oceanBackground.addColorStop(1, "#01050d"); ctx.fillStyle = oceanBackground; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "rgba(16, 185, 129, 0.02)"; ctx.beginPath(); ctx.moveTo(60, 0); ctx.lineTo(190, 480); ctx.lineTo(110, 480); ctx.lineTo(20, 0); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.moveTo(220, 0); ctx.lineTo(340, 480); ctx.lineTo(260, 480); ctx.lineTo(170, 0); ctx.closePath(); ctx.fill();
        if (Math.random() < 0.06) environmentBubbles.push({ x: Math.random() * canvas.width, y: 500, r: Math.random() * 2.5 + 1, speed: Math.random() * 0.8 + 0.4 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed; ctx.fillStyle = "rgba(52, 211, 153, 0.12)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });
        let dx = player.targetX - player.x; let dy = player.targetY - player.y; player.x += dx * player.speed; player.y += dy * player.speed; if (dx !== 0 && Math.abs(dx) > 1) player.facingLeft = dx < 0;
        draw3DFishMesh(player.x, player.y, player.radius, player.facingLeft, 185, 3, player.tailWag);
        marineThreats.forEach((t, index) => {
            t.x += t.speed; t.loopSeed++; const isTargetEdible = t.radius < player.radius; const dynamicHue = isTargetEdible ? 140 : 0;
            draw3DFishMesh(t.x, t.y, t.radius, t.speed < 0, dynamicHue, t.fishType, t.loopSeed);
            let distance = Math.hypot(player.x - t.x, player.y - t.y);
            if (distance < player.radius + t.radius * 0.75) {
                if (isTargetEdible) { sound("ding"); score += Math.floor(t.radius * 12); player.radius += t.radius * 0.11; marineThreats.splice(index, 1); scoreLabel.innerText = "SCORE: " + String(score).padStart(5, '0'); sizeLabel.innerText = `RANK: ${getRankName(player.radius)} (${Math.floor(player.radius)})`; if (player.radius >= 55) terminateGameEngine(true); }
                else { terminateGameEngine(false); }
            }
            if ((t.speed > 0 && t.x > 460) || (t.speed < 0 && t.x < -60)) marineThreats.splice(index, 1);
        });
        animationFrameId = requestAnimationFrame(runGameLoop);
    }
</script>
</body>
</html>
"""

components.html(game_html, height=520, scrolling=False)
