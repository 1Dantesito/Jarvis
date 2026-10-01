// =========================================================================
// JARVIS v3.0 — Continuous Hands-Free Engine, Real Voice & WebSockets
// =========================================================================

// --- BOBA / FLOATING BUBBLES CANVAS ENGINE ---
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

    const bubbles = [];
    const BUBBLE_COUNT = 16;

    for (let i = 0; i < BUBBLE_COUNT; i++) {
        const typeRoll = Math.random();
        let hue, sat, light, alpha;
        if (typeRoll < 0.4) {
            hue = 348 + Math.random() * 10;
            sat = 85;
            light = 50;
            alpha = Math.random() * 0.06 + 0.03;
        } else if (typeRoll < 0.75) {
            hue = 356 + Math.random() * 8;
            sat = 90;
            light = 45;
            alpha = Math.random() * 0.05 + 0.02;
        } else {
            hue = 0 + Math.random() * 10;
            sat = 80;
            light = 38;
            alpha = Math.random() * 0.07 + 0.03;
        }

        bubbles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 90 + 35,
            vx: (Math.random() - 0.5) * 0.25,
            vy: (Math.random() - 0.5) * 0.25,
            hue, sat, light, alpha
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (const b of bubbles) {
            b.x += b.vx;
            b.y += b.vy;

            if (b.x < -b.radius) b.x = width + b.radius;
            if (b.x > width + b.radius) b.x = -b.radius;
            if (b.y < -b.radius) b.y = height + b.radius;
            if (b.y > height + b.radius) b.y = -b.radius;

            const grad = ctx.createRadialGradient(b.x, b.y, b.radius * 0.1, b.x, b.y, b.radius);
            grad.addColorStop(0, `hsla(${b.hue}, ${b.sat}%, ${b.light}%, ${b.alpha * 1.6})`);
            grad.addColorStop(0.7, `hsla(${b.hue}, ${b.sat}%, ${b.light}%, ${b.alpha * 0.6})`);
            grad.addColorStop(1, `hsla(${b.hue}, ${b.sat}%, ${b.light}%, 0)`);

            ctx.beginPath();
            ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();
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
            }
        }
    }, 500);
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
        if (!jarvisOrb) return;
        jarvisOrb.classList.remove('idle', 'listening', 'thinking', 'processing', 'speaking', 'error');

        switch (state) {
            case "LISTENING":
                jarvisOrb.classList.add('listening');
                jarvisOrb.setAttribute('aria-label', 'JARVIS escuchando tu voz...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Escuchando...";
                if (handsfreeHint) handsfreeHint.textContent = "🎙️ Micrófono Abierto";
                if (micBtn) micBtn.classList.add('listening');
                break;
            case "PROCESSING":
                jarvisOrb.classList.add('thinking');
                jarvisOrb.setAttribute('aria-label', 'JARVIS procesando respuesta...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Procesando...";
                if (handsfreeHint) handsfreeHint.textContent = "⚡ Consultando...";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "SPEAKING":
                jarvisOrb.classList.add('speaking');
                jarvisOrb.setAttribute('aria-label', 'JARVIS respondiendo con voz...');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Hablando...";
                if (handsfreeHint) handsfreeHint.textContent = "🔊 Audio Activo";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "ERROR":
                jarvisOrb.classList.add('error');
                jarvisOrb.setAttribute('aria-label', 'JARVIS ha encontrado un error. Haz clic para reintentar.');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Error";
                if (handsfreeHint) handsfreeHint.textContent = "⚠️ Intenta de nuevo";
                if (micBtn) micBtn.classList.remove('listening');
                break;
            case "IDLE":
            default:
                jarvisOrb.classList.add('idle');
                jarvisOrb.setAttribute('aria-label', 'JARVIS en reposo. Haz clic o di Jarvis para interactuar.');
                if (voiceStatusText) voiceStatusText.textContent = customText || "Listo (escuchando 'Jarvis'...)";
                if (handsfreeHint) handsfreeHint.textContent = "🎙️ Manos Libres Activo";
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
                        <button class="msg-util-btn btn-read-aloud" title="Leer en voz alta">🔊 Leer</button>
                        <button class="msg-util-btn btn-copy-msg" title="Copiar texto">📋 Copiar</button>
                        <button class="msg-util-btn btn-like-msg" title="Me gusta">🤍</button>
                    `;
                    const readBtn = utils.querySelector('.btn-read-aloud');
                    if (readBtn) {
                        readBtn.addEventListener('click', () => {
                            clearTTSAudioQueue();
                            if (!fullText) return;
                            // Fragmentar en oraciones para reproducción instantánea con pre-carga continua
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
                            copyBtn.textContent = '✓ Copiado';
                            setTimeout(() => copyBtn.textContent = '📋 Copiar', 2000);
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
                        <span class="assistant-label">⚡ JARVIS AI</span>
                        <span class="msg-time">${new Date().toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'})}</span>
                    </div>
                    <div class="msg-content">🔔 <strong>${title}</strong><br>${message}</div>
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
                    <span style="font-family:'Outfit',sans-serif; font-size:11px; font-weight:800; color:var(--accent-secondary); letter-spacing:0.5px;">⚡ JARVIS AI</span>
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

        let icon = "⚡";
        let label = detail || 'Acción completada';
        let btnText = "Ver detalle";
        let btnAction = () => {};

        if (actionType === "play_music") {
            icon = "🎵";
            label = `Reproduciendo música • ${detail || 'Música'}`;
            btnText = "▶ Oír pista";
            btnAction = () => {
                const studioM = document.getElementById('music-studio-modal');
                if (studioM) studioM.style.display = 'flex';
            };
        } else if (actionType === "remember_info" || actionType === "forget_memory") {
            icon = "🧠";
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
                    <span class="msg-sender-tag">⚡ JARVIS AI</span>
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
    // MODAL: ESTUDIO MUSICAL Y SONIDOS & COLA DINÁMICA
    // =========================================================================
    const studioModal = document.getElementById('music-studio-modal');
    const miniPlayerEl = document.getElementById('mini-player');
    const btnCloseStudio = document.getElementById('btn-close-music-studio');
    const studioBackdrop = document.getElementById('music-studio-backdrop');

    // Inicializar render de playlist vacía
    window.renderMusicStudioPlaylist = function() {
        const grid = document.getElementById('playlist-grid');
        const queueTag = document.getElementById('queue-count-tag');
        if (!grid) return;
        
        if (queueTag) queueTag.textContent = `${window.playlistData.length} pistas`;
        grid.innerHTML = '';

        if (window.playlistData.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; color: #9CA3AF; padding: 22px; font-size: 12px;">
                    🎵 Sin canciones en cola. Pide una canción o mix a JARVIS.
                </div>
            `;
            return;
        }

        window.playlistData.forEach((track, idx) => {
            const card = document.createElement('div');
            const isActive = idx === window.currentTrackIdx;
            card.className = `playlist-card-item ${isActive ? 'active' : ''}`;
            card.innerHTML = `
                <div class="card-play-dot" style="background: ${track.color || '#EC4899'};">
                    ${isActive && window.isStudioPlaying ? '⏸' : '▶'}
                </div>
                <div class="card-info">
                    <div class="card-title">${track.title}</div>
                    <div class="card-artist">${track.artist}</div>
                </div>
                <div class="card-duration">${track.duration || '3:30'}</div>
            `;

            card.addEventListener('click', () => {
                window.playTrackFromStudio(idx);
            });

            grid.appendChild(card);
        });
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
        if (studioPlayBtn) studioPlayBtn.textContent = '⏸';
        if (playPauseBtn) playPauseBtn.textContent = '⏸';

        const playerTrackTitle = document.getElementById('player-track-title');
        const playerTrackArtist = document.getElementById('player-track-artist');
        if (playerTrackTitle) playerTrackTitle.textContent = track.title;
        if (playerTrackArtist) playerTrackArtist.textContent = track.artist;
        
        if (miniPlayerEl) {
            miniPlayerEl.style.display = 'flex';
            miniPlayerEl.classList.add('playing');
        }
        if (studioModal) studioModal.classList.add('playing');

        window.renderMusicStudioPlaylist();

        if (track.videoId || track.id) {
            startTrackPlayback(track.videoId || track.id, track.title, track.artist);
        }
    };

    window.addTrackToStudioQueue = function(title, artist, videoId, duration) {
        const colors = ['#EC4899', '#8B5CF6', '#10B981', '#3B82F6', '#F59E0B', '#F43F5E'];
        const randomColor = colors[window.playlistData.length % colors.length];

        const existingIdx = window.playlistData.findIndex(t => t.title.toLowerCase() === title.toLowerCase());
        if (existingIdx !== -1) {
            // Ya está en la lista: si no hay nada reproduciéndose, reproducir; si ya hay, solo actualizar UI
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

        // Solo reproducir si NO hay nada activo
        if (!window.isStudioPlaying) {
            window.playTrackFromStudio(window.playlistData.length - 1);
        } else {
            // Solo agregar a la lista, sin interrumpir lo que se reproduce
            window.renderMusicStudioPlaylist();
        }
    };

    window.loadPlaylistFromBackend = function(tracks, replaceAll) {
        if (!tracks || tracks.length === 0) return;
        const colors = ['#EC4899', '#8B5CF6', '#10B981', '#3B82F6', '#F59E0B', '#F43F5E'];

        const newTracks = tracks.map((t, i) => ({
            id: t.id,
            videoId: t.id,
            title: t.title,
            artist: t.artist,
            genre: 'MIX',
            duration: t.duration ? `${Math.floor(t.duration/60)}:${t.duration%60 < 10 ? '0':''}${t.duration%60}` : '3:30',
            color: colors[i % colors.length]
        }));

        // Siempre reemplaza: el backend es la fuente de verdad de la cola
        window.playlistData = newTracks;
        window.currentTrackIdx = 0;
        window.playTrackFromStudio(0);
    };


    // Render inicial vacío
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

    const studioBtnPlayPause = document.getElementById('studio-btn-playpause');
    const studioBtnNext = document.getElementById('studio-btn-next');
    const studioBtnPrev = document.getElementById('studio-btn-prev');
    const studioVolSlider = document.getElementById('studio-vol-slider');

    if (studioBtnPlayPause) {
        studioBtnPlayPause.addEventListener('click', () => {
            if (window.playlistData.length === 0) return;
            window.isStudioPlaying = !window.isStudioPlaying;
            studioBtnPlayPause.textContent = window.isStudioPlaying ? '⏸' : '▶';
            const miniBtn = document.getElementById('btn-playpause');
            if (miniBtn) miniBtn.textContent = window.isStudioPlaying ? '⏸' : '▶';
            
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