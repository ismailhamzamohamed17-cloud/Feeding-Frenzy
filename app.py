import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Virtua Arcade: Feeding Frenzy", layout="centered")
st.title("🐟 Virtua Arcade: Feeding Frenzy")
st.caption("Move your cursor or drag your finger on mobile to feed and grow! Avoid bigger fish.")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; padding: 0; background: #010a15; font-family: monospace; user-select: none; -webkit-user-select: none; overflow: hidden; }
        #gameContainer { position: relative; width: 380px; height: 480px; margin: auto; border: 4px solid #00f0ff; border-radius: 16px; overflow: hidden; box-shadow: 0 0 30px rgba(0, 240, 255, 0.3); touch-action: none; }
        canvas { display: block; background: linear-gradient(to bottom, #02162e, #010714); }
        #hud { position: absolute; top: 12px; left: 12px; right: 12px; display: flex; justify-content: space-between; color: #00f0ff; font-size: 16px; font-weight: bold; pointer-events: none; z-index: 10; text-shadow: 0 0 5px #00f0ff; }
        #screenOverlay { position: absolute; inset: 0; background: rgba(1, 10, 21, 0.85); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 20; color: white; text-align: center; }
        .arcade-btn { margin-top: 15px; padding: 10px 24px; background: #00f0ff; color: #010a15; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px #00f0ff; font-family: monospace; }
    </style>
</head>
"""
<body>
    <div id="gameContainer">
        <div id="hud">
            <div id="scoreLabel">SCORE: 00000</div>
            <div id="sizeLabel">SIZE: 15</div>
        </div>
        <div id="screenOverlay">
            <h2 id="overlayTitle" style="color: #00f0ff; letter-spacing: 2px;">FEEDING FRENZY</h2>
            <p id="overlaySub" style="color: #64748b; font-size: 12px; max-width: 280px;">Eat smaller fish to grow. Avoid larger ocean predators!</p>
            <button class="arcade-btn" id="actionBtn" onclick="initiateArcadeGame()">START VENTURE </button>
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
    let player = { x: 190, y: 240, radius: 15, targetX: 190, targetY: 240, speed: 0.12, facingLeft: false };
    let marineThreats = []; let environmentBubbles = [];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;

    function setupAudio() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
    function sound(type) {
        setupAudio(); if (!audioCtx) return; let osc = audioCtx.createOscillator(), gain = audioCtx.createGain(); osc.connect(gain); gain.connect(audioCtx.destination);
        if (type === "zap") { osc.type = "sawtooth"; osc.frequency.setValueAtTime(540, audioCtx.currentTime); osc.frequency.exponentialRampToValueAtTime(45, audioCtx.currentTime + 0.15); gain.gain.setValueAtTime(0.4, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.15); }
        else if (type === "ding") { osc.type = "sine"; osc.frequency.setValueAtTime(950, audioCtx.currentTime); osc.frequency.linearRampToValueAtTime(1350, audioCtx.currentTime + 0.08); gain.gain.setValueAtTime(0.2, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.08); }
        else if (type === "boom") { osc.type = "sawtooth"; osc.frequency.setValueAtTime(110, audioCtx.currentTime); osc.frequency.exponentialRampToValueAtTime(20, audioCtx.currentTime + 0.38); gain.gain.setValueAtTime(0.5, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.38); }
        else if (type === "level") { osc.type = "sine"; osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.1); osc.frequency.setValueAtTime(783.99, audioCtx.currentTime + 0.2); gain.gain.setValueAtTime(0.25, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.4); }
    }

    function updateInputCoordinates(clientX, clientY) {
        if (!gameActive) return; const rect = container.getBoundingClientRect();
        player.targetX = Math.max(10, Math.min(clientX - rect.left, rect.width - 10));
        player.targetY = Math.max(10, Math.min(clientY - rect.top, rect.height - 10));
    }
    container.addEventListener("mousemove", (e) => updateInputCoordinates(e.clientX, e.clientY));
    container.addEventListener("touchstart", (e) => { setupAudio(); if(e.touches.length > 0) updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
    container.addEventListener("touchmove", (e) => { e.preventDefault(); if(e.touches.length > 0) updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY); }, { passive: false });

    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; player.radius = 15; player.x = 190; player.y = 240; player.targetX = 190; player.targetY = 240;
        marineThreats = []; environmentBubbles = []; screenOverlay.style.display = "none"; scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "SIZE: 15";
        if(spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 900);
        if(animationFrameId) cancelAnimationFrame(animationFrameId); runGameLoop();
    }
    function generateMarineLife() {
        if (!gameActive) return; const spawnFromLeft = Math.random() > 0.5;
        const minSize = Math.max(6, player.radius - 10), maxSize = player.radius + 18;
        const sizeRadius = Math.floor(Math.random() * (maxSize - minSize)) + minSize;
        marineThreats.push({ x: spawnFromLeft ? -50 : 430, y: Math.random() * (canvas.height - 40) + 20, radius: sizeRadius, speed: (Math.random() * 2 + 1.2) * (spawnFromLeft ? 1 : -1), color: "" });
    }
    function terminateGameEngine(victory) {
        gameActive = false; clearInterval(spawnIntervalId); cancelAnimationFrame(animationFrameId); screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX PREDATOR 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution complete! Final Score Account: ${score}`; actionBtn.innerText = "EVOLVE AGAIN 🔄"; }
        else { sound("boom"); overlayTitle.innerText = "🐋 WASTED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You got consumed! Final Score Log: ${score}`; actionBtn.innerText = "REDEPLOY VENTURE 🔄"; }
    }
    function runGameLoop() {
        if (!gameActive) return; ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (Math.random() < 0.08) environmentBubbles.push({ x: Math.random() * canvas.width, y: 500, r: Math.random() * 3 + 1, speed: Math.random() * 1 + 0.5 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed; ctx.fillStyle = "rgba(0, 240, 255, 0.15)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });
        let dx = player.targetX - player.x; let dy = player.targetY - player.y; player.x += dx * player.speed; player.y += dy * player.speed; if (dx !== 0) player.facingLeft = dx < 0;
        ctx.fillStyle = "#00f0ff"; ctx.beginPath(); ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = "#00a8ff"; ctx.beginPath();
        if (player.facingLeft) { ctx.moveTo(player.x + player.radius, player.y); ctx.lineTo(player.x + player.radius * 1.8, player.y - player.radius * 0.6); ctx.lineTo(player.x + player.radius * 1.8, player.y + player.radius * 0.6); }
        else { ctx.moveTo(player.x - player.radius, player.y); ctx.lineTo(player.x - player.radius * 1.8, player.y - player.radius * 0.6); ctx.lineTo(player.x - player.radius * 1.8, player.y + player.radius * 0.6); }
        ctx.closePath(); ctx.fill();
        marineThreats.forEach((t, index) => {
            t.x += t.speed; t.color = t.radius < player.radius ? "#22c55e" : "#ef4444"; ctx.fillStyle = t.color; ctx.beginPath(); ctx.arc(t.x, t.y, t.radius, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.beginPath();
            if (t.speed > 0) { ctx.moveTo(t.x - t.radius, t.y); ctx.lineTo(t.x - t.radius * 1.7, t.y - t.radius * 0.5); ctx.lineTo(t.x - t.radius * 1.7, t.y + t.radius * 0.5); }
            else { ctx.moveTo(t.x + t.radius, t.y); ctx.lineTo(t.x + t.radius * 1.7, t.y - t.radius * 0.5); ctx.lineTo(t.x + t.radius * 1.7, t.y + t.radius * 0.5); }
            ctx.closePath(); ctx.fill();
            let collisionDistance = Math.hypot(player.x - t.x, player.y - t.y);
            if (collisionDistance < player.radius + t.radius * 0.8) {
                if (player.radius >= t.radius) { sound("ding"); score += Math.floor(t.radius * 10); player.radius += t.radius * 0.12; marineThreats.splice(index, 1); scoreLabel.innerText = "SCORE: " + String(score).padStart(5, '0'); sizeLabel.innerText = "SIZE: " + Math.floor(player.radius); if (player.radius >= 55) terminateGameEngine(true); }
                else { terminateGameEngine(false); }
            }
            if ((t.speed > 0 && t.x > 450) || (t.speed < 0 && t.x < -60)) marineThreats.splice(index, 1);
        });
        animationFrameId = requestAnimationFrame(runGameLoop);
    }
</script>
</body>
</html>
"""
components.html(game_html, height=520, scrolling=False)
