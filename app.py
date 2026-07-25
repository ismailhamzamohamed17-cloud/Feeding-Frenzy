import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Virtua Arcade: Feeding Frenzy 3D", layout="centered")
st.title("🐋 Virtua Arcade: Feeding Frenzy 3D Evolution")
st.caption("Drag your finger or cursor to navigate the depths. Consume green-tinted prey, avoid red alpha predators!")

# Part A: Setup structural canvas borders and the deep-sea dark palette layout
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
# Part B: Append dynamic interface menus and stabilized single-finger array element interceptors
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

    let score = 0, gameActive = false, timeTick = 0;
    let player = { x: 190, y: 240, vx: 0, vy: 0, radius: 15, targetX: 190, targetY: 240, facingLeft: false, tailWag: 0, tiltAngle: 0 };
    let marineThreats = []; let environmentBubbles = []; let particles = []; let kelpFronds = [];
    let animationFrameId = null, spawnIntervalId = null, audioCtx = null;
    let screenShake = 0;

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

    // Stabilized Multi-Device Handlers: Explicitly locking index zero array values for touch targets
    container.addEventListener("mousemove", (e) => updateInputCoordinates(e.clientX, e.clientY));

    container.addEventListener("touchstart", (e) => {
        setupAudio();
        if(e.touches && e.touches.length > 0) {
            updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY);
        }
    }, { passive: true });

    container.addEventListener("touchmove", (e) => {
        e.preventDefault(); // Disables phone viewport screen-bounce
        if(e.touches && e.touches.length > 0) {
            updateInputCoordinates(e.touches[0].clientX, e.touches[0].clientY);
        }
    }, { passive: false });

    for (let i = 0; i < 5; i++) {
        kelpFronds.push({ x: Math.random() * 380, height: 60 + Math.random() * 90, sway: Math.random() * 10, phase: Math.random() * 100 });
    }
"""
# Part C: Inject the 3D asset vectors that draw lighting reflections, gills, fins, tail undulation and rim light
game_html += r"""
    function draw3DFishMesh(x, y, r, isLeft, baseHue, fishType, pulseTick, speedMag, tiltAngle) {
        ctx.save(); ctx.translate(x, y); if (isLeft) ctx.scale(-1, 1);
        ctx.rotate(Math.max(-0.35, Math.min(0.35, tiltAngle)) * (isLeft ? -1 : 1));

        // Tail beat frequency scales with how fast the creature is actually swimming (realistic locomotion cue)
        const wagSpeed = 0.12 + Math.min(0.35, speedMag * 0.22);
        const wag = Math.sin(pulseTick * wagSpeed) * (r * (0.22 + Math.min(0.18, speedMag * 0.12)));
        const tailWag = Math.sin(pulseTick * wagSpeed + 0.6) * (r * 0.35);

        let finGrd = ctx.createLinearGradient(-r, 0, -r * 2, 0);
        finGrd.addColorStop(0, `hsl(${baseHue}, 85%, 35%)`); finGrd.addColorStop(1, `hsl(${(baseHue+40)%360}, 90%, 55%)`);
        ctx.fillStyle = finGrd;

        // Caudal (tail) fin — separate segment lagging the body for a proper swimming flex
        ctx.beginPath();
        if (fishType === 2) {
            ctx.moveTo(-r * 0.8, 0); ctx.quadraticCurveTo(-r * 1.5, -r * 0.8 + tailWag, -r * 2.1, -r * 0.9 + tailWag); ctx.lineTo(-r * 1.5, tailWag); ctx.lineTo(-r * 2.1, r * 0.9 + tailWag); ctx.quadraticCurveTo(-r * 1.5, r * 0.8 + tailWag, -r * 0.8, 0);
        } else {
            ctx.moveTo(-r * 0.7, 0); ctx.lineTo(-r * 1.9, -r * 0.7 + tailWag); ctx.lineTo(-r * 1.4, tailWag); ctx.lineTo(-r * 1.9, r * 0.7 + tailWag);
        }
        ctx.closePath(); ctx.fill();

        // Dorsal fin on top for silhouette realism
        ctx.beginPath(); ctx.moveTo(-r * 0.1, -r * 0.85); ctx.quadraticCurveTo(r * 0.15, -r * 1.5 + wag * 0.3, r * 0.5, -r * 0.8); ctx.quadraticCurveTo(r * 0.15, -r * 0.75, -r * 0.1, -r * 0.85); ctx.fill();

        // Pectoral (side) fin — flutters on its own phase, offset from the tail beat
        ctx.beginPath();
        ctx.moveTo(-r * 0.1, r * 0.3); ctx.quadraticCurveTo(r * 0.1, r * 0.9 + wag * 0.4, r * 0.35, r * 0.75 + wag * 0.4); ctx.quadraticCurveTo(r * 0.15, r * 0.5, -r * 0.1, r * 0.3);
        ctx.fill();

        let bodyYScale = fishType === 1 ? 1.0 : (fishType === 2 ? 0.65 : 0.8); ctx.scale(1, bodyYScale);
        let bodyGrd = ctx.createRadialGradient(r * 0.2, -r * 0.2, r * 0.1, 0, 0, r);
        bodyGrd.addColorStop(0, `hsl(${(baseHue+20)%360}, 90%, 75%)`); bodyGrd.addColorStop(0.3, `hsl(${baseHue}, 85%, 45%)`); bodyGrd.addColorStop(0.8, `hsl(${baseHue}, 95%, 20%)`); bodyGrd.addColorStop(1, '#01050e');
        ctx.fillStyle = bodyGrd; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

        // Rim light along the top edge, mimicking caustic light filtering down through the water
        ctx.strokeStyle = `hsla(${(baseHue+60)%360}, 90%, 75%, 0.5)`; ctx.lineWidth = Math.max(1, r * 0.08);
        ctx.beginPath(); ctx.arc(0, 0, r * 0.97, Math.PI * 1.1, Math.PI * 1.75); ctx.stroke();

        // Scale texture lines
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
# Part D: Process realistic swimming physics, boid-style schooling/predator-prey AI, and safely inject the final interactive window wrapper into Streamlit
game_html += r"""
    function initiateArcadeGame() {
        setupAudio(); score = 0; gameActive = true; player.radius = 15; player.x = 190; player.y = 240; player.targetX = 190; player.targetY = 240; player.vx = 0; player.vy = 0;
        marineThreats = []; environmentBubbles = []; particles = []; screenShake = 0; screenOverlay.style.display = "none"; scoreLabel.innerText = "SCORE: 00000"; sizeLabel.innerText = "RANK: MINNOW (15)";
        if(spawnIntervalId) clearInterval(spawnIntervalId); spawnIntervalId = setInterval(generateMarineLife, 900);
        if(animationFrameId) cancelAnimationFrame(animationFrameId); runGameLoop();
    }

    // Fish spawn in loose schools of similar size/species so shoaling behavior has something to act on
    function generateMarineLife() {
        if (!gameActive) return; const spawnFromLeft = Math.random() > 0.5;
        const schoolSize = Math.random() < 0.45 ? Math.floor(Math.random() * 3) + 2 : 1;
        const sizeRadius = Math.floor(Math.random() * (player.radius + 22 - Math.max(6, player.radius - 12))) + Math.max(6, player.radius - 12);
        const specificType = Math.floor(Math.random() * 3) + 1;
        const flockId = Math.random();
        const baseY = Math.random() * (canvas.height - 80) + 40;
        const baseSpeed = (Math.random() * 0.7 + 0.6) * (spawnFromLeft ? 1 : -1);
        for (let i = 0; i < schoolSize; i++) {
            marineThreats.push({
                x: (spawnFromLeft ? -60 : 440) - i * 34 * (spawnFromLeft ? 1 : -1),
                y: baseY + (Math.random() - 0.5) * 50,
                radius: Math.max(5, sizeRadius + (Math.random() - 0.5) * 5),
                vx: baseSpeed + (Math.random() - 0.5) * 0.2,
                vy: (Math.random() - 0.5) * 0.3,
                fishType: specificType, flockId, wagPhase: Math.random() * 100
            });
        }
    }

    function getRankName(r) { if(r < 25) return "MINNOW"; if(r < 40) return "BASS"; if(r < 55) return "TUNA"; return "APEX SHARK"; }

    function terminateGameEngine(victory) {
        gameActive = false; clearInterval(spawnIntervalId); cancelAnimationFrame(animationFrameId); screenOverlay.style.display = "flex";
        if (victory) { sound("level"); overlayTitle.innerText = "👑 APEX OCEAN GOD 👑"; overlayTitle.style.color = "#eab308"; overlaySub.innerText = `Evolution completed safely! Final Score: ${score}`; actionBtn.innerText = "RESTART EVOLUTION 🔄"; }
        else { sound("boom"); screenShake = 14; overlayTitle.innerText = "🐋 CONSUMED 🐋"; overlayTitle.style.color = "#ef4444"; overlaySub.innerText = `You became organic mass. Final Score: ${score}`; actionBtn.innerText = "REDEPLOY DESCENT 🔄"; }
    }

    // Simplified boid steering: separation + cohesion within a flock, plus flee-from-predator / chase-prey drives
    function stepMarineThreat(t) {
        let ax = 0, ay = 0;
        const isEdible = t.radius < player.radius;
        const pdx = player.x - t.x, pdy = player.y - t.y;
        const pdist = Math.hypot(pdx, pdy) || 1;

        if (isEdible && pdist < 95) { ax -= (pdx / pdist) * 0.16; ay -= (pdy / pdist) * 0.16; }
        else if (!isEdible && pdist < 150) { ax += (pdx / pdist) * 0.045; ay += (pdy / pdist) * 0.045; }

        let cohX = 0, cohY = 0, sepX = 0, sepY = 0, neighbors = 0;
        for (let o of marineThreats) {
            if (o === t || o.flockId !== t.flockId) continue;
            const odx = o.x - t.x, ody = o.y - t.y, odist = Math.hypot(odx, ody) || 1;
            if (odist < 85) { cohX += o.x; cohY += o.y; neighbors++; if (odist < 26) { sepX -= odx / odist; sepY -= ody / odist; } }
        }
        if (neighbors > 0) {
            cohX = cohX / neighbors - t.x; cohY = cohY / neighbors - t.y;
            const cl = Math.hypot(cohX, cohY) || 1; ax += (cohX / cl) * 0.02; ay += (cohY / cl) * 0.02;
        }
        ax += sepX * 0.035; ay += sepY * 0.035;

        // Gentle ambient current — a soft flow field so paths read as swimming, not sliding
        ax += Math.sin(timeTick * 0.012 + t.y * 0.02) * 0.012;
        ay += Math.cos(timeTick * 0.01 + t.x * 0.02) * 0.01;

        if (t.y < 30) ay += 0.08; if (t.y > canvas.height - 30) ay -= 0.08;

        t.vx += ax; t.vy += ay;
        const sp = Math.hypot(t.vx, t.vy); const maxSp = 1.7;
        if (sp > maxSp) { t.vx = (t.vx / sp) * maxSp; t.vy = (t.vy / sp) * maxSp; }
        t.x += t.vx; t.y += t.vy; t.wagPhase++;
    }

    function runGameLoop() {
        if (!gameActive) return; timeTick++;
        ctx.save();
        if (screenShake > 0) { ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake); screenShake *= 0.9; if (screenShake < 0.3) screenShake = 0; }

        let oceanBackground = ctx.createLinearGradient(0, 0, 0, canvas.height); oceanBackground.addColorStop(0, "#041628"); oceanBackground.addColorStop(0.5, "#020f1c"); oceanBackground.addColorStop(1, "#01050d"); ctx.fillStyle = oceanBackground; ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Animated caustic light shafts (opacity breathes over time instead of sitting static)
        const causticPulse = 0.015 + Math.sin(timeTick * 0.02) * 0.008;
        ctx.fillStyle = `rgba(16, 185, 129, ${causticPulse})`; ctx.beginPath(); ctx.moveTo(60, 0); ctx.lineTo(190, 480); ctx.lineTo(110, 480); ctx.lineTo(20, 0); ctx.closePath(); ctx.fill();
        ctx.beginPath(); ctx.moveTo(220, 0); ctx.lineTo(340, 480); ctx.lineTo(260, 480); ctx.lineTo(170, 0); ctx.closePath(); ctx.fill();
        ctx.fillStyle = `rgba(52, 211, 153, ${causticPulse * 0.7})`; ctx.beginPath(); ctx.moveTo(140 + Math.sin(timeTick*0.01)*20, 0); ctx.lineTo(230, 480); ctx.lineTo(190, 480); ctx.lineTo(100 + Math.sin(timeTick*0.01)*20, 0); ctx.closePath(); ctx.fill();

        // Swaying kelp silhouettes at the seafloor for parallax depth
        kelpFronds.forEach(k => {
            const sway = Math.sin(timeTick * 0.015 + k.phase) * k.sway;
            ctx.strokeStyle = "rgba(6, 78, 59, 0.35)"; ctx.lineWidth = 6; ctx.beginPath();
            ctx.moveTo(k.x, canvas.height); ctx.quadraticCurveTo(k.x + sway, canvas.height - k.height * 0.5, k.x + sway * 1.6, canvas.height - k.height); ctx.stroke();
        });

        if (Math.random() < 0.06) environmentBubbles.push({ x: Math.random() * canvas.width, y: 500, r: Math.random() * 2.5 + 1, speed: Math.random() * 0.8 + 0.4, drift: (Math.random()-0.5)*0.4 });
        environmentBubbles.forEach((b, i) => { b.y -= b.speed; b.x += b.drift; ctx.fillStyle = "rgba(52, 211, 153, 0.12)"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); if (b.y < -10) environmentBubbles.splice(i, 1); });

        // Bite/impact particles
        particles.forEach((p, i) => {
            p.x += p.vx; p.y += p.vy; p.life -= 0.04;
            if (p.life <= 0) { particles.splice(i, 1); return; }
            ctx.fillStyle = `hsla(${p.hue}, 90%, 65%, ${p.life})`; ctx.beginPath(); ctx.arc(p.x, p.y, 2.5 * p.life, 0, Math.PI*2); ctx.fill();
        });

        // Player physics: accelerate toward the touch/cursor target with inertia; bigger fish are heavier and turn slower
        let dx = player.targetX - player.x; let dy = player.targetY - player.y; let dist = Math.hypot(dx, dy);
        const maxSpeed = 2.6 + player.radius * 0.02;
        const desiredSpeed = Math.min(dist * 0.09, maxSpeed);
        const desiredVX = dist > 0.5 ? (dx / dist) * desiredSpeed : 0;
        const desiredVY = dist > 0.5 ? (dy / dist) * desiredSpeed : 0;
        const agility = Math.max(0.045, 0.17 - player.radius * 0.0016);
        player.vx += (desiredVX - player.vx) * agility; player.vy += (desiredVY - player.vy) * agility;
        // subtle current drift affects the player too, for consistency with the world
        player.vx += Math.sin(timeTick * 0.012 + player.y * 0.02) * 0.01;
        player.x += player.vx; player.y += player.vy;
        player.x = Math.max(15, Math.min(player.x, canvas.width - 15)); player.y = Math.max(15, Math.min(player.y, canvas.height - 15));
        if (Math.abs(player.vx) > 0.15) player.facingLeft = player.vx < 0;
        player.tiltAngle += ((player.vy * 0.12) - player.tiltAngle) * 0.15;
        player.tailWag++;
        const playerSpeedMag = Math.hypot(player.vx, player.vy);
        draw3DFishMesh(player.x, player.y, player.radius, player.facingLeft, 185, 3, player.tailWag, playerSpeedMag, player.tiltAngle);

        for (let index = marineThreats.length - 1; index >= 0; index--) {
            const t = marineThreats[index];
            stepMarineThreat(t);
            const isTargetEdible = t.radius < player.radius; const dynamicHue = isTargetEdible ? 140 : 0;
            const tSpeedMag = Math.hypot(t.vx, t.vy);
            const tTilt = Math.max(-0.3, Math.min(0.3, t.vy * 0.2));
            draw3DFishMesh(t.x, t.y, t.radius, t.vx < 0, dynamicHue, t.fishType, t.wagPhase, tSpeedMag, tTilt);
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
            if ((t.x > 460 && t.vx > 0) || (t.x < -60 && t.vx < 0)) marineThreats.splice(index, 1);
        }

        ctx.restore();
        animationFrameId = requestAnimationFrame(runGameLoop);
    }
</script>
</body>
</html>
"""

components.html(game_html, height=520, scrolling=False)
