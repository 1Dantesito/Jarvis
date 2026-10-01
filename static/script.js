// =========================================================================
// JARVIS v3.0 — Continuous Hands-Free Engine, Real Voice & WebSockets
// =========================================================================

// --- ANIMUS LOADING VOID & NEURAL 3D PERSPECTIVE ENGINE (AC Black Flag Aesthetic) ---
function initBobaCanvas() {
    const canvas = document.getElementById('boba-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    // 64 Partículas flotantes de bruma cibernética Animus Void
    const particles = [];
    const PARTICLE_COUNT = 64;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            size: Math.random() * 2.2 + 0.8,
            speedY: Math.random() * 0.45 + 0.15,
            swaySpeed: Math.random() * 0.02 + 0.008,
            swayDistance: Math.random() * 32 + 10,
            seed: Math.random() * 100,
            baseAlpha: Math.random() * 0.45 + 0.15,
            isDiamond: Math.random() > 0.75,
            rotation: Math.random() * Math.PI,
            rotSpeed: (Math.random() - 0.5) * 0.03
        });
    }

    let time = 0;

    function animate() {
        ctx.clearRect(0, 0, width, height);
        time += 0.02;

        const horizonY = height * 0.63;
        const centerX = width * 0.5;

        // 1. Abismo y Atmósfera del Animus Void (Cian Profundo / Cyber Ocean)
        const skyGrad = ctx.createLinearGradient(0, 0, 0, horizonY);
        skyGrad.addColorStop(0, '#02050A');
        skyGrad.addColorStop(0.65, '#030C16');
        skyGrad.addColorStop(1, '#051A2C');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, width, horizonY);

        const floorGrad = ctx.createLinearGradient(0, horizonY, 0, height);
        floorGrad.addColorStop(0, '#051A2C');
        floorGrad.addColorStop(0.3, '#020C17');
        floorGrad.addColorStop(1, '#010408');
        ctx.fillStyle = floorGrad;
        ctx.fillRect(0, horizonY, width, height - horizonY);

        // 2. Resplandor Difuso y Línea de Horizonte Especular
        const horizonGlow = ctx.createLinearGradient(0, horizonY - 45, 0, horizonY + 45);
        horizonGlow.addColorStop(0, 'rgba(0, 242, 254, 0)');
        horizonGlow.addColorStop(0.5, 'rgba(0, 242, 254, 0.16)');
        horizonGlow.addColorStop(1, 'rgba(0, 242, 254, 0)');
        ctx.fillStyle = horizonGlow;
        ctx.fillRect(0, horizonY - 45, width, 90);

        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        ctx.lineTo(width, horizonY);
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.45)';
        ctx.lineWidth = 1;
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(0, 242, 254, 0.75)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        // 3. Rejilla de Perspectiva 3D Animus (Suelo del Vacío)
        const voiceState = (typeof window.currentVoiceState !== 'undefined') ? window.currentVoiceState : "IDLE";
        const isSpeaking = voiceState === "SPEAKING";
        const isListening = voiceState === "LISTENING";

        // Líneas de perspectiva en fuga hacia el centro del horizonte
        ctx.lineWidth = 0.75;
        const lineCount = 18;
        for (let i = -lineCount; i <= lineCount; i++) {
            const spreadX = centerX + i * (width / (lineCount * 0.85));
            ctx.beginPath();
            ctx.moveTo(centerX, horizonY);
            ctx.lineTo(spreadX, height);
            const lineAlpha = Math.max(0, 0.11 - Math.abs(i) * 0.005);
            ctx.strokeStyle = `rgba(0, 242, 254, ${lineAlpha})`;
            ctx.stroke();
        }

        // Líneas horizontales de profundidad en perspectiva
        for (let d = 1; d <= 8; d++) {
            const progress = Math.pow(d / 8, 2.3);
            const lineY = horizonY + progress * (height - horizonY);
            const hAlpha = progress * 0.12;
            ctx.beginPath();
            ctx.moveTo(0, lineY);
            ctx.lineTo(width, lineY);
            ctx.strokeStyle = `rgba(0, 242, 254, ${hAlpha})`;
            ctx.stroke();
        }

        // 4. Membrana Neuronal Ondulante Reactiva a la Voz de JARVIS
        const waveAmp = isSpeaking ? 16 : (isListening ? 9 : 3.5);
        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        for (let x = 0; x <= width; x += 20) {
            const wave = Math.sin(x * 0.007 + time * 1.8) * waveAmp + Math.cos(x * 0.015 - time * 1.1) * (waveAmp * 0.6);
            ctx.lineTo(x, horizonY + wave);
        }
        ctx.strokeStyle = isSpeaking ? 'rgba(0, 242, 254, 0.7)' : 'rgba(0, 242, 254, 0.22)';
        ctx.lineWidth = isSpeaking ? 2 : 1;
        ctx.shadowBlur = isSpeaking ? 14 : 6;
        ctx.shadowColor = 'rgba(0, 242, 254, 0.7)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        // 5. Partículas de Bruma y Motes de Datos Animus (Ember Motes)
        for (const p of particles) {
            p.y -= p.speedY * (isSpeaking ? 1.3 : 1.0);
            p.rotation += p.rotSpeed;
            if (p.y < -15) {
                p.y = height + 15;
                p.x = Math.random() * width;
            }
            const currentX = p.x + Math.sin(time * p.swaySpeed + p.seed) * p.swayDistance;
            const alpha = p.baseAlpha * (0.8 + 0.25 * Math.sin(time * 1.5 + p.seed));

            ctx.save();
            ctx.translate(currentX, p.y);
            ctx.shadowBlur = isSpeaking ? 12 : 8;
            ctx.shadowColor = 'rgba(0, 242, 254, 0.6)';

            if (p.isDiamond) {
                ctx.rotate(p.rotation);
                ctx.fillStyle = `rgba(56, 225, 255, ${alpha * 0.9})`;
                ctx.fillRect(-p.size, -p.size, p.size * 2, p.size * 2);
            } else {
                ctx.beginPath();
                ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0, 242, 254, ${alpha})`;
                ctx.fill();
            }
            ctx.restore();
        }

        requestAnimationFrame(animate);
    }
    animate();
}

// --- ACTIVATION CHIME (Web Audio API) ---
let audioCtx = null;
function playActivationChime() {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, now);
        osc.frequency.exponentialRampToValueAtTime(880.00, now + 0.10);
        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.22);
    } catch (e) {
        console.debug("[Chime] AudioContext no inicializado:", e);
    }
}

// --- YOUTUBE CLIENT-SIDE REAL PLAYBACK ENGINE ---
let ytPlayer = null;
let isPlayerReady = false;
let progressInterval = null;

// Lista de reproducción global (inicia 100% vacía)
window.playlistData = [];
window.currentTrackIdx = 0;
window.isStudioPlaying = false;

function initializeYouTubePlayer() {
    if (ytPlayer || typeof YT === 'undefined' || !YT.Player) return;
    try {
        ytPlayer = new YT.Player('ytplayer', {
            height: '100%',
            width: '100%',
            videoId: '',
            playerVars: {
                'autoplay': 1,
                'controls': 0,
                'disablekb': 1,
                'enablejsapi': 1,
                'origin': window.location.origin
            },
            events: {
                'onReady': () => {
                    isPlayerReady = true;
                    console.log("[YouTube Player] Listo.");
                },
                'onStateChange': onPlayerStateChange,
                'onError': onPlayerError
            }
        });
    } catch (e) {
        console.warn("[YouTube Player] Error inicializando:", e);
    }
}
window.onYouTubeIframeAPIReady = () => initializeYouTubePlayer();

function onPlayerStateChange(event) {
    const playPauseBtn = document.getElementById('btn-playpause');
    const studioPlayPauseBtn = document.getElementById('studio-btn-playpause');
    const miniPlayer = document.getElementById('mini-player');
    const studioModal = document.getElementById('music-studio-modal');

    if (event.data === YT.PlayerState.PLAYING) {
        window.isStudioPlaying = true;
        if (playPauseBtn) playPauseBtn.textContent = '⏸';
        if (studioPlayPauseBtn) studioPlayPauseBtn.textContent = '⏸';
        if (miniPlayer) {
            miniPlayer.style.display = 'flex';
            miniPlayer.classList.add('playing');
        }
        if (studioModal) studioModal.classList.add('playing');
        
        try {
            if (ytPlayer && typeof ytPlayer.getVideoData === 'function') {
                const vData = ytPlayer.getVideoData();
                if (vData && vData.title) {
                    const playerTrackTitle = document.getElementById('player-track-title');
                    const playerTrackArtist = document.getElementById('player-track-artist');
                    const studioTitle = document.getElementById('studio-main-title');
                    const studioArtist = document.getElementById('studio-main-artist');
                    if (playerTrackTitle) playerTrackTitle.textContent = vData.title;
                    if (playerTrackArtist && vData.author) playerTrackArtist.textContent = vData.author;
                    if (studioTitle) studioTitle.textContent = vData.title;
                    if (studioArtist && vData.author) studioArtist.textContent = vData.author;
                }
            }
        } catch (e) {
            console.debug("[YouTube Player] Error leyendo videoData:", e);
        }

        startProgressTracking();
        if (typeof window.renderMusicStudioPlaylist === 'function') {
            window.renderMusicStudioPlaylist();
        }
    } else if (event.data === YT.PlayerState.PAUSED) {
        window.isStudioPlaying = false;
        if (playPauseBtn) playPauseBtn.textContent = '▶';
        if (studioPlayPauseBtn) studioPlayPauseBtn.textContent = '▶';
        if (miniPlayer) miniPlayer.classList.remove('playing');
        if (studioModal) studioModal.classList.remove('playing');
        stopProgressTracking();
        if (typeof window.renderMusicStudioPlaylist === 'function') {
            window.renderMusicStudioPlaylist();
        }
    } else if (event.data === YT.PlayerState.ENDED) {
        window.isStudioPlaying = false;
        if (playPauseBtn) playPauseBtn.textContent = '▶';
        if (studioPlayPauseBtn) studioPlayPauseBtn.textContent = '▶';
        if (miniPlayer) miniPlayer.classList.remove('playing');
        if (studioModal) studioModal.classList.remove('playing');
        stopProgressTracking();
        playNextTrackInQueue();
    }
}

function onPlayerError(event) {
    console.warn("[YouTube Player] Error en reproducción:", event.data);
    playNextTrackInQueue();
}

function startProgressTracking() {
    stopProgressTracking();
    const bar = document.getElementById('player-progress-bar');
    const studioFill = document.getElementById('studio-progress-fill');
    const timeCur = document.getElementById('studio-time-current');
    const timeTot = document.getElementById('studio-time-total');

    progressInterval = setInterval(() => {
        if (isPlayerReady && ytPlayer && typeof ytPlayer.getCurrentTime === 'function' && typeof ytPlayer.getDuration === 'function') {
            const current = ytPlayer.getCurrentTime();
            const duration = ytPlayer.getDuration();
            if (duration > 0) {
                const pct = Math.min(100, Math.max(0, (current / duration) * 100));
                if (bar) bar.style.width = `${pct}%`;
                if (studioFill) studioFill.style.width = `${pct}%`;
                
                if (timeCur) {
                    const m = Math.floor(current / 60);
                    const s = Math.floor(current % 60);
                    timeCur.textContent = `${m}:${s < 10 ? '0' : ''}${s}`;
                }
                if (timeTot) {
                    const mTot = Math.floor(duration / 60);
                    const sTot = Math.floor(duration % 60);
                    timeTot.textContent = `${mTot}:${sTot < 10 ? '0' : ''}${sTot}`;
                }

                // Sincronización inteligente de letras estilo Spotify
                if (typeof syncLyricsWithTime === 'function') {
                    syncLyricsWithTime(current);
                }
            }
        }
    }, 250);
}

function stopProgressTracking() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function startTrackPlayback(videoId, title, artist) {
    const miniPlayer = document.getElementById('mini-player');
    const playerTrackTitle = document.getElementById('player-track-title');
    const playerTrackArtist = document.getElementById('player-track-artist');
    const studioTitle = document.getElementById('studio-main-title');
    const studioArtist = document.getElementById('studio-main-artist');

    if (miniPlayer) miniPlayer.style.display = 'flex';
    if (playerTrackTitle) playerTrackTitle.textContent = title || 'Reproduciendo';
    if (playerTrackArtist) playerTrackArtist.textContent = artist || 'Música';
    if (studioTitle) studioTitle.textContent = title || 'Reproduciendo';
    if (studioArtist) studioArtist.textContent = artist || 'Música';

    // Activar color dinámico de la canción y carga de letra sincronizada
    if (typeof applyDynamicSongColor === 'function') {
        applyDynamicSongColor(title, artist);
    }
    if (typeof fetchAndRenderLyrics === 'function') {
        fetchAndRenderLyrics(title, artist);
    }

    if (videoId) {
        if (isPlayerReady && ytPlayer && typeof ytPlayer.loadVideoById === 'function') {
            try {
                ytPlayer.loadVideoById(videoId);
                ytPlayer.playVideo();
            } catch (err) {
                console.warn("[YouTube Player] Error en loadVideoById:", err);
            }
        }
    }
}

function playNextTrackInQueue(data) {
    if (data && data.next_track) {
        const nt = data.next_track;
        if (typeof window.addTrackToStudioQueue === 'function') {
            window.addTrackToStudioQueue(nt.title, nt.artist, nt.id);
        }
        return;
    }
    if (window.playlistData && window.playlistData.length > 0) {
        window.currentTrackIdx = (window.currentTrackIdx + 1) % window.playlistData.length;
        if (typeof window.playTrackFromStudio === 'function') {
            window.playTrackFromStudio(window.currentTrackIdx);
        }
    }
}

// --- AUTO FOCUS SEGURO ---
function autoFocusInput() {
    try {
        const input = document.getElementById('user-input');
        if (input) {
            setTimeout(() => input.focus(), 60);
        }
    } catch (e) {
        console.debug("[AutoFocus] Error:", e);
    }
}

// =========================================================================
// MAIN DOM CONTENT LOADED
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initBobaCanvas();
    initializeYouTubePlayer();
    autoFocusInput();

    // --- COLA DE AUDIO TTS EN STREAMING CON PRECARGA FLUIDA SIN PAUSAS ---
    let currentTTSAudio = null;
    const ttsAudioQueue = [];
    let isPlayingTTSQueue = false;

    function enqueueTTSUrl(url) {
        if (!url || !uiState.soundEnabled || uiState.voiceState === "INTERRUPTED") return;
        
        const audio = new Audio(url);
        audio.preload = 'auto';
        // Iniciar precarga inmediata por red para eliminar latencia entre oraciones
        try {
            audio.load();
        } catch (e) {}

        ttsAudioQueue.push(audio);

        if (!isPlayingTTSQueue) {
            playNextTTSChunk();
        }
    }

    function playNextTTSChunk() {
        if (!uiState.soundEnabled || uiState.voiceState === "INTERRUPTED") {
            clearTTSAudioQueue();
            return;
        }
        if (ttsAudioQueue.length === 0) {
            isPlayingTTSQueue = false;
            currentTTSAudio = null;
            return;
        }

        isPlayingTTSQueue = true;
        const nextAudio = ttsAudioQueue.shift();
        currentTTSAudio = nextAudio;

        currentTTSAudio.onended = () => {
            playNextTTSChunk();
        };

        currentTTSAudio.onerror = (e) => {
            console.warn("[TTS Chunk Error]", e);
            playNextTTSChunk();
        };

        currentTTSAudio.play().catch(e => {
            console.warn("[TTS Play Error]", e);
            playNextTTSChunk();
        });
    }

    function clearTTSAudioQueue() {
        ttsAudioQueue.forEach(audio => {
            try {
                audio.pause();
                audio.src = '';
                audio.load();
            } catch (e) {}
        });
        ttsAudioQueue.length = 0;
        isPlayingTTSQueue = false;
        if (currentTTSAudio) {
            try {
                currentTTSAudio.pause();
                currentTTSAudio.src = '';
                currentTTSAudio.load();
            } catch (e) {}
            currentTTSAudio = null;
        }
    }

    const jarvisOrb = document.getElementById('jarvis-orb');
    const voiceStatusText = document.getElementById('voice-status-text');
    const handsfreeHint = document.getElementById('handsfree-hint');
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const micBtn = document.getElementById('mic-btn');
    const messagesList = document.getElementById('messages-list');
    const chatBody = document.getElementById('chat-body');
    const welcomeScreen = document.getElementById('welcome-screen');
    const btnPlayPause = document.getElementById('btn-playpause');
    const btnNext = document.getElementById('btn-next');
    const btnToggleDrawer = document.getElementById('btn-toggle-drawer');
    const btnCloseDrawer = document.getElementById('btn-close-drawer');
    const contextDrawer = document.getElementById('context-drawer');

    const uiState = {
        voiceState: "IDLE",
        isWaitingResponse: false,
        soundEnabled: true,
        generationId: 0,
        activeAssistantBubble: null,
        activeAssistantItem: null,
        isDrawerOpen: false
    };

    let isSpeechActive = false;
    let isConversationActive = false;
    let continuousEnabled = true;
    const WAKE_WORD_REGEX = /(?:oye|hola|hey|ok|bueno)?\s*,?\s*(?:jarvis|jarbis|yarvis|llarvis|harvis|chavis|yervis|aura|awra|laura)\b/i;

    function formatAssistantMessage(text) {
        if (!text) return "";
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
        return formatted;
    }

    function setVoiceState(state, customText) {
        uiState.voiceState = state;
        window.currentVoiceState = state;
        if (!jarvisOrb) return;
        jarvisOrb.classList.remove('idle', 'listening', 'thinking', 'processing', 'speaking', 'error');

        switch (state) {
            case "LISTENING":
                jarvisOrb.classList.add('listening');
                jarvisOrb.setAttribute('aria-label', 'JARVIS escuchando tu voz...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Escuchando...";
                if (handsfreeHint) handsfreeHint.textContent = "Micrófono Abierto";
                if (micBtn) micBtn.classList.add('listening');
                break;
            case "PROCESSING":
                jarvisOrb.classList.add('thinking');
                jarvisOrb.setAttribute('aria-label', 'JARVIS procesando respuesta...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Procesando...";
                if (handsfreeHint) handsfreeHint.textContent = "Consultando Red Neuronal...";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "SPEAKING":
                jarvisOrb.classList.add('speaking');
                jarvisOrb.setAttribute('aria-label', 'JARVIS respondiendo con voz...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Hablando...";
                if (handsfreeHint) handsfreeHint.textContent = "Audio Activo";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "ERROR":
                jarvisOrb.classList.add('error');
                jarvisOrb.setAttribute('aria-label', 'JARVIS ha encontrado un error. Haz clic para reintentar.');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Error";
                if (handsfreeHint) handsfreeHint.textContent = "Atención Requerida";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "IDLE":
            default:
                jarvisOrb.classList.add('idle');
                jarvisOrb.setAttribute('aria-label', 'JARVIS en reposo. Haz clic o di Jarvis para interactuar.');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Listo (escuchando 'Jarvis'...)";
                if (handsfreeHint) handsfreeHint.textContent = "Manos Libres Activo";
                if (micBtn) micBtn.classList.remove('listening');
                break;
        }
    }

    // --- WEBSOCKET CONNECTION CON BACKOFF EXPONENCIAL Y HEARTBEAT (A.1, A.2) ---
    let ws = null;
    let wsRetryCount = 0;
    let wsPingInterval = null;
    let wsPongTimeout = null;

    function getWsUrl() {
        const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        let deviceId = localStorage.getItem('jarvis_device_id');
        if (!deviceId) {
            deviceId = 'dev_' + Math.random().toString(36).substring(2, 12);
            localStorage.setItem('jarvis_device_id', deviceId);
        }
        const sessionId = localStorage.getItem('jarvis_session_id') || '';
        return `${wsProto}//${host}/ws/v1/chat?session_id=${encodeURIComponent(sessionId)}&device_id=${encodeURIComponent(deviceId)}`;
    }

    function connectWebSocket() {
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        const url = getWsUrl();
        console.log(`[Jarvis WS] Conectando (intento #${wsRetryCount + 1})...`);

        try {
            ws = new WebSocket(url);

            ws.onopen = () => {
                console.log("[Jarvis WS] Conectado al pipeline de voz.");
                wsRetryCount = 0;
                startWsHeartbeat();
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === "pong") {
                        if (wsPongTimeout) {
                            clearTimeout(wsPongTimeout);
                            wsPongTimeout = null;
                        }
                        return;
                    }
                    if (data.type === "sync_state" && data.session_id) {
                        localStorage.setItem('jarvis_session_id', data.session_id);
                    }
                    handleServerEvent(data);
                } catch (e) {
                    console.warn("[Jarvis WS] Error parseando mensaje:", e);
                }
            };

            ws.onclose = () => {
                stopWsHeartbeat();
                const exponentialDelay = Math.min(1000 * Math.pow(2, Math.min(wsRetryCount, 5)), 30000);
                const jitter = Math.floor(Math.random() * 300);
                const delay = exponentialDelay + jitter;
                wsRetryCount++;
                console.warn(`[Jarvis WS] Conexión perdida. Reconectando en ${delay}ms...`);
                setTimeout(connectWebSocket, delay);
            };

            ws.onerror = (err) => {
                console.debug("[Jarvis WS] Evento onerror:", err);
            };

        } catch (e) {
            console.error("[Jarvis WS] Error iniciando conexión:", e);
            setTimeout(connectWebSocket, 3000);
        }
    }

    function startWsHeartbeat() {
        stopWsHeartbeat();
        wsPingInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ping", timestamp: Date.now() }));
                wsPongTimeout = setTimeout(() => {
                    console.warn("[Jarvis WS] Heartbeat timeout: Pong no recibido en 5s. Reconectando...");
                    if (ws) ws.close();
                }, 5000);
            }
        }, 15000);
    }

    function stopWsHeartbeat() {
        if (wsPingInterval) clearInterval(wsPingInterval);
        if (wsPongTimeout) clearTimeout(wsPongTimeout);
        wsPingInterval = null;
        wsPongTimeout = null;
    }

    connectWebSocket();

    function handleServerEvent(event) {
        if (event.type === "state_change") {
            if (event.generation_id !== undefined) {
                uiState.generationId = Math.max(uiState.generationId, event.generation_id);
            }
            setVoiceState(event.state);
        } 
        else if (event.type === "token") {
            if (event.generation_id === undefined || event.generation_id === uiState.generationId) {
                if (uiState.voiceState !== "INTERRUPTED") {
                    ensureAssistantBubble();
                    if (uiState.activeAssistantBubble) {
                        uiState.activeAssistantBubble.dataset.streamedTokens = "true";
                        if (!uiState.activeAssistantBubble.dataset.rawText) {
                            uiState.activeAssistantBubble.dataset.rawText = "";
                        }
                        uiState.activeAssistantBubble.dataset.rawText += event.token || "";
                        uiState.activeAssistantBubble.innerHTML = formatAssistantMessage(uiState.activeAssistantBubble.dataset.rawText);
                        scrollToBottom();
                    }
                }
            }
        }
        else if (event.type === "tts_chunk") {
            if (event.generation_id === undefined || event.generation_id === uiState.generationId) {
                if (uiState.voiceState !== "INTERRUPTED") {
                    // Encolar y reproducir audio TTS de esta oración completada inmediatamente
                    if (event.audio_url && uiState.soundEnabled) {
                        enqueueTTSUrl(event.audio_url);
                    }

                    ensureAssistantBubble();
                    if (uiState.activeAssistantBubble && !uiState.activeAssistantBubble.dataset.streamedTokens) {
                        if (!uiState.activeAssistantBubble.dataset.rawText) {
                            uiState.activeAssistantBubble.dataset.rawText = "";
                        }
                        uiState.activeAssistantBubble.dataset.rawText += (uiState.activeAssistantBubble.dataset.rawText ? " " : "") + event.text;
                        uiState.activeAssistantBubble.innerHTML = formatAssistantMessage(uiState.activeAssistantBubble.dataset.rawText);
                        scrollToBottom();
                    }
                }
            }
        } 
        else if (event.type === "tool_executed") {
            ensureAssistantBubble();
            const toolName = event.tool_name;
            if (["open_application", "play_music", "pause_music", "resume_music", "create_reminder", "remember_info", "forget_memory", "create_text_file"].includes(toolName)) {
                if (uiState.activeAssistantItem) {
                    appendActionBadge(uiState.activeAssistantItem, toolName, "Acción completada");
                }
            }
        } 
        else if (event.type === "player_control") {
            if (event.action === "pause") {
                if (isPlayerReady && ytPlayer && typeof ytPlayer.pauseVideo === 'function') ytPlayer.pauseVideo();
            } else if (event.action === "play") {
                if (isPlayerReady && ytPlayer && typeof ytPlayer.playVideo === 'function') ytPlayer.playVideo();
            } else if (event.action === "next") {
                playNextTrackInQueue(event.data);
            } else if (event.action === "play_track" && event.data) {
                const tr = event.data.current_track;
                const tracks = event.data.tracks || [];
                if (tracks.length > 0) {
                    window.loadPlaylistFromBackend(tracks);
                } else if (tr) {
                    window.addTrackToStudioQueue(tr.title, tr.artist, tr.id);
                }
            } else if (event.action === "clear_queue") {
                // La IA ejecutó clear_music_queue: vaciar lista y detener reproducción
                window.playlistData = [];
                window.currentTrackIdx = 0;
                window.isStudioPlaying = false;
                if (isPlayerReady && ytPlayer && typeof ytPlayer.stopVideo === 'function') ytPlayer.stopVideo();
                window.renderMusicStudioPlaylist();
            }
        }
        else if (event.type === "response_end" || event.type === "complete") {
            uiState.isWaitingResponse = false;
            if (uiState.voiceState !== "INTERRUPTED") {
                if (uiState.activeAssistantBubble && event.full_text) {
                    uiState.activeAssistantBubble.innerHTML = formatAssistantMessage(event.full_text);
                }
                
                if (uiState.activeAssistantItem && (event.generated_image || event.generated_doc)) {
                    appendMediaAssets(uiState.activeAssistantItem, event.generated_image, event.generated_doc);
                }

                if (uiState.activeAssistantItem && !uiState.activeAssistantItem.querySelector('.msg-utility-actions')) {
                    const utils = document.createElement('div');
                    utils.className = 'msg-utility-actions';
                    const fullText = event.full_text || '';
                    utils.innerHTML = `
                        <button class="msg-util-btn btn-read-aloud" title="Leer en voz alta">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                            </svg>
                            <span>Voz</span>
                        </button>
                        <button class="msg-util-btn btn-copy-msg" title="Copiar respuesta">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                            <span>Copiar</span>
                        </button>
                        <button class="msg-util-btn btn-like-msg" title="Guardar como preferencia">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                        </button>
                    `;
                    const readBtn = utils.querySelector('.btn-read-aloud');
                    if (readBtn) {
                        readBtn.addEventListener('click', () => {
                            clearTTSAudioQueue();
                            if (!fullText) return;
                            const sentences = fullText.match(/[^.!?\n]+[.!?\n]+|[^.!?\n]+$/g) || [fullText];
                            for (const s of sentences) {
                                const clean = s.trim();
                                if (clean.length > 0) {
                                    enqueueTTSUrl(`/api/tts/stream?text=${encodeURIComponent(clean)}`);
                                }
                            }
                        });
                    }
                    const copyBtn = utils.querySelector('.btn-copy-msg');
                    if (copyBtn) {
                        copyBtn.addEventListener('click', () => {
                            navigator.clipboard.writeText(fullText);
                            copyBtn.innerHTML = `
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                                <span>Copiado</span>
                            `;
                            setTimeout(() => {
                                copyBtn.innerHTML = `
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                    <span>Copiar</span>
                                `;
                            }, 2000);
                        });
                    }
                    const likeBtn = utils.querySelector('.btn-like-msg');
                    if (likeBtn) {
                        likeBtn.addEventListener('click', () => {
                            likeBtn.classList.toggle('liked');
                        });
                    }
                    uiState.activeAssistantItem.appendChild(utils);
                }

                scrollToBottom();

                // Reproducir audio acumulado de respaldo únicamente si no hubo oraciones encoladas previamente
                if (!isPlayingTTSQueue && ttsAudioQueue.length === 0 && event.audio_url && uiState.soundEnabled) {
                    enqueueTTSUrl(event.audio_url);
                }
                setVoiceState("IDLE", "Listo (escuchando 'Jarvis'...)");
                startContinuousListening(true);
            }
            uiState.activeAssistantBubble = null;
            uiState.activeAssistantItem = null;
            autoFocusInput();
        }
        else if (event.type === "error") {
            uiState.isWaitingResponse = false;
            ensureAssistantBubble();
            if (uiState.activeAssistantBubble) {
                uiState.activeAssistantBubble.textContent = "Error: " + (event.message || "Ocurrió un error al procesar.");
            }
            setVoiceState("ERROR", "Error del servidor");
            uiState.activeAssistantBubble = null;
            uiState.activeAssistantItem = null;
            startContinuousListening(true);
            autoFocusInput();
        }
        else if (event.type === "reminder_alarm") {
            // --- ALARMA DE RECORDATORIO ---
            const title   = event.title   || "Recordatorio";
            const message = event.message || `¡Es hora! ${title}`;
            const priority = (event.priority || "NORMAL").toUpperCase();

            // 1. Burbuja de JARVIS en el chat
            const alarmItem = document.createElement('div');
            alarmItem.className = 'chat-item assistant-item';
            alarmItem.innerHTML = `
                <div class="chat-bubble assistant-bubble reminder-alarm-bubble">
                    <div class="msg-header">
                        <span class="assistant-label" style="display:inline-flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> JARVIS</span>
                        <span class="msg-time">${new Date().toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'})}</span>
                    </div>
                    <div class="msg-content"><span style="display:inline-flex; align-items:center; gap:6px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg> <strong>${title}</strong></span><br>${message}</div>
                </div>`;
            const chatContainer = document.getElementById('chat-messages');
            if (chatContainer) {
                chatContainer.appendChild(alarmItem);
                scrollToBottom();
            }

            // 2. Audio TTS del recordatorio
            if (uiState.soundEnabled) {
                const encoded = encodeURIComponent(message);
                const alarmAudio = new Audio(`/api/tts/stream?text=${encoded}`);
                alarmAudio.play().catch(e => console.log('[ReminderAlarm TTS]', e));
            }

            // 3. Parpadeo visual en el orbe
            const orb = document.getElementById('central-orb') || document.querySelector('.orb-ring');
            if (orb) {
                orb.classList.add('reminder-pulse');
                setTimeout(() => orb.classList.remove('reminder-pulse'), 4000);
            }
        }
    }

    // --- RECONOCIMIENTO DE VOZ WEB SPEECH API ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;

    function initSpeechRecognition() {
        if (!SpeechRecognition) return null;
        try {
            const rec = new SpeechRecognition();
            rec.continuous = true;
            rec.interimResults = true;
            rec.lang = 'es-ES';

            rec.onstart = () => {
                isSpeechActive = true;
            };

            rec.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    const piece = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += piece;
                    } else {
                        interimTranscript += piece;
                    }
                }

                const rawTranscript = (finalTranscript || interimTranscript).trim();

                if (!isConversationActive) {
                    if (WAKE_WORD_REGEX.test(rawTranscript)) {
                        playActivationChime();
                        isConversationActive = true;
                        let cleanCommand = rawTranscript.replace(WAKE_WORD_REGEX, '').trim();
                        setVoiceState("LISTENING", "Te escucho...");
                        if (cleanCommand.length > 2) {
                            handleSendMessage(cleanCommand);
                        }
                    }
                } else {
                    if (finalTranscript.trim().length > 1) {
                        const cleanFinal = finalTranscript.replace(WAKE_WORD_REGEX, '').trim();
                        if (cleanFinal) {
                            handleSendMessage(cleanFinal);
                        }
                    }
                }
            };

            rec.onerror = () => {
                isSpeechActive = false;
            };

            rec.onend = () => {
                isSpeechActive = false;
                if (continuousEnabled) {
                    setTimeout(() => {
                        if (!isSpeechActive && uiState.voiceState !== "PROCESSING" && uiState.voiceState !== "SPEAKING") {
                            startContinuousListening();
                        }
                    }, 100);
                }
            };

            return rec;
        } catch (err) {
            console.error("[SpeechRecognition] Error:", err);
            return null;
        }
    }

    recognition = initSpeechRecognition();

    function startContinuousListening(force = false) {
        if (!continuousEnabled || !SpeechRecognition) return;
        if (!recognition) recognition = initSpeechRecognition();
        if (!recognition) return;

        if (force && isSpeechActive) {
            try { recognition.stop(); } catch (e) {}
            isSpeechActive = false;
        }

        if (!isSpeechActive) {
            try {
                recognition.start();
            } catch (err) {
                if (err.name === 'InvalidStateError') isSpeechActive = true;
            }
        }
    }

    startContinuousListening();

    // --- ENVIAR MENSAJE ---
    function ensureAssistantBubble() {
        if (!uiState.activeAssistantBubble) {
            const item = document.createElement('div');
            item.classList.add('message-item', 'jarvis');
            
            const bubble = document.createElement('div');
            bubble.classList.add('bubble');
            const timeStr = getCurrentTimeStr();
            bubble.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-family:'Outfit',sans-serif; font-size:11px; font-weight:800; color:var(--accent-secondary); letter-spacing:0.8px; display:inline-flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> JARVIS</span>
                    <span style="font-size:10px; color:var(--text-muted); opacity:0.8;">${timeStr}</span>
                </div>
                <div class="msg-content">Pensando...</div>
            `;
            item.appendChild(bubble);
            messagesList.appendChild(item);

            uiState.activeAssistantItem = item;
            uiState.activeAssistantBubble = bubble.querySelector('.msg-content') || bubble;
        }
    }

    // --- ADJUNTOS MULTIMODALES Y DOCUMENTOS (PDF, DOCX, TXT, IMÁGENES) ---
    let currentAttachment = null;

    function formatFileSize(bytes) {
        if (!bytes || bytes <= 0) return '0 B';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function showAttachmentPreview(attach) {
        const previewCont = document.getElementById('attachment-preview-container');
        const previewImg = document.getElementById('attachment-preview-img');
        const iconSpan = document.getElementById('attachment-icon');
        const nameText = document.getElementById('attachment-name-text');
        if (!previewCont) return;

        if (attach.type === 'image') {
            if (previewImg) {
                previewImg.src = attach.preview;
                previewImg.style.display = 'block';
            }
            if (iconSpan) iconSpan.style.display = 'none';
            if (nameText) nameText.textContent = attach.name ? `Imagen: ${attach.name}` : 'Imagen adjunta';
        } else {
            if (previewImg) {
                previewImg.src = '';
                previewImg.style.display = 'none';
            }
            if (iconSpan) {
                iconSpan.textContent = attach.file_type === 'pdf' ? '📄' : (attach.file_type === 'docx' ? '📝' : '📑');
                iconSpan.style.display = 'inline-block';
            }
            const sizeStr = attach.size_bytes ? ` (${formatFileSize(attach.size_bytes)})` : '';
            if (nameText) nameText.textContent = `${attach.name}${sizeStr}`;
        }
        previewCont.style.display = 'flex';
    }

    function clearAttachment() {
        currentAttachment = null;
        const previewCont = document.getElementById('attachment-preview-container');
        const previewImg = document.getElementById('attachment-preview-img');
        const iconSpan = document.getElementById('attachment-icon');
        const fileInput = document.getElementById('image-file-input');
        if (previewCont) previewCont.style.display = 'none';
        if (previewImg) { previewImg.src = ''; previewImg.style.display = 'none'; }
        if (iconSpan) iconSpan.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (userInput) {
            userInput.placeholder = "Siempre escuchando... Di 'Jarvis' o escribe aquí...";
        }
    }

    async function processAttachedFile(file) {
        if (!file) return;
        const isImgType = file.type && file.type.startsWith('image/');
        const isImgExt = /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(file.name || '');

        if (isImgType || isImgExt) {
            const reader = new FileReader();
            reader.onload = (evt) => {
                const dataUrl = evt.target.result;
                const b64 = dataUrl.split(',')[1];
                currentAttachment = {
                    type: 'image',
                    mime_type: file.type || 'image/png',
                    data: b64,
                    preview: dataUrl,
                    name: file.name || 'imagen_adjunta.png'
                };
                showAttachmentPreview(currentAttachment);
                if (userInput) {
                    if (!userInput.value) {
                        userInput.placeholder = "¿Qué deseas saber sobre esta imagen?";
                    }
                    userInput.focus();
                }
            };
            reader.readAsDataURL(file);
        } else {
            const nameText = document.getElementById('attachment-name-text');
            const previewCont = document.getElementById('attachment-preview-container');
            if (previewCont) previewCont.style.display = 'flex';
            if (nameText) nameText.textContent = `⏳ Subiendo y leyendo ${file.name}...`;

            try {
                const formData = new FormData();
                formData.append('file', file);
                const resp = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const resJson = await resp.json();
                const data = (resJson && resJson.ok && resJson.data) ? resJson.data : resJson;
                if (resp.ok && (data.success || resJson.ok)) {
                    currentAttachment = {
                        type: 'document',
                        file_type: data.file_type,
                        name: data.filename,
                        text: data.text,
                        size_bytes: data.size_bytes,
                        char_count: data.char_count
                    };
                    showAttachmentPreview(currentAttachment);
                    if (userInput) {
                        if (!userInput.value) {
                            userInput.placeholder = `Pregunta sobre ${file.name} (ej. "Resúmelo" o "¿De qué trata?")`;
                        }
                        userInput.focus();
                    }
                } else {
                    alert(data.error || 'No se pudo leer el archivo.');
                    clearAttachment();
                }
            } catch (err) {
                console.error('[Upload error]', err);
                alert('Error al subir el archivo para análisis.');
                clearAttachment();
            }
        }
    }

    function handlePasteEvent(e) {
        const clipboard = e.clipboardData || window.clipboardData;
        if (!clipboard) return;

        // 1. Archivos directos en portapapeles
        if (clipboard.files && clipboard.files.length > 0) {
            for (let f of clipboard.files) {
                e.preventDefault();
                processAttachedFile(f);
                return;
            }
        }

        // 2. Elementos del clipboard
        if (clipboard.items && clipboard.items.length > 0) {
            for (let item of clipboard.items) {
                if (item.kind === 'file') {
                    const f = item.getAsFile();
                    if (f) {
                        e.preventDefault();
                        processAttachedFile(f);
                        return;
                    }
                }
            }
        }
    }

    // Escuchar Ctrl+V tanto a nivel de ventana como en el input
    window.addEventListener('paste', handlePasteEvent);
    if (userInput) {
        userInput.addEventListener('paste', handlePasteEvent);
    }

    // Soporte para Arrastrar y Soltar (Drag & Drop)
    window.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    window.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
            processAttachedFile(files[0]);
        }
    });

    // Botón físico para adjuntar archivo
    const attachImgBtn = document.getElementById('attach-img-btn');
    const imageFileInput = document.getElementById('image-file-input');
    if (attachImgBtn && imageFileInput) {
        attachImgBtn.addEventListener('click', () => {
            imageFileInput.click();
        });
        imageFileInput.addEventListener('change', () => {
            if (imageFileInput.files && imageFileInput.files[0]) {
                processAttachedFile(imageFileInput.files[0]);
            }
        });
    }

    const removeAttachBtn = document.getElementById('attachment-remove-btn');
    if (removeAttachBtn) {
        removeAttachBtn.addEventListener('click', clearAttachment);
    }

    function appendMediaAssets(parentItem, generatedImage, generatedDoc) {
        if (!parentItem) return;
        if (generatedImage && !parentItem.querySelector('.generated-image-card')) {
            const imgCard = document.createElement('div');
            imgCard.className = 'generated-image-card';
            imgCard.innerHTML = `
                <img src="${generatedImage}" alt="Imagen generada por JARVIS">
                <div class="generated-image-footer">
                    <span>✨ Generada con IA</span>
                    <span style="opacity:0.8;">Guardada en Imágenes</span>
                </div>
            `;
            parentItem.appendChild(imgCard);
            scrollToBottom();
        }
        if (generatedDoc && !parentItem.querySelector('.generated-doc-card')) {
            const docCard = document.createElement('div');
            docCard.className = 'generated-doc-card';
            const icon = (generatedDoc.format === 'DOCX') ? '📝' : '📄';
            docCard.innerHTML = `
                <div class="generated-doc-icon">${icon}</div>
                <div class="generated-doc-info">
                    <span class="generated-doc-title">${generatedDoc.file_name}</span>
                    <span class="generated-doc-meta">${generatedDoc.format} • ${generatedDoc.standard || 'APA'} • Guardado con éxito</span>
                </div>
            `;
            parentItem.appendChild(docCard);
            scrollToBottom();
        }
    }

    async function handleSendMessage(customText) {
        const text = (customText || userInput.value).trim();
        const attachmentToSend = currentAttachment;
        if (!text && !attachmentToSend) return;

        let promptText = text;
        if (attachmentToSend && attachmentToSend.type === 'document') {
            const docHeader = `[DOCUMENTO ADJUNTO: "${attachmentToSend.name}"]\n${attachmentToSend.text}\n[FIN DEL DOCUMENTO]\n\n`;
            promptText = docHeader + (text || "¿Qué contiene este documento? Resúmelo y destaca los puntos clave.");
        } else if (!text && attachmentToSend && attachmentToSend.type === 'image') {
            promptText = "Analiza esta imagen adjunta y descríbela en detalle";
        }

        if (welcomeScreen) welcomeScreen.style.display = 'none';

        clearTTSAudioQueue();

        appendMessage('user', text || (attachmentToSend?.type === 'document' ? `Consulta sobre ${attachmentToSend.name}` : 'Imagen adjunta'), attachmentToSend);
        userInput.value = '';
        clearAttachment();
        autoFocusInput();

        uiState.isWaitingResponse = true;
        setVoiceState("PROCESSING");

        ensureAssistantBubble();
        scrollToBottom();

        // Enviar por WebSocket si está conectado
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: "user_text",
                text: promptText,
                image: attachmentToSend ? { mime_type: attachmentToSend.mime_type, data: attachmentToSend.data } : null
            }));
        } else {
            // Fallback HTTP directo
            try {
                let did = localStorage.getItem('jarvis_device_id');
                if (!did) {
                    did = 'dev_' + Math.random().toString(36).substring(2, 12);
                    localStorage.setItem('jarvis_device_id', did);
                }
                let sid = localStorage.getItem('jarvis_session_id') || '';

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: promptText,
                        image: attachmentToSend ? { mime_type: attachmentToSend.mime_type, data: attachmentToSend.data } : null,
                        session_id: sid || undefined,
                        device_id: did
                    })
                });
                const resJson = await response.json();
                const data = (resJson && resJson.ok && resJson.data) ? resJson.data : resJson;
                if (data && data.session_id) {
                    localStorage.setItem('jarvis_session_id', data.session_id);
                }
                if (response.ok && data.text) {
                    if (uiState.activeAssistantBubble) {
                        uiState.activeAssistantBubble.textContent = data.text;
                    }
                    if (uiState.activeAssistantItem && (data.generated_image || data.generated_doc)) {
                        appendMediaAssets(uiState.activeAssistantItem, data.generated_image, data.generated_doc);
                    }
                    if (data.action_type === "music") {
                        if (data.action_detail === "Cola vaciada" || (Array.isArray(data.playlist) && data.playlist.length === 0)) {
                            window.playlistData = [];
                            window.currentTrackIdx = 0;
                            window.isStudioPlaying = false;
                            if (isPlayerReady && ytPlayer && typeof ytPlayer.stopVideo === 'function') ytPlayer.stopVideo();
                            window.renderMusicStudioPlaylist();
                        } else if (data.current_track) {
                            if (data.tracks && data.tracks.length > 0) {
                                window.loadPlaylistFromBackend(data.tracks);
                            } else {
                                window.addTrackToStudioQueue(data.current_track.title, data.current_track.artist, data.current_track.id);
                            }
                        }
                    }
                    if (uiState.soundEnabled && data.audio_url) {
                        enqueueTTSUrl(data.audio_url);
                    }
                } else {
                    if (uiState.activeAssistantBubble) {
                        uiState.activeAssistantBubble.textContent = data.text || "No pude procesar la solicitud.";
                    }
                }
            } catch (err) {
                if (uiState.activeAssistantBubble) {
                    uiState.activeAssistantBubble.textContent = "Error de conexión con el servidor.";
                }
            } finally {
                uiState.isWaitingResponse = false;
                uiState.activeAssistantBubble = null;
                uiState.activeAssistantItem = null;
                setVoiceState("IDLE");
                scrollToBottom();
                autoFocusInput();
            }
        }
    }

    function getCurrentTimeStr() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function appendActionBadge(parentItem, actionType, detail) {
        if (!parentItem) return;
        const card = document.createElement('div');
        card.className = 'chat-action-card';

        if (actionType === "security_confirmation") {
            card.classList.add('confirmation');
            card.innerHTML = `
                <div class="chat-action-card-header">
                    <span class="chat-action-icon">⚠️</span>
                    <div>
                        <div class="chat-action-title">Confirmación Requerida</div>
                        <div class="chat-action-desc">${detail || 'Esta acción requiere tu confirmación para proceder de forma segura.'}</div>
                    </div>
                </div>
                <div class="chat-action-actions">
                    <button type="button" class="chat-action-btn chat-confirm-btn" aria-label="Confirmar y proceder con la acción">Confirmar y Proceder</button>
                    <button type="button" class="chat-action-btn chat-cancel-btn" aria-label="Cancelar acción">Cancelar</button>
                </div>
            `;
            const confirmBtn = card.querySelector('.chat-confirm-btn');
            const cancelBtn = card.querySelector('.chat-cancel-btn');
            if (confirmBtn) {
                confirmBtn.addEventListener('click', () => {
                    card.innerHTML = `
                        <div class="chat-action-card-header">
                            <span class="chat-action-icon">⏳</span>
                            <div class="chat-action-desc">Confirmación enviada. Procediendo...</div>
                        </div>
                    `;
                    handleSendMessage("Sí, confirmo la acción");
                });
            }
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    card.innerHTML = `
                        <div class="chat-action-card-header">
                            <span class="chat-action-icon">🛑</span>
                            <div class="chat-action-desc">Acción cancelada por el usuario.</div>
                        </div>
                    `;
                });
            }
            parentItem.appendChild(card);
            return;
        }

        let icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>`;
        let label = detail || 'Acción completada';
        let btnText = "Ver detalle";
        let btnAction = () => {};

        if (actionType === "play_music") {
            icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>`;
            label = `Reproduciendo música • ${detail || 'Música'}`;
            btnText = "Oír pista";
            btnAction = () => {
                const studioM = document.getElementById('music-studio-modal');
                if (studioM) studioM.style.display = 'flex';
            };
        } else if (actionType === "remember_info" || actionType === "forget_memory") {
            icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/><line x1="9" y1="21" x2="15" y2="21"/></svg>`;
            label = `Memoria • ${detail || 'Preferencias guardadas'}`;
            btnText = "Ver memoria";
            btnAction = () => {
                const btnMem = document.getElementById('btn-open-memory');
                if (btnMem) btnMem.click();
            };
        }

        card.innerHTML = `
            <div class="chat-action-card-header">
                <span class="chat-action-icon">${icon}</span>
                <span class="chat-action-label">${label}</span>
            </div>
            <div class="chat-action-actions">
                <button type="button" class="chat-action-btn">${btnText}</button>
            </div>
        `;

        const actionBtn = card.querySelector('.chat-action-btn');
        if (actionBtn) actionBtn.addEventListener('click', btnAction);

        parentItem.appendChild(card);
    }

    function appendMessage(sender, text, attachment) {
        const item = document.createElement('div');
        item.classList.add('message-item', sender);
        
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        const timeStr = getCurrentTimeStr();
        
        if (sender === 'jarvis') {
            bubble.innerHTML = `
                <div class="msg-header">
                    <span class="msg-sender-tag">
                        <span class="pulse-indicator"></span>
                        <span class="sender-name">JARVIS AI</span>
                    </span>
                    <span class="msg-time-tag">${timeStr}</span>
                </div>
                <div class="msg-content">${formatAssistantMessage(text)}</div>
            `;
            item.appendChild(bubble);
        } else {
            let attachHtml = '';
            if (attachment && attachment.type === 'image' && attachment.preview) {
                attachHtml = `<img src="${attachment.preview}" class="chat-attached-image" alt="Imagen adjunta">`;
            } else if (attachment && attachment.type === 'document') {
                const icon = attachment.file_type === 'pdf' ? '📄' : (attachment.file_type === 'docx' ? '📝' : '📑');
                attachHtml = `
                    <div class="chat-attached-doc">
                        <span class="chat-doc-icon">${icon}</span>
                        <div class="chat-doc-info">
                            <span class="chat-doc-name">${attachment.name}</span>
                            <span class="chat-doc-meta">${formatFileSize(attachment.size_bytes)} • Documento analizado</span>
                        </div>
                    </div>
                `;
            }
            bubble.innerHTML = `
                ${attachHtml}
                <div class="msg-content">${text || (attachment ? '<i>Adjunto enviado</i>' : '')}</div>
                <div class="msg-time-tag msg-time-user">${timeStr}</div>
            `;
            item.appendChild(bubble);
        }

        messagesList.appendChild(item);
        scrollToBottom();
        return item;
    }

    function scrollToBottom() {
        if (!chatBody) return;
        chatBody.scrollTo({
            top: chatBody.scrollHeight,
            behavior: 'smooth'
        });
    }

    // --- FORM Y EVENTOS ---
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSendMessage();
    });

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            clearTTSAudioQueue();
            if (SpeechRecognition) {
                playActivationChime();
                isConversationActive = true;
                setVoiceState("LISTENING", "Te escucho...");
                startContinuousListening(true);
            }
        });
    }

    if (jarvisOrb) {
        const triggerOrbActivation = () => {
            clearTTSAudioQueue();
            if (SpeechRecognition) {
                playActivationChime();
                isConversationActive = true;
                setVoiceState("LISTENING", "Te escucho...");
                startContinuousListening(true);
            }
        };

        jarvisOrb.addEventListener('click', triggerOrbActivation);
        jarvisOrb.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                triggerOrbActivation();
            }
        });
    }

    document.querySelectorAll('.prompt-chip, .prompt-chip-sm').forEach(btn => {
        btn.addEventListener('click', () => {
            const pr = btn.getAttribute('data-prompt');
            if (pr) handleSendMessage(pr);
        });
    });

    // =========================================================================
    // MODAL: ESTUDIO MUSICAL Y SONIDOS, LETRAS SINCRONIZADAS & COLA DRAG & DROP
    // =========================================================================
    const studioModal = document.getElementById('music-studio-modal');
    const miniPlayerEl = document.getElementById('mini-player');
    const btnCloseStudio = document.getElementById('btn-close-music-studio');
    const studioBackdrop = document.getElementById('music-studio-backdrop');

    // --- MOTOR DE EXTRACCIÓN DINÁMICA DE COLOR DE LA CANCIÓN ---
    function applyDynamicSongColor(title, artist) {
        const text = ((title || '') + ' ' + (artist || '')).toLowerCase();
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            hash = text.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash) % 360;
        const accent = `hsl(${hue}, 90%, 60%)`;
        const glow = `hsla(${hue}, 95%, 55%, 0.40)`;
        const bgTint = `hsla(${hue}, 45%, 10%, 0.85)`;

        document.documentElement.style.setProperty('--song-accent', accent);
        document.documentElement.style.setProperty('--song-glow', glow);
        document.documentElement.style.setProperty('--song-bg-tint', bgTint);
    }

    // --- MOTOR DE LETRAS SINCRONIZADAS ESTILO SPOTIFY (LRCLIB API) ---
    let currentLyricsData = [];
    let activeLyricIdx = -1;

    async function fetchAndRenderLyrics(title, artist) {
        const container = document.getElementById('studio-lyrics-container');
        const trackLabel = document.getElementById('lyrics-current-track-name');
        const statusBadge = document.getElementById('lyrics-source-text');
        if (!container) return;

        if (trackLabel) trackLabel.textContent = `${artist || ''} — ${title || 'Sin título'}`;
        if (statusBadge) statusBadge.textContent = "Buscando letra...";
        container.innerHTML = `
            <div class="lyrics-empty-state">
                <div class="lyrics-pulse-dot" style="width:14px; height:14px; margin-bottom:8px;"></div>
                <p>Sincronizando letra con LRCLIB...</p>
            </div>
        `;
        currentLyricsData = [];
        activeLyricIdx = -1;

        try {
            const cleanTitle = (title || '').replace(/\(.*?\)|\(.*$/g, '').trim();
            const cleanArtist = (artist || '').replace(/\(.*?\)|\(.*$/g, '').trim();
            
            let res = await fetch(`https://lrclib.net/api/get?artist_name=${encodeURIComponent(cleanArtist)}&track_name=${encodeURIComponent(cleanTitle)}`);
            let data = null;
            if (res.ok) {
                data = await res.json();
            } else {
                let sRes = await fetch(`https://lrclib.net/api/search?q=${encodeURIComponent(cleanTitle + ' ' + cleanArtist)}`);
                if (sRes.ok) {
                    const searchArr = await sRes.json();
                    if (Array.isArray(searchArr) && searchArr.length > 0) {
                        data = searchArr[0];
                    }
                }
            }

            if (data && (data.syncedLyrics || data.plainLyrics)) {
                if (statusBadge) statusBadge.textContent = data.syncedLyrics ? "LRCLIB • Sincronizada" : "LRCLIB • Letra Plana";
                if (data.syncedLyrics) {
                    parseAndRenderSyncedLyrics(data.syncedLyrics);
                } else {
                    renderPlainLyrics(data.plainLyrics);
                }
            } else {
                if (statusBadge) statusBadge.textContent = "Modo Instrumental";
                container.innerHTML = `
                    <div class="lyrics-empty-state">
                        <p>No se encontró letra registrada para "${title}".<br><span style="font-size:11px; opacity:0.6;">Disfruta de la atmósfera musical.</span></p>
                    </div>
                `;
            }
        } catch (err) {
            console.debug("[Lyrics] Error buscando letra:", err);
            if (statusBadge) statusBadge.textContent = "Audio Studio";
            container.innerHTML = `
                <div class="lyrics-empty-state">
                    <p>Letra no disponible temporalmente.<br><span style="font-size:11px; opacity:0.6;">Sincronización fuera de línea.</span></p>
                </div>
            `;
        }
    }

    function parseAndRenderSyncedLyrics(lrcText) {
        const container = document.getElementById('studio-lyrics-container');
        if (!container) return;
        container.innerHTML = '';
        currentLyricsData = [];
        activeLyricIdx = -1;

        const lines = lrcText.split('\n');
        lines.forEach((line) => {
            const match = line.match(/\[(\d+):(\d+(?:\.\d+)?)\](.*)/);
            if (match) {
                const minutes = parseInt(match[1], 10);
                const seconds = parseFloat(match[2]);
                const time = minutes * 60 + seconds;
                const text = match[3].trim();
                if (text.length > 0) {
                    const lyricObj = { time, text, elemIdx: currentLyricsData.length };
                    currentLyricsData.push(lyricObj);

                    const div = document.createElement('div');
                    div.className = 'lyrics-line';
                    div.id = `lyric-line-${lyricObj.elemIdx}`;
                    div.textContent = text;
                    div.addEventListener('click', () => {
                        if (isPlayerReady && ytPlayer && typeof ytPlayer.seekTo === 'function') {
                            ytPlayer.seekTo(time, true);
                            syncLyricsWithTime(time);
                        }
                    });
                    container.appendChild(div);
                }
            }
        });

        if (currentLyricsData.length === 0) {
            renderPlainLyrics(lrcText);
        }
    }

    function renderPlainLyrics(plainText) {
        const container = document.getElementById('studio-lyrics-container');
        if (!container) return;
        container.innerHTML = '';
        currentLyricsData = [];
        activeLyricIdx = -1;

        const lines = (plainText || '').split('\n');
        lines.forEach(line => {
            const t = line.trim();
            if (t.length > 0) {
                const div = document.createElement('div');
                div.className = 'lyrics-line';
                div.textContent = t;
                container.appendChild(div);
            }
        });
    }

    window.syncLyricsWithTime = function(currentTime) {
        if (!currentLyricsData || currentLyricsData.length === 0) return;
        const container = document.getElementById('studio-lyrics-container');
        if (!container) return;

        let newActiveIdx = -1;
        for (let i = 0; i < currentLyricsData.length; i++) {
            const nextTime = (i + 1 < currentLyricsData.length) ? currentLyricsData[i + 1].time : Infinity;
            if (currentTime >= currentLyricsData[i].time && currentTime < nextTime) {
                newActiveIdx = i;
                break;
            }
        }

        if (newActiveIdx !== -1 && newActiveIdx !== activeLyricIdx) {
            if (activeLyricIdx !== -1) {
                const prevEl = document.getElementById(`lyric-line-${activeLyricIdx}`);
                if (prevEl) prevEl.classList.remove('active');
            }
            activeLyricIdx = newActiveIdx;
            const activeEl = document.getElementById(`lyric-line-${activeLyricIdx}`);
            if (activeEl) {
                activeEl.classList.add('active');
                activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    };

    // --- COLA DE REPRODUCCIÓN INTERACTIVA CON DRAG & DROP Y REMOVER ---
    let draggedItemIdx = null;

    window.renderMusicStudioPlaylist = function() {
        const grid = document.getElementById('playlist-grid');
        const queueTag = document.getElementById('queue-count-tag');
        if (!grid) return;
        
        if (queueTag) queueTag.textContent = `${window.playlistData.length}`;
        grid.innerHTML = '';

        if (window.playlistData.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; color: var(--text-secondary); padding: 32px; font-size: 13px;">
                    Sin canciones en cola. Pide una canción o mix a JARVIS.
                </div>
            `;
            return;
        }

        window.playlistData.forEach((track, idx) => {
            const card = document.createElement('div');
            const isActive = idx === window.currentTrackIdx;
            card.className = `playlist-card-item ${isActive ? 'active' : ''}`;
            card.setAttribute('draggable', 'true');
            card.setAttribute('data-index', idx);

            card.innerHTML = `
                <div class="card-drag-handle" title="Arrastra para reordenar con el mouse">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/>
                        <circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/>
                        <circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/>
                    </svg>
                </div>
                <div class="card-play-dot" style="background: ${track.color || 'var(--song-accent, #00f2fe)'};">
                    ${isActive && window.isStudioPlaying ? '⏸' : '▶'}
                </div>
                <div class="card-info">
                    <div class="card-title">${track.title}</div>
                    <div class="card-artist">${track.artist}</div>
                </div>
                <div class="card-duration">${track.duration || '3:30'}</div>
                <button type="button" class="card-remove-btn" title="Quitar de la lista" data-remove-idx="${idx}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;

            // Reproducir al hacer click
            card.addEventListener('click', (e) => {
                if (e.target.closest('.card-remove-btn') || e.target.closest('.card-drag-handle')) return;
                window.playTrackFromStudio(idx);
            });

            // Soporte Drag and Drop nativo
            card.addEventListener('dragstart', (e) => {
                draggedItemIdx = idx;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });

            card.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                card.classList.add('drag-over');
            });

            card.addEventListener('dragleave', () => {
                card.classList.remove('drag-over');
            });

            card.addEventListener('drop', (e) => {
                e.preventDefault();
                card.classList.remove('drag-over');
                if (draggedItemIdx === null || draggedItemIdx === idx) return;

                const moved = window.playlistData.splice(draggedItemIdx, 1)[0];
                window.playlistData.splice(idx, 0, moved);

                if (window.currentTrackIdx === draggedItemIdx) {
                    window.currentTrackIdx = idx;
                } else if (draggedItemIdx < window.currentTrackIdx && idx >= window.currentTrackIdx) {
                    window.currentTrackIdx--;
                } else if (draggedItemIdx > window.currentTrackIdx && idx <= window.currentTrackIdx) {
                    window.currentTrackIdx++;
                }

                draggedItemIdx = null;
                window.renderMusicStudioPlaylist();
            });

            card.addEventListener('dragend', () => {
                card.classList.remove('dragging', 'drag-over');
                draggedItemIdx = null;
            });

            // Botón de remoción de canción
            const removeBtn = card.querySelector('.card-remove-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    window.removeTrackFromStudioQueue(idx);
                });
            }

            grid.appendChild(card);
        });
    };

    window.removeTrackFromStudioQueue = function(idx) {
        if (idx < 0 || idx >= window.playlistData.length) return;
        if (idx === window.currentTrackIdx) {
            window.playlistData.splice(idx, 1);
            if (window.playlistData.length > 0) {
                window.currentTrackIdx = idx % window.playlistData.length;
                window.playTrackFromStudio(window.currentTrackIdx);
            } else {
                window.currentTrackIdx = 0;
                window.isStudioPlaying = false;
                if (ytPlayer && typeof ytPlayer.stopVideo === 'function') ytPlayer.stopVideo();
            }
        } else {
            if (idx < window.currentTrackIdx) window.currentTrackIdx--;
            window.playlistData.splice(idx, 1);
        }
        window.renderMusicStudioPlaylist();
    };

    window.playTrackFromStudio = function(index) {
        if (index < 0 || index >= window.playlistData.length) return;
        window.currentTrackIdx = index;
        const track = window.playlistData[window.currentTrackIdx];
        window.isStudioPlaying = true;

        const mainTitle = document.getElementById('studio-main-title');
        const mainArtist = document.getElementById('studio-main-artist');
        const genreBadge = document.getElementById('studio-genre-badge');
        const timeTotal = document.getElementById('studio-time-total');
        const studioPlayBtn = document.getElementById('studio-btn-playpause');
        const playPauseBtn = document.getElementById('btn-playpause');

        if (mainTitle) mainTitle.textContent = track.title;
        if (mainArtist) mainArtist.textContent = track.artist;
        if (genreBadge) genreBadge.textContent = track.genre || 'EN REPRODUCCIÓN';
        if (timeTotal) timeTotal.textContent = track.duration || '3:45';
        if (studioPlayBtn) studioPlayBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';
        if (playPauseBtn) playPauseBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';

        const playerTrackTitle = document.getElementById('player-track-title');
        const playerTrackArtist = document.getElementById('player-track-artist');
        if (playerTrackTitle) playerTrackTitle.textContent = track.title;
        if (playerTrackArtist) playerTrackArtist.textContent = track.artist;
        
        if (miniPlayerEl) {
            miniPlayerEl.style.display = 'flex';
            miniPlayerEl.classList.add('playing');
        }
        if (studioModal) studioModal.classList.add('playing');

        // Aplicar color dinámico de la canción
        applyDynamicSongColor(track.title, track.artist);

        // Cargar letra sincronizada
        fetchAndRenderLyrics(track.title, track.artist);

        window.renderMusicStudioPlaylist();

        if (track.videoId || track.id) {
            startTrackPlayback(track.videoId || track.id, track.title, track.artist);
        }
    };

    window.addTrackToStudioQueue = function(title, artist, videoId, duration) {
        const colors = ['#00F2FE', '#4FACFE', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899'];
        const randomColor = colors[window.playlistData.length % colors.length];

        const existingIdx = window.playlistData.findIndex(t => t.title.toLowerCase() === title.toLowerCase());
        if (existingIdx !== -1) {
            if (!window.isStudioPlaying) {
                window.playTrackFromStudio(existingIdx);
            } else {
                window.renderMusicStudioPlaylist();
            }
            return;
        }

        const newTrack = {
            id: videoId || `custom_${Date.now()}`,
            videoId: videoId || null,
            title: title || 'Canción en cola',
            artist: artist || 'Artista',
            genre: 'EN COLA',
            duration: duration || '3:30',
            color: randomColor
        };

        window.playlistData.push(newTrack);

        if (!window.isStudioPlaying) {
            window.playTrackFromStudio(window.playlistData.length - 1);
        } else {
            window.renderMusicStudioPlaylist();
        }
    };

    window.loadPlaylistFromBackend = function(tracks, replaceAll) {
        if (!tracks || tracks.length === 0) return;
        const colors = ['#00F2FE', '#4FACFE', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899'];

        const newTracks = tracks.map((t, i) => ({
            id: t.id,
            videoId: t.id,
            title: t.title,
            artist: t.artist,
            genre: 'MIX',
            duration: t.duration ? `${Math.floor(t.duration/60)}:${t.duration%60 < 10 ? '0':''}${t.duration%60}` : '3:30',
            color: colors[i % colors.length]
        }));

        window.playlistData = newTracks;
        window.currentTrackIdx = 0;
        window.playTrackFromStudio(0);
    };

    // Pestañas del Estudio: Letras / Cola / Ambiente
    const tabLyricsBtn = document.getElementById('tab-lyrics-btn');
    const tabQueueBtn = document.getElementById('tab-queue-btn');
    const tabAmbientBtn = document.getElementById('tab-ambient-btn');
    const viewLyrics = document.getElementById('studio-lyrics-view');
    const viewQueue = document.getElementById('studio-queue-view');
    const viewAmbient = document.getElementById('studio-ambient-view');
    const modeSubtitle = document.getElementById('studio-mode-subtitle');

    function switchStudioTab(tab) {
        [tabLyricsBtn, tabQueueBtn, tabAmbientBtn].forEach(b => b?.classList.remove('active'));
        [viewLyrics, viewQueue, viewAmbient].forEach(v => { if (v) v.style.display = 'none'; });

        if (tab === 'lyrics') {
            if (tabLyricsBtn) tabLyricsBtn.classList.add('active');
            if (viewLyrics) viewLyrics.style.display = 'flex';
            if (modeSubtitle) modeSubtitle.textContent = 'Letras Sincronizadas en Tiempo Real';
        } else if (tab === 'queue') {
            if (tabQueueBtn) tabQueueBtn.classList.add('active');
            if (viewQueue) viewQueue.style.display = 'flex';
            if (modeSubtitle) modeSubtitle.textContent = 'Cola de Reproducción & Reordenamiento';
            window.renderMusicStudioPlaylist();
        } else if (tab === 'ambient') {
            if (tabAmbientBtn) tabAmbientBtn.classList.add('active');
            if (viewAmbient) viewAmbient.style.display = 'block';
            if (modeSubtitle) modeSubtitle.textContent = 'Mezclador de Ambiente Procedural';
        }
    }

    if (tabLyricsBtn) tabLyricsBtn.addEventListener('click', () => switchStudioTab('lyrics'));
    if (tabQueueBtn) tabQueueBtn.addEventListener('click', () => switchStudioTab('queue'));
    if (tabAmbientBtn) tabAmbientBtn.addEventListener('click', () => switchStudioTab('ambient'));

    // Render inicial
    window.renderMusicStudioPlaylist();

    if (miniPlayerEl && studioModal) {
        miniPlayerEl.addEventListener('click', (e) => {
            if (e.target.closest('.player-ctrl-btn')) return;
            studioModal.style.display = 'flex';
            window.renderMusicStudioPlaylist();
        });
    }

    if (btnCloseStudio && studioModal) {
        btnCloseStudio.addEventListener('click', () => {
            studioModal.style.display = 'none';
        });
    }
    if (studioBackdrop && studioModal) {
        studioBackdrop.addEventListener('click', () => {
            studioModal.style.display = 'none';
        });
    }

    // Salto interactivo en la barra de progreso
    const studioProgressBg = document.getElementById('studio-progress-bg');
    if (studioProgressBg) {
        studioProgressBg.addEventListener('click', (e) => {
            if (isPlayerReady && ytPlayer && typeof ytPlayer.getDuration === 'function' && typeof ytPlayer.seekTo === 'function') {
                const rect = studioProgressBg.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const pct = Math.max(0, Math.min(1, clickX / rect.width));
                const dur = ytPlayer.getDuration();
                if (dur > 0) {
                    const seekTime = pct * dur;
                    ytPlayer.seekTo(seekTime, true);
                    if (typeof window.syncLyricsWithTime === 'function') {
                        window.syncLyricsWithTime(seekTime);
                    }
                }
            }
        });
    }

    const studioBtnPlayPause = document.getElementById('studio-btn-playpause');
    const studioBtnNext = document.getElementById('studio-btn-next');
    const studioBtnPrev = document.getElementById('studio-btn-prev');
    const studioVolSlider = document.getElementById('studio-vol-slider');

    if (studioBtnPlayPause) {
        studioBtnPlayPause.addEventListener('click', () => {
            if (window.playlistData.length === 0) return;
            window.isStudioPlaying = !window.isStudioPlaying;
            studioBtnPlayPause.innerHTML = window.isStudioPlaying
                ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>'
                : '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>';
            
            const miniBtn = document.getElementById('btn-playpause');
            if (miniBtn) {
                miniBtn.innerHTML = window.isStudioPlaying
                    ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>'
                    : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>';
            }
            
            if (isPlayerReady && ytPlayer && typeof ytPlayer.getPlayerState === 'function') {
                if (window.isStudioPlaying) ytPlayer.playVideo();
                else ytPlayer.pauseVideo();
            }
            if (miniPlayerEl) miniPlayerEl.classList.toggle('playing', window.isStudioPlaying);
            if (studioModal) studioModal.classList.toggle('playing', window.isStudioPlaying);
            window.renderMusicStudioPlaylist();
        });
    }

    if (studioBtnNext) {
        studioBtnNext.addEventListener('click', () => {
            if (window.playlistData.length === 0) return;
            let next = (window.currentTrackIdx + 1) % window.playlistData.length;
            window.playTrackFromStudio(next);
        });
    }

    if (studioBtnPrev) {
        studioBtnPrev.addEventListener('click', () => {
            if (window.playlistData.length === 0) return;
            let prev = (window.currentTrackIdx - 1 + window.playlistData.length) % window.playlistData.length;
            window.playTrackFromStudio(prev);
        });
    }

    if (btnPlayPause) {
        btnPlayPause.addEventListener('click', (e) => {
            e.stopPropagation();
            if (studioBtnPlayPause) studioBtnPlayPause.click();
        });
    }

    if (btnNext) {
        btnNext.addEventListener('click', (e) => {
            e.stopPropagation();
            if (studioBtnNext) studioBtnNext.click();
        });
    }

    if (studioVolSlider) {
        studioVolSlider.addEventListener('input', (e) => {
            const vol = parseInt(e.target.value, 10);
            if (isPlayerReady && ytPlayer && typeof ytPlayer.setVolume === 'function') {
                ytPlayer.setVolume(vol);
            }
        });
    }

    // --- MEZCLADOR DE AMBIENTE PROCEDURAL ---
    let ambientAudioCtx = null;
    let rainGain = null, wavesGain = null, cafeGain = null;

    function initAmbientAudio() {
        if (ambientAudioCtx) return;
        try {
            ambientAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const bufferSize = ambientAudioCtx.sampleRate * 2;
            const noiseBuffer = ambientAudioCtx.createBuffer(1, bufferSize, ambientAudioCtx.sampleRate);
            const output = noiseBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }

            // Lluvia
            const whiteNoise = ambientAudioCtx.createBufferSource();
            whiteNoise.buffer = noiseBuffer;
            whiteNoise.loop = true;
            const rainFilter = ambientAudioCtx.createBiquadFilter();
            rainFilter.type = 'lowpass';
            rainFilter.frequency.value = 1000;
            rainGain = ambientAudioCtx.createGain();
            rainGain.gain.value = 0;
            whiteNoise.connect(rainFilter);
            rainFilter.connect(rainGain);
            rainGain.connect(ambientAudioCtx.destination);
            whiteNoise.start();

            // Olas
            const wavesFilter = ambientAudioCtx.createBiquadFilter();
            wavesFilter.type = 'bandpass';
            wavesFilter.frequency.value = 400;
            const wavesLFO = ambientAudioCtx.createOscillator();
            wavesLFO.frequency.value = 0.12;
            const lfoGain = ambientAudioCtx.createGain();
            lfoGain.gain.value = 250;
            wavesLFO.connect(lfoGain);
            lfoGain.connect(wavesFilter.frequency);
            wavesGain = ambientAudioCtx.createGain();
            wavesGain.gain.value = 0;
            const wavesNoise = ambientAudioCtx.createBufferSource();
            wavesNoise.buffer = noiseBuffer;
            wavesNoise.loop = true;
            wavesNoise.connect(wavesFilter);
            wavesFilter.connect(wavesGain);
            wavesGain.connect(ambientAudioCtx.destination);
            wavesLFO.start();
            wavesNoise.start();

            // Café
            const cafeFilter = ambientAudioCtx.createBiquadFilter();
            cafeFilter.type = 'lowpass';
            cafeFilter.frequency.value = 550;
            cafeGain = ambientAudioCtx.createGain();
            cafeGain.gain.value = 0;
            const cafeNoise = ambientAudioCtx.createBufferSource();
            cafeNoise.buffer = noiseBuffer;
            cafeNoise.loop = true;
            cafeNoise.connect(cafeFilter);
            cafeFilter.connect(cafeGain);
            cafeGain.connect(ambientAudioCtx.destination);
            cafeNoise.start();
        } catch (e) {
            console.debug("[Ambient Sound] Error:", e);
        }
    }

    const studioRainSlider = document.getElementById('studio-rain-slider');
    const studioWavesSlider = document.getElementById('studio-waves-slider');
    const studioCafeSlider = document.getElementById('studio-cafe-slider');

    if (studioRainSlider) {
        studioRainSlider.addEventListener('input', (e) => {
            initAmbientAudio();
            if (rainGain) rainGain.gain.value = (e.target.value / 100) * 0.30;
        });
    }
    if (studioWavesSlider) {
        studioWavesSlider.addEventListener('input', (e) => {
            initAmbientAudio();
            if (wavesGain) wavesGain.gain.value = (e.target.value / 100) * 0.35;
        });
    }
    if (studioCafeSlider) {
        studioCafeSlider.addEventListener('input', (e) => {
            initAmbientAudio();
            if (cafeGain) cafeGain.gain.value = (e.target.value / 100) * 0.25;
        });
    }

    document.querySelectorAll('.mix-mute-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const soundType = btn.getAttribute('data-sound');
            let slider = null;
            if (soundType === 'rain') slider = studioRainSlider;
            if (soundType === 'waves') slider = studioWavesSlider;
            if (soundType === 'cafe') slider = studioCafeSlider;
            
            if (slider) {
                if (slider.value > 0) {
                    slider.dataset.prevVal = slider.value;
                    slider.value = 0;
                    btn.textContent = '🔇';
                } else {
                    slider.value = slider.dataset.prevVal || 40;
                    btn.textContent = '🔈';
                }
                slider.dispatchEvent(new Event('input'));
            }
        });
    });

    const btnOpenAmbient = document.getElementById('btn-open-ambient');
    if (btnOpenAmbient && studioModal) {
        btnOpenAmbient.addEventListener('click', () => {
            studioModal.style.display = 'flex';
            window.renderMusicStudioPlaylist();
        });
    }

    // --- TEMAS INTERCAMBIABLES ---
    const btnOpenThemes = document.getElementById('btn-open-themes');
    const themeSelectorBar = document.getElementById('theme-selector-bar');
    if (btnOpenThemes && themeSelectorBar) {
        btnOpenThemes.addEventListener('click', () => {
            const isHidden = themeSelectorBar.style.display === 'none';
            themeSelectorBar.style.display = isHidden ? 'flex' : 'none';
        });
    }

    document.querySelectorAll('.theme-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const theme = chip.getAttribute('data-theme');
            document.documentElement.setAttribute('data-theme', theme);
            document.querySelectorAll('.theme-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
        });
    });

    // --- MEMORIA PERMANENTE ---
    const memoryData = [
        { cat: 'gaming', key: 'Juegos Favoritos', val: 'Devil May Cry 3 y 5 (Estilo Hack and Slash)' },
        { cat: 'music', key: 'Artista Favorita', val: 'Billie Eilish (le fascina su voz y estilo melódico)' },
        { cat: 'music', key: 'Banda Principal', val: 'Queen (Rock Clásico)' },
        { cat: 'music', key: 'Bandas Destacadas', val: 'My Chemical Romance, System of a Down, Scorpions, Audioslave' },
        { cat: 'preference', key: 'Color Favorito', val: 'Azul oscuro' },
        { cat: 'preference', key: 'Estilo de Comunicación', val: 'Respuestas ultra cortas y precisas' },
        { cat: 'preference', key: 'Estilo de Humor', val: 'Tono serio y sobrio' },
        { cat: 'lifestyle', key: 'Nombre', val: 'Jhonatan David Torres Patiño (Alias: Dante)' },
        { cat: 'lifestyle', key: 'Hobby', val: 'Programación en Python' },
        { cat: 'lifestyle', key: 'Deporte', val: 'Ajedrez' },
        { cat: 'lifestyle', key: 'Horario Universidad', val: 'Lunes a Viernes | 18:00 - 22:00' }
    ];

    const memoryDrawer = document.getElementById('memory-drawer');
    const btnOpenMemory = document.getElementById('btn-open-memory');
    const btnCloseMemory = document.getElementById('btn-close-memory');
    const memoryItemsList = document.getElementById('memory-items-list');

    function renderMemories(category = 'all') {
        if (!memoryItemsList) return;
        memoryItemsList.innerHTML = '';
        const filtered = category === 'all' ? memoryData : memoryData.filter(m => m.cat === category);
        filtered.forEach(m => {
            const card = document.createElement('div');
            card.className = 'memory-item-card';
            card.innerHTML = `
                <div class="mem-key">#${m.cat} • ${m.key}</div>
                <div class="mem-val">${m.val}</div>
            `;
            memoryItemsList.appendChild(card);
        });
    }

    if (btnOpenMemory && memoryDrawer) {
        btnOpenMemory.addEventListener('click', () => {
            renderMemories('all');
            memoryDrawer.classList.toggle('open');
        });
    }
    if (btnCloseMemory && memoryDrawer) {
        btnCloseMemory.addEventListener('click', () => {
            memoryDrawer.classList.remove('open');
        });
    }

    document.querySelectorAll('.mem-cat-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mem-cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMemories(btn.getAttribute('data-cat'));
        });
    });

    // --- AJUSTES Y DIAGNÓSTICO ---
    if (btnToggleDrawer && contextDrawer) {
        btnToggleDrawer.addEventListener('click', () => {
            uiState.isDrawerOpen = !uiState.isDrawerOpen;
            contextDrawer.classList.toggle('open', uiState.isDrawerOpen);
        });
    }
    if (btnCloseDrawer && contextDrawer) {
        btnCloseDrawer.addEventListener('click', () => {
            uiState.isDrawerOpen = false;
            contextDrawer.classList.remove('open');
        });
    }
});