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
        const isSpeaking = (window.currentVoiceState === "SPEAKING" || window.isPlayingTTSQueue === true || window.isSpeakingAudio === true);
        const isListening = (window.currentVoiceState === "LISTENING");

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

        // 4. Membrana Neuronal y Cuerdas Vocales Cuánticas Reactivas a la Voz de JARVIS
        const targetAmp = isSpeaking ? 34.0 : (isListening ? 12.0 : 3.5);
        if (typeof window._jarvisVoiceAmp === 'undefined') window._jarvisVoiceAmp = 3.5;
        window._jarvisVoiceAmp += (targetAmp - window._jarvisVoiceAmp) * 0.12;
        const vAmp = window._jarvisVoiceAmp;
        const vSpeed = isSpeaking ? 4.5 : (isListening ? 2.4 : 1.2);

        // Cuerda 3: Resonancia de Sub-frecuencia (Azul Zafiro Profundo)
        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        for (let x = 0; x <= width; x += 15) {
            const subW = Math.sin(x * 0.005 + time * (vSpeed * 0.8)) * (vAmp * 0.85) +
                         Math.cos(x * 0.012 - time * (vSpeed * 0.6)) * (vAmp * 0.4);
            ctx.lineTo(x, horizonY + subW);
        }
        ctx.strokeStyle = isSpeaking ? 'rgba(0, 136, 255, 0.75)' : 'rgba(0, 136, 255, 0.20)';
        ctx.lineWidth = isSpeaking ? 2.2 : 0.9;
        ctx.shadowBlur = isSpeaking ? 16 : 4;
        ctx.shadowColor = 'rgba(0, 136, 255, 0.8)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Cuerda 2: Armónico Medio (Turquesa Eléctrico)
        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        for (let x = 0; x <= width; x += 12) {
            const midW = Math.sin(x * 0.011 - time * (vSpeed * 1.1)) * (vAmp * 0.7) +
                         Math.sin(x * 0.024 + time * vSpeed) * (vAmp * 0.35);
            ctx.lineTo(x, horizonY + midW);
        }
        ctx.strokeStyle = isSpeaking ? 'rgba(56, 225, 255, 0.85)' : 'rgba(56, 225, 255, 0.25)';
        ctx.lineWidth = isSpeaking ? 1.8 : 0.8;
        ctx.shadowBlur = isSpeaking ? 14 : 5;
        ctx.shadowColor = 'rgba(56, 225, 255, 0.7)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Cuerda 1: Cuerda Vocal Principal (Cian Neón Puro)
        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        const nodePoints = [];
        for (let x = 0; x <= width; x += 10) {
            const mainW = Math.sin(x * 0.008 + time * vSpeed) * vAmp +
                          Math.cos(x * 0.018 - time * (vSpeed * 1.3)) * (vAmp * 0.45) +
                          Math.sin(x * 0.035 + time * (vSpeed * 1.8)) * (vAmp * 0.2);
            const yPt = horizonY + mainW;
            ctx.lineTo(x, yPt);
            if (x > 0 && x < width && x % Math.floor(width / 8) < 10) {
                nodePoints.push({ x, y: yPt });
            }
        }
        ctx.strokeStyle = isSpeaking ? 'rgba(0, 242, 254, 0.95)' : 'rgba(0, 242, 254, 0.35)';
        ctx.lineWidth = isSpeaking ? 2.6 : 1.2;
        ctx.shadowBlur = isSpeaking ? 22 : 8;
        ctx.shadowColor = 'rgba(0, 242, 254, 0.9)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Cuerda 4: Shimmer de Alta Frecuencia (Cobalto Resonante)
        ctx.beginPath();
        ctx.moveTo(0, horizonY);
        for (let x = 0; x <= width; x += 12) {
            const shimW = Math.sin(x * 0.028 + time * (vSpeed * 1.7)) * (vAmp * 0.35);
            ctx.lineTo(x, horizonY + shimW);
        }
        ctx.strokeStyle = isSpeaking ? 'rgba(79, 172, 254, 0.75)' : 'rgba(79, 172, 254, 0.15)';
        ctx.lineWidth = isSpeaking ? 1.2 : 0.6;
        ctx.stroke();

        // Nodos Cuánticos Luminosos en la cuerda principal
        for (const pt of nodePoints) {
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, isSpeaking ? 3.5 : 1.8, 0, Math.PI * 2);
            ctx.fillStyle = isSpeaking ? '#FFFFFF' : 'rgba(0, 242, 254, 0.6)';
            ctx.shadowBlur = isSpeaking ? 16 : 6;
            ctx.shadowColor = '#00F2FE';
            ctx.fill();
            ctx.shadowBlur = 0;
        }

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
                'playsinline': 1,
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

// Funciones para ducking y control de volumen musical
window.duckMusicForTTS = function() {
    if (isPlayerReady && ytPlayer && typeof ytPlayer.setVolume === 'function') {
        ytPlayer.setVolume(20);
    }
};

window.restoreMusicVolume = function() {
    if (isPlayerReady && ytPlayer && typeof ytPlayer.setVolume === 'function') {
        const studioVolSlider = document.getElementById('studio-volume-slider');
        const normalVol = studioVolSlider ? parseInt(studioVolSlider.value, 10) : 100;
        ytPlayer.setVolume(normalVol || 100);
    }
};

function onPlayerStateChange(event) {
    const playPauseBtn = document.getElementById('btn-playpause');
    const studioPlayPauseBtn = document.getElementById('studio-btn-playpause');
    const miniPlayer = document.getElementById('mini-player');
    const studioModal = document.getElementById('music-studio-modal');

    if (event.data === YT.PlayerState.PLAYING) {
        window.isStudioPlaying = true;
        if (typeof window.stopSpeechForMusicPlayback === 'function') {
            window.stopSpeechForMusicPlayback();
        }
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
        if (typeof window.resumeSpeechAfterMusicPlayback === 'function') {
            window.resumeSpeechAfterMusicPlayback();
        }
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
        if (typeof window.resumeSpeechAfterMusicPlayback === 'function') {
            window.resumeSpeechAfterMusicPlayback();
        }
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
            if (typeof window.duckMusicForTTS === 'function') {
                window.duckMusicForTTS();
            }
            playNextTTSChunk();
        }
    }

    function onTTSPlaybackFinished() {
        isPlayingTTSQueue = false;
        window.isPlayingTTSQueue = false;
        window.isSpeakingAudio = false;
        currentTTSAudio = null;

        if (typeof window.restoreMusicVolume === 'function') {
            window.restoreMusicVolume();
        }

        if (window.wasMusicPlayingBeforeMic) {
            window.wasMusicPlayingBeforeMic = false;
            if (isPlayerReady && ytPlayer && typeof ytPlayer.playVideo === 'function' && !window.isStudioPlaying) {
                ytPlayer.playVideo();
            }
        }

        if (continuousEnabled && !window.isStudioPlaying && !window.isMusicPlaying) {
            openConversationalWindow(8000);
        } else if (uiState.voiceState === "SPEAKING") {
            setVoiceState("IDLE");
        }
    }

    function playNextTTSChunk() {
        if (!uiState.soundEnabled || uiState.voiceState === "INTERRUPTED") {
            clearTTSAudioQueue();
            return;
        }
        if (ttsAudioQueue.length === 0) {
            onTTSPlaybackFinished();
            return;
        }

        isPlayingTTSQueue = true;
        window.isPlayingTTSQueue = true;
        window.isSpeakingAudio = true;
        setVoiceState("SPEAKING");

        const nextAudio = ttsAudioQueue.shift();
        currentTTSAudio = nextAudio;

        currentTTSAudio.onended = () => {
            currentTTSAudio = null;
            if (ttsAudioQueue.length === 0) {
                onTTSPlaybackFinished();
            }
            playNextTTSChunk();
        };

        currentTTSAudio.onerror = (e) => {
            console.warn("[TTS Chunk Error]", e);
            currentTTSAudio = null;
            if (ttsAudioQueue.length === 0) {
                onTTSPlaybackFinished();
            }
            playNextTTSChunk();
        };

        currentTTSAudio.play().catch(e => {
            console.warn("[TTS Play Error]", e);
            currentTTSAudio = null;
            if (ttsAudioQueue.length === 0) {
                onTTSPlaybackFinished();
            }
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
        window.isPlayingTTSQueue = false;
        window.isSpeakingAudio = false;
        if (currentTTSAudio) {
            try {
                currentTTSAudio.pause();
                currentTTSAudio.src = '';
                currentTTSAudio.load();
            } catch (e) {}
            currentTTSAudio = null;
        }
        if (typeof window.restoreMusicVolume === 'function') {
            window.restoreMusicVolume();
        }
        if (uiState.voiceState === "SPEAKING") {
            setVoiceState("IDLE");
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

    // --- RENDERIZADO MARKDOWN AVANZADO (LISTAS, CÓDIGO, PÁRRAFOS TIPO CHATGPT) ---
    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function parseInlineMarkdown(text) {
        if (!text) return "";
        let t = text;
        // Negrita
        t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        t = t.replace(/__([^_]+)__/g, '<strong>$1</strong>');
        // Cursiva
        t = t.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        t = t.replace(/_([^_]+)_/g, '<em>$1</em>');
        // Tachado
        t = t.replace(/~~(.*?)~~/g, '<del>$1</del>');
        // Enlaces [texto](url)
        t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        return t;
    }

    function renderMarkdownNative(text) {
        if (!text) return "";

        // 1. Proteger bloques de código ```lang ... ```
        const codeBlocks = [];
        let src = text.replace(/```([a-zA-Z0-9_\-\+\.]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const idx = codeBlocks.length;
            const langLabel = lang.trim() || "código";
            const escapedCode = escapeHtml(code.trim());
            codeBlocks.push(
                `<div class="code-block-container">` +
                    `<div class="code-header">` +
                        `<span class="code-lang">${langLabel}</span>` +
                        `<button class="code-copy-btn" onclick="navigator.clipboard.writeText(this.closest('.code-block-container').querySelector('code').innerText).then(()=>{this.textContent='Copiado!';setTimeout(()=>this.textContent='Copiar',2000)})">Copiar</button>` +
                    `</div>` +
                    `<pre><code class="language-${langLabel}">${escapedCode}</code></pre>` +
                `</div>`
            );
            return `__CODE_BLOCK_${idx}__`;
        });

        // 2. Proteger código inline `code`
        const inlineCodes = [];
        src = src.replace(/`([^`\n]+)`/g, (match, code) => {
            const idx = inlineCodes.length;
            inlineCodes.push(`<code>${escapeHtml(code)}</code>`);
            return `__INLINE_CODE_${idx}__`;
        });

        // 3. Procesar líneas y estructuras (Encabezados, Listas, Citas, Párrafos)
        const lines = src.split(/\r?\n/);
        let inUl = false;
        let inOl = false;
        let inBlockquote = false;
        let result = [];

        function closeOpenLists() {
            if (inUl) { result.push('</ul>'); inUl = false; }
            if (inOl) { result.push('</ol>'); inOl = false; }
            if (inBlockquote) { result.push('</blockquote>'); inBlockquote = false; }
        }

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            const trimmed = line.trim();

            if (!trimmed) {
                closeOpenLists();
                continue;
            }

            // Encabezados Markdown
            if (trimmed.startsWith('#### ')) {
                closeOpenLists();
                result.push(`<h4>${parseInlineMarkdown(trimmed.substring(5))}</h4>`);
                continue;
            } else if (trimmed.startsWith('### ')) {
                closeOpenLists();
                result.push(`<h3>${parseInlineMarkdown(trimmed.substring(4))}</h3>`);
                continue;
            } else if (trimmed.startsWith('## ')) {
                closeOpenLists();
                result.push(`<h2>${parseInlineMarkdown(trimmed.substring(3))}</h2>`);
                continue;
            } else if (trimmed.startsWith('# ')) {
                closeOpenLists();
                result.push(`<h1>${parseInlineMarkdown(trimmed.substring(2))}</h1>`);
                continue;
            }

            // Separador horizontal
            if (/^(?:---|\*\*\*|___)$/.test(trimmed)) {
                closeOpenLists();
                result.push('<hr>');
                continue;
            }

            // Citas / Blockquotes
            if (trimmed.startsWith('> ')) {
                if (inUl) { result.push('</ul>'); inUl = false; }
                if (inOl) { result.push('</ol>'); inOl = false; }
                if (!inBlockquote) {
                    result.push('<blockquote>');
                    inBlockquote = true;
                }
                result.push(parseInlineMarkdown(trimmed.substring(2)));
                continue;
            } else if (inBlockquote) {
                result.push('</blockquote>');
                inBlockquote = false;
            }

            // Listas con viñetas (- o *)
            const ulMatch = trimmed.match(/^[-*]\s+(.*)$/);
            if (ulMatch) {
                if (inOl) { result.push('</ol>'); inOl = false; }
                if (!inUl) {
                    result.push('<ul>');
                    inUl = true;
                }
                result.push(`<li>${parseInlineMarkdown(ulMatch[1])}</li>`);
                continue;
            }

            // Listas numeradas (1. , 2. )
            const olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
            if (olMatch) {
                if (inUl) { result.push('</ul>'); inUl = false; }
                if (!inOl) {
                    result.push('<ol>');
                    inOl = true;
                }
                result.push(`<li>${parseInlineMarkdown(olMatch[1])}</li>`);
                continue;
            }

            // Placeholder de bloque de código
            if (trimmed.startsWith('__CODE_BLOCK_') && trimmed.endsWith('__')) {
                closeOpenLists();
                result.push(trimmed);
                continue;
            }

            // Placeholder o montura de bloque visual interactivo
            if (trimmed.startsWith('<div class="jarvis-visual-mount"') || /^(?:__|@@|%%)(?:JARVIS_)?VISUAL_BLOCK_\d+(?:__|@@|%%)$/.test(trimmed)) {
                closeOpenLists();
                result.push(trimmed);
                continue;
            }

            // Párrafo normal
            closeOpenLists();
            result.push(`<p>${parseInlineMarkdown(trimmed)}</p>`);
        }

        closeOpenLists();

        let output = result.join('\n');

        // Restaurar bloques de código e inline
        output = output.replace(/__CODE_BLOCK_(\d+)__/g, (match, idx) => codeBlocks[idx] || "");
        output = output.replace(/__INLINE_CODE_(\d+)__/g, (match, idx) => inlineCodes[idx] || "");

        return output;
    }

    function beautifyMarkdownText(text) {
        if (!text) return "";
        let s = text;
        // 0. Separar encabezados markdown (# Título, ## Subtítulo, ### 01. Ítem) pegados a texto previo
        s = s.replace(/([^\n])\s+(?=#{1,3}\s+)/g, "$1\n\n");
        s = s.replace(/([^\n])\s+(?=JARVIS\s*[·•-]?\s*¿?QUÉ\s+TE\s+APETECE)/gi, "$1\n\n");
        // 0.1 Separar subtítulo en negrita dentro de una tarjeta si está pegado al título
        s = s.replace(/(###\s*0?\d+\.\s*[^\n*]+?)\s+(\*\*[^\*\n]+\*\*)/g, "$1\n$2");
        // 1. Separar encabezado previo a una lista numerada (ej. ': 1. ' -> ':\n\n1. ')
        s = s.replace(/([:;])\s+(?=\d+\.\s+)/g, "$1\n\n");
        // 2. Separar elementos de lista numerada pegados en el mismo renglón (ej. '. 2. ' -> '.\n\n2. ')
        s = s.replace(/([.?!])\s+(?=\d+\.\s+)/g, "$1\n\n");
        // 3. Separar viñetas pegadas tras puntuación (ej. ': - ' -> ':\n\n- ')
        s = s.replace(/([:;.?!])\s+(?=[-•*]\s+)/g, "$1\n\n");
        // Separar viñetas pegadas sin puntuación cuando van seguidas de mayúscula o negrita
        s = s.replace(/(?<=[^\s:;.?!])\s+[-•*]\s+(?=[A-ZÁÉÍÓÚ]|\*\*)/g, "\n\n- ");
        // 4. Normalizar viñetas unicode (•, ·) a guiones markdown estándar
        s = s.replace(/(?:^|\n)[ \t]*[•·]\s+/g, "\n- ");
        // 5. Separar preguntas o conclusiones finales después de una lista numerada
        s = s.replace(/(\d+\.[^\n]+?[.?!])\s+([¿¡A-ZÁÉÍÓÚ][^\n]{3,})/g, "$1\n\n$2");
        // 6. Normalizar saltos excesivos a máximo 2 saltos
        s = s.replace(/\n{3,}/g, "\n\n");
        return s.trim();
    }

    window.toggleChecklistItem = function(el) {
        if (!el) return;
        el.classList.toggle('checked');
        const card = el.closest('.jarvis-checklist-card');
        if (card) {
            const total = card.querySelectorAll('.checklist-item').length;
            const checked = card.querySelectorAll('.checklist-item.checked').length;
            const countEl = card.querySelector('.checklist-count');
            const fillEl = card.querySelector('.progress-fill');
            if (countEl) countEl.textContent = `${checked}/${total}`;
            if (fillEl && total > 0) fillEl.style.width = `${Math.round((checked / total) * 100)}%`;
        }
    };

    window.toggleCardFav = function(btn) {
        if (!btn) return;
        btn.classList.toggle('favorited');
        const isFav = btn.classList.contains('favorited');
        const textSpan = btn.querySelector('.fav-text');
        const svgIcon = btn.querySelector('.fav-icon');
        if (textSpan) {
            textSpan.textContent = isFav ? 'Guardado' : 'Añadir a Favoritos';
        }
        if (svgIcon) {
            svgIcon.setAttribute('fill', isFav ? 'currentColor' : 'none');
        }
    };

    window.sendSuggestedPrompt = function(promptText) {
        if (!promptText) return;
        const input = document.getElementById('user-input');
        if (input) {
            input.value = promptText;
            input.focus();
        }
        const form = document.getElementById('chat-form');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    };

    window.handleShowcaseImgError = function(target) {
        if (!target) return;
        const card = target.closest ? target.closest('.jarvis-showcase-card') : target;
        if (!card) return;
        card.classList.remove('has-thumb', 'is-loading-img');
        card.classList.add('no-thumb');

        const thumbCol = card.querySelector('.showcase-thumb-col');
        const pillRow = card.querySelector('.showcase-pill-row');
        if (thumbCol && pillRow) {
            const favBtn = thumbCol.querySelector('.showcase-fav-btn');
            if (favBtn && !pillRow.querySelector('.showcase-fav-btn')) {
                favBtn.classList.add('inline-fav-btn');
                pillRow.appendChild(favBtn);
            }
            thumbCol.remove();
        }
    };

    window.resolveShowcaseCardImages = function() {
        const cards = document.querySelectorAll('.jarvis-showcase-card[data-auto-img-query]:not([data-resolving])');
        if (!cards || cards.length === 0) return;

        cards.forEach(card => {
            card.setAttribute('data-resolving', 'true');
            const query = (card.getAttribute('data-auto-img-query') || '').trim();
            if (!query) {
                window.handleShowcaseImgError(card);
                return;
            }

            // Si el cliente no tiene conexión a internet, nunca dejar emojis ni cajas vacías
            if (typeof navigator !== 'undefined' && navigator.onLine === false) {
                window.handleShowcaseImgError(card);
                return;
            }

            // Consultar endpoint de resolución de imágenes reales de JARVIS
            fetch(`/api/images/search?q=${encodeURIComponent(query)}`)
                .then(res => {
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    return res.json();
                })
                .then(result => {
                    const imgUrl = (result && result.data && result.data.image_url) ? result.data.image_url : null;
                    if (!imgUrl) {
                        window.handleShowcaseImgError(card);
                        return;
                    }

                    // Precargar imagen para evitar saltos visuales o enlaces rotos
                    const preloadImg = new Image();
                    preloadImg.onload = function() {
                        const thumbBox = card.querySelector('.showcase-thumb-box');
                        if (thumbBox) {
                            thumbBox.classList.remove('showcase-skeleton-box');
                            thumbBox.innerHTML = `<img src="${escapeHtml(imgUrl)}" alt="${escapeHtml(query)}" class="showcase-thumb-img" loading="lazy" onerror="window.handleShowcaseImgError(this)" />`;
                            card.classList.remove('is-loading-img');
                            card.classList.add('img-loaded');
                        }
                    };
                    preloadImg.onerror = function() {
                        window.handleShowcaseImgError(card);
                    };
                    preloadImg.src = imgUrl;
                })
                .catch(err => {
                    console.debug("[ShowcaseImages] No se pudo obtener imagen externa:", err);
                    window.handleShowcaseImgError(card);
                });
        });
    };

    function buildShowcaseCardHtml(numStr, title, meta, desc, imgUrl) {
        const numDisplay = (numStr && String(numStr).length === 1) ? `0${numStr}` : (numStr || '01');
        const safeTitle = escapeHtml(title || 'Recomendación');
        const safeMeta = meta ? escapeHtml(meta) : '';
        const safeDesc = escapeHtml(desc || '');

        // 1. Si ya viene con URL de imagen válida en el texto/markdown
        if (imgUrl && (imgUrl.startsWith('http') || imgUrl.startsWith('/') || imgUrl.startsWith('data:'))) {
            return `
                <div class="jarvis-showcase-card has-thumb">
                    <div class="showcase-thumb-col">
                        <div class="showcase-thumb-box">
                            <img src="${escapeHtml(imgUrl)}" alt="${safeTitle}" class="showcase-thumb-img" loading="lazy" onerror="window.handleShowcaseImgError(this)" />
                        </div>
                        <button type="button" class="showcase-fav-btn" onclick="window.toggleCardFav(this)" title="Añadir a Favoritos">
                            <svg class="fav-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                            <span class="fav-text">Añadir a Favoritos</span>
                        </button>
                    </div>
                    <div class="showcase-body-col">
                        <div class="showcase-pill-row">
                            <span class="showcase-pill">${escapeHtml(numDisplay)}</span>
                        </div>
                        <h4 class="showcase-title">${safeTitle}</h4>
                        ${safeMeta ? `<span class="showcase-meta">${safeMeta}</span>` : ''}
                        <p class="showcase-desc">${safeDesc}</p>
                    </div>
                </div>
            `;
        }

        // 2. Si no hay internet o estamos offline: NUNCA dejar emojis ni cajas vacías en la lista
        const isOffline = (typeof navigator !== 'undefined' && navigator.onLine === false);
        if (isOffline) {
            return `
                <div class="jarvis-showcase-card no-thumb">
                    <div class="showcase-body-col">
                        <div class="showcase-pill-row">
                            <span class="showcase-pill">${escapeHtml(numDisplay)}</span>
                            <button type="button" class="showcase-fav-btn inline-fav-btn" onclick="window.toggleCardFav(this)" title="Añadir a Favoritos">
                                <svg class="fav-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                </svg>
                                <span class="fav-text">Añadir a Favoritos</span>
                            </button>
                        </div>
                        <h4 class="showcase-title">${safeTitle}</h4>
                        ${safeMeta ? `<span class="showcase-meta">${safeMeta}</span>` : ''}
                        <p class="showcase-desc">${safeDesc}</p>
                    </div>
                </div>
            `;
        }

        // 3. Con internet disponible: resolver automáticamente fotografías e ilustraciones reales
        return `
            <div class="jarvis-showcase-card has-thumb is-loading-img" data-auto-img-query="${safeTitle}">
                <div class="showcase-thumb-col">
                    <div class="showcase-thumb-box showcase-skeleton-box">
                        <div class="showcase-shimmer"></div>
                    </div>
                    <button type="button" class="showcase-fav-btn" onclick="window.toggleCardFav(this)" title="Añadir a Favoritos">
                        <svg class="fav-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                        </svg>
                        <span class="fav-text">Añadir a Favoritos</span>
                    </button>
                </div>
                <div class="showcase-body-col">
                    <div class="showcase-pill-row">
                        <span class="showcase-pill">${escapeHtml(numDisplay)}</span>
                    </div>
                    <h4 class="showcase-title">${safeTitle}</h4>
                    ${safeMeta ? `<span class="showcase-meta">${safeMeta}</span>` : ''}
                    <p class="showcase-desc">${safeDesc}</p>
                </div>
            </div>
        `;
    }

    function parseShowcaseItem(rawItem, idx) {
        let s = rawItem.trim();
        let numStr = `${idx + 1}`;
        let title = `Opción ${idx + 1}`;
        let meta = '';
        let desc = '';
        let imgUrl = null;

        // 1. Extraer imagen si existe: ![alt](url)
        const imgMatch = s.match(/!\[([^\]]*)\]\(([^)]+)\)/);
        if (imgMatch) {
            imgUrl = imgMatch[2].trim();
            s = s.replace(imgMatch[0], '').trim();
        }

        // 2. Extraer número de tarjeta
        const numMatch = s.match(/^#{1,4}\s*0?(\d+)[.\-:\s]\s*/i);
        if (numMatch) {
            numStr = numMatch[1];
            s = s.substring(numMatch[0].length).trim();
        }

        // 3. Caso A: Multilínea
        const lines = s.split('\n').map(l => l.trim()).filter(Boolean);
        if (lines.length >= 2) {
            title = lines[0].replace(/^0?\d+[.\-:\s]\s*/, '').replace(/^[*_#\s]+|[*_#\s]+$/g, '').trim();

            let descStartIdx = 1;
            const l1 = lines[1];
            const mBold = l1.match(/^\*\*([^*]+)\*\*$/);
            const hasSep = l1.includes('·') || l1.includes('/') || l1.includes(' - ');
            if (mBold) {
                meta = mBold[1].trim();
                descStartIdx = 2;
            } else if ((hasSep || l1.length < 50) && !l1.endsWith('.') && !l1.includes(':')) {
                meta = l1.replace(/^[*_]+|[*_]+$/g, '').trim();
                descStartIdx = 2;
            }
            desc = lines.slice(descStartIdx).join(' ').trim();
        } else {
            // Caso B: Línea única compacta
            const boldMetaMatch = s.match(/^([^\n*]+?)\s+\*\*([^*]+)\*\*\s+([\s\S]+)$/);
            if (boldMetaMatch) {
                title = boldMetaMatch[1].replace(/^0?\d+[.\-:\s]\s*/, '').trim();
                meta = boldMetaMatch[2].trim();
                desc = boldMetaMatch[3].trim();
            } else {
                const sepMetaMatch = s.match(/\b([A-ZÁÉÍÓÚ][a-zñáéíóú]+\s*(?:·|\/)\s*[A-ZÁÉÍÓÚ][a-zñáéíóú]+)\b/);
                if (sepMetaMatch && sepMetaMatch.index > 0 && sepMetaMatch.index < 50) {
                    const matchPos = sepMetaMatch.index;
                    title = s.substring(0, matchPos).replace(/^0?\d+[.\-:\s]\s*/, '').trim();
                    meta = sepMetaMatch[1].trim();
                    desc = s.substring(matchPos + sepMetaMatch[0].length).trim();
                } else {
                    const dotMatch = s.match(/^([^.?!:]{2,45}[:.]?)\s+([A-ZÁÉÍÓÚ][\s\S]+)$/);
                    if (dotMatch) {
                        title = dotMatch[1].replace(/^0?\d+[.\-:\s]\s*/, '').replace(/[:.]$/, '').trim();
                        desc = dotMatch[2].trim();
                    } else {
                        title = s.replace(/^0?\d+[.\-:\s]\s*/, '').trim();
                    }
                }
            }
        }

        title = title.replace(/^[*_]+|[*_]+$/g, '').replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();
        meta = meta.replace(/^[*_]+|[*_]+$/g, '').replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();

        return { numStr, title, meta, desc, imgUrl };
    }

    function extractShowcaseCardsFromMarkdown(text, visualBlocks) {
        if (!text) return text;

        // Patrón A: Encabezados numerados tipo ### 01. Título o ### 1. Título o ## 1 - Título
        const cardBlockRegex = /(?:^|\n|\s)(#{2,3}\s*0?\d+[.\-:\s]\s*[\s\S]*?)(?=(?:\s*#{2,3}\s*0?\d+[.\-:\s]\s*|\s*(?:__|@@|%%)(?:JARVIS_)?VISUAL_BLOCK_|\s*<div class="jarvis-visual-mount"|\s*JARVIS|\s*¿?\s*QUÉ\s+(?:TE\s+APETECE|DESEAS|QUIERES)\s+EXPLORAR|\s*#\s+[A-ZÁÉÍÓÚ]|\s*---|$))/gi;
        const matches = Array.from(text.matchAll(cardBlockRegex));

        if (matches.length >= 1) {
            let firstIndex = matches[0].index;
            let lastMatch = matches[matches.length - 1];
            let totalSpanEnd = lastMatch.index + lastMatch[0].length;

            let cardsHtml = '';
            matches.forEach((m, idx) => {
                const parsed = parseShowcaseItem(m[1], idx);
                cardsHtml += buildShowcaseCardHtml(parsed.numStr, parsed.title, parsed.meta, parsed.desc, parsed.imgUrl);
            });

            if (cardsHtml) {
                const gridHtml = `<div class="jarvis-showcase-grid">${cardsHtml}</div>`;
                const idx = visualBlocks.length;
                visualBlocks.push({ html: gridHtml, fallback: text.substring(firstIndex, totalSpanEnd) });

                const before = text.substring(0, firstIndex);
                const after = text.substring(totalSpanEnd);
                return `${before}\n\n<div class="jarvis-visual-mount" data-block-id="${idx}"></div>\n@@JARVIS_VISUAL_BLOCK_${idx}@@\n\n${after}`;
            }
        }

        // Patrón B: Tarjetas con número suelto (ej. 01\n\nPizza napolitana\n\nNápoles · Campania)
        const patternBRegex = /(?:^|\n)[ \t]*(?:0?(\d{1,2}))\s*\n+([A-ZÁÉÍÓÚ][^\n]+)\n+(?:!\[[^\]]*\]\(([^)]+)\)\s*\n+)?(?:\*\*([^\*\n]+)\*\*|([A-ZÁÉÍÓÚa-zñáéíóú\s]+·[^\n]+))\n+([^\n]+(?:\n+(?![0-9]{1,2}\s*\n|[A-ZÁÉÍÓÚ·\s]+·|JARVIS|¿?\s*QUÉ\s+(?:TE\s+APETECE|DESEAS|QUIERES)\s+EXPLORAR)[^\n]+)*)/g;
        const bMatches = Array.from(text.matchAll(patternBRegex));
        if (bMatches.length >= 2) {
            let firstIndex = bMatches[0].index;
            let lastMatch = bMatches[bMatches.length - 1];
            let totalSpanEnd = lastMatch.index + lastMatch[0].length;

            let cardsHtml = '';
            bMatches.forEach((m, idx) => {
                const numStr = m[1] || `${idx + 1}`;
                const title = m[2].trim();
                const imgUrl = m[3] ? m[3].trim() : null;
                const meta = (m[4] || m[5] || '').trim();
                const desc = (m[6] || '').trim().replace(/\n+/g, ' ');
                cardsHtml += buildShowcaseCardHtml(numStr, title, meta, desc, imgUrl);
            });

            if (cardsHtml) {
                const gridHtml = `<div class="jarvis-showcase-grid">${cardsHtml}</div>`;
                const idx = visualBlocks.length;
                visualBlocks.push({ html: gridHtml, fallback: text.substring(firstIndex, totalSpanEnd) });

                const before = text.substring(0, firstIndex);
                const after = text.substring(totalSpanEnd);
                return `${before}\n\n<div class="jarvis-visual-mount" data-block-id="${idx}"></div>\n@@JARVIS_VISUAL_BLOCK_${idx}@@\n\n${after}`;
            }
        }

        // Patrón C: Listas numeradas estándar con negrita (ej. 1. **Pizza napolitana** (Nápoles · Campania): Masa...)
        const patternCRegex = /(?:^|\n)[ \t]*(\d{1,2})\.\s+\*\*([^*]+)\*\*(?:\s*[(·\-]\s*([^):\n]+)[):\-])?\s*[:\-]?\s*([^\n]+(?:\n+(?!(?:\d{1,2}\.\s+\*\*|JARVIS|¿?\s*QUÉ\s+(?:TE\s+APETECE|DESEAS|QUIERES)\s+EXPLORAR|#{1,3}\s+|---|__(?:VISUAL_BLOCK_)|@@|<div class="jarvis-visual-mount"))[^\n]+)*)/gi;
        const cMatches = Array.from(text.matchAll(patternCRegex));
        if (cMatches.length >= 2) {
            let firstIndex = cMatches[0].index;
            let lastMatch = cMatches[cMatches.length - 1];
            let totalSpanEnd = lastMatch.index + lastMatch[0].length;

            let cardsHtml = '';
            cMatches.forEach((m, idx) => {
                const numStr = m[1] || `${idx + 1}`;
                const title = m[2].trim();
                const meta = (m[3] || '').trim();
                const desc = (m[4] || '').trim().replace(/\n+/g, ' ');
                cardsHtml += buildShowcaseCardHtml(numStr, title, meta, desc, null);
            });

            if (cardsHtml) {
                const gridHtml = `<div class="jarvis-showcase-grid">${cardsHtml}</div>`;
                const idx = visualBlocks.length;
                visualBlocks.push({ html: gridHtml, fallback: text.substring(firstIndex, totalSpanEnd) });

                const before = text.substring(0, firstIndex);
                const after = text.substring(totalSpanEnd);
                return `${before}\n\n<div class="jarvis-visual-mount" data-block-id="${idx}"></div>\n@@JARVIS_VISUAL_BLOCK_${idx}@@\n\n${after}`;
            }
        }

        return text;
    }

    function extractJsonArray(str) {
        if (!str) return null;
        let s = str.trim();
        s = s.replace(/^`+[a-zA-Z0-9_\-]*\s*/, '').replace(/`+$/, '').trim();

        try {
            const val = JSON.parse(s);
            if (Array.isArray(val)) return val;
            if (val && Array.isArray(val.items)) return val.items;
            if (val && Array.isArray(val.cards)) return val.cards;
        } catch (e) {}

        const start = s.indexOf('[');
        const end = s.lastIndexOf(']');
        if (start !== -1 && end !== -1 && end > start) {
            const sub = s.substring(start, end + 1);
            try {
                const val = JSON.parse(sub);
                if (Array.isArray(val)) return val;
            } catch (e) {
                try {
                    const cleaned = sub.replace(/,\s*([\]}])/g, '$1');
                    const val = JSON.parse(cleaned);
                    if (Array.isArray(val)) return val;
                } catch (e2) {}
            }
        }
        return null;
    }

    function extractJsonObject(str) {
        if (!str) return null;
        let s = str.trim();
        s = s.replace(/^`+[a-zA-Z0-9_\-]*\s*/, '').replace(/`+$/, '').trim();
        try {
            const val = JSON.parse(s);
            if (typeof val === 'object' && val !== null) return val;
        } catch (e) {}
        const start = s.indexOf('{');
        const end = s.lastIndexOf('}');
        if (start !== -1 && end !== -1 && end > start) {
            const sub = s.substring(start, end + 1);
            try {
                return JSON.parse(sub);
            } catch (e) {
                try {
                    const cleaned = sub.replace(/,\s*([\]}])/g, '$1');
                    return JSON.parse(cleaned);
                } catch (e2) {}
            }
        }
        return null;
    }

    function renderCardsBlock(jsonStr) {
        const items = extractJsonArray(jsonStr);
        if (!items || !Array.isArray(items) || items.length === 0) return null;
        let cardsHtml = '';
        items.forEach((item, idx) => {
            const numStr = `${idx + 1}`;
            const title = item.title || item.name || `Opción ${idx + 1}`;
            const meta = item.subtitle || item.badge || item.region || item.category || '';
            const desc = item.desc || item.content || item.description || '';
            const img = item.image || item.img || item.imgUrl || null;
            cardsHtml += buildShowcaseCardHtml(numStr, title, meta, desc, img);
        });
        return `<div class="jarvis-showcase-grid">${cardsHtml}</div>`;
    }

    function renderComparativaBlock(jsonStr) {
        const data = extractJsonObject(jsonStr);
        if (!data) return null;
        const title = data.title ? `<div class="table-card-header"><span class="table-icon">📊</span><h4 class="table-title">${escapeHtml(data.title)}</h4></div>` : '';
        const headers = Array.isArray(data.headers) ? data.headers : [];
        const rows = Array.isArray(data.rows) ? data.rows : [];

        let thHtml = '';
        headers.forEach(h => {
            thHtml += `<th>${escapeHtml(String(h))}</th>`;
        });

        let trHtml = '';
        rows.forEach(r => {
            trHtml += '<tr>';
            if (Array.isArray(r)) {
                r.forEach(c => {
                    trHtml += `<td>${escapeHtml(String(c))}</td>`;
                });
            }
            trHtml += '</tr>';
        });

        return `
            <div class="jarvis-table-card">
                ${title}
                <div class="table-responsive-wrapper">
                    <table class="jarvis-glass-table">
                        ${thHtml ? `<thead><tr>${thHtml}</tr></thead>` : ''}
                        <tbody>${trHtml}</tbody>
                    </table>
                </div>
            </div>
        `;
    }

    function renderChecklistBlock(jsonStr) {
        const data = extractJsonObject(jsonStr);
        if (!data) return null;
        const title = escapeHtml(data.title || "Guía de Estudio y Verificación");
        const sections = Array.isArray(data.sections) ? data.sections : (data.items ? [{ category: "Temas", items: data.items }] : []);

        let totalItems = 0;
        sections.forEach(s => {
            if (Array.isArray(s.items)) totalItems += s.items.length;
        });

        let sectionsHtml = '';
        sections.forEach(sec => {
            const catName = escapeHtml(sec.category || "General");
            const items = Array.isArray(sec.items) ? sec.items : [];
            let itemsHtml = '';
            items.forEach(it => {
                const text = typeof it === 'string' ? it : (it.text || it.name || '');
                const isChecked = typeof it === 'object' && it.checked ? ' checked' : '';
                itemsHtml += `
                    <div class="checklist-item${isChecked}" onclick="window.toggleChecklistItem(this)">
                        <span class="custom-checkbox"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg></span>
                        <span class="item-text">${escapeHtml(text)}</span>
                    </div>
                `;
            });

            sectionsHtml += `
                <div class="checklist-section">
                    <h5 class="section-badge">${catName}</h5>
                    <div class="checklist-items">${itemsHtml}</div>
                </div>
            `;
        });

        return `
            <div class="jarvis-checklist-card">
                <div class="checklist-header">
                    <div class="checklist-title-group">
                        <span class="checklist-icon">📋</span>
                        <h4 class="checklist-title">${title}</h4>
                    </div>
                    <div class="checklist-progress-badge">
                        <span class="checklist-count">0/${totalItems}</span>
                        <div class="checklist-progress-bar"><div class="progress-fill" style="width: 0%"></div></div>
                    </div>
                </div>
                <div class="checklist-sections">${sectionsHtml}</div>
            </div>
        `;
    }

    function formatAssistantMessage(text) {
        if (!text) return "";
        let working = beautifyMarkdownText(text);

        // 1. Extraer y proteger bloques visuales interactivos (acepta 1 a 3 backticks, con o sin saltos de línea)
        const visualBlocks = [];
        const makeBlockPlaceholder = (idx) => `\n\n<div class="jarvis-visual-mount" data-block-id="${idx}"></div>\n@@JARVIS_VISUAL_BLOCK_${idx}@@\n\n`;

        working = working.replace(/`{1,3}(?:cards|flashcards|bento)\b\s*([\s\S]*?)(?:`{1,3}|$)/gi, (match, json) => {
            const rendered = renderCardsBlock(json);
            if (rendered) {
                const idx = visualBlocks.length;
                visualBlocks.push({ html: rendered, fallback: match });
                return makeBlockPlaceholder(idx);
            }
            return match;
        });

        working = working.replace(/`{1,3}(?:comparativa|comparison)\b\s*([\s\S]*?)(?:`{1,3}|$)/gi, (match, json) => {
            const rendered = renderComparativaBlock(json);
            if (rendered) {
                const idx = visualBlocks.length;
                visualBlocks.push({ html: rendered, fallback: match });
                return makeBlockPlaceholder(idx);
            }
            return match;
        });

        working = working.replace(/`{1,3}checklist\b\s*([\s\S]*?)(?:`{1,3}|$)/gi, (match, json) => {
            const rendered = renderChecklistBlock(json);
            if (rendered) {
                const idx = visualBlocks.length;
                visualBlocks.push({ html: rendered, fallback: match });
                return makeBlockPlaceholder(idx);
            }
            return match;
        });

        // Detectar bloque json que contenga un array de cards
        working = working.replace(/`{1,3}json\b\s*(\[\s*\{[\s\S]*?\}\s*\])\s*(?:`{1,3}|$)/gi, (match, json) => {
            const rendered = renderCardsBlock(json);
            if (rendered) {
                const idx = visualBlocks.length;
                visualBlocks.push({ html: rendered, fallback: match });
                return makeBlockPlaceholder(idx);
            }
            return match;
        });

        // Si todo el mensaje recibido es un array JSON de tarjetas sin backticks
        if (working.trim().startsWith('[') && working.trim().endsWith(']')) {
            const rendered = renderCardsBlock(working);
            if (rendered) {
                return rendered;
            }
        }

        // 1.5 Detectar y transformar tarjetas showcase de Markdown en componentes visuales interactivos
        working = extractShowcaseCardsFromMarkdown(working, visualBlocks);

        // 1.6 Detectar sección de sugerencias de exploración interactiva (JARVIS · ¿QUÉ TE APETECE EXPLORAR?)
        const suggestionHeaderRegex = /(?:(?:JARVIS\s*[·•-]?\s*)?¿?\s*QUÉ\s+(?:TE\s+APETECE|DESEAS|QUIERES)\s+EXPLORAR\??|EXPLORAR:)\s*\n+([\s\S]+?)(?=(?:\n*#{2,3}|\n*(?:__|@@|%%)(?:JARVIS_)?VISUAL_BLOCK_|\n*<div class="jarvis-visual-mount"|\n*#\s+[A-ZÁÉÍÓÚ]|---|$))/i;
        const suggMatch = working.match(suggestionHeaderRegex);
        if (suggMatch) {
            const rawList = suggMatch[1].trim();
            const items = [];
            const itemLines = rawList.split('\n');
            itemLines.forEach(l => {
                const cleanItem = l.replace(/^[ \t]*[-*•]\s*/, '').replace(/[*_~`]/g, '').trim();
                if (cleanItem && cleanItem.length < 120 && !cleanItem.startsWith('#')) {
                    items.push(cleanItem);
                }
            });

            if (items.length > 0) {
                let chipsHtml = `
                    <div class="jarvis-suggestion-chips-block">
                        <div class="chips-header">
                            <span class="chips-prefix">JARVIS</span>
                            <span class="chips-sep">·</span>
                            <span class="chips-title">¿QUÉ TE APETECE EXPLORAR?</span>
                        </div>
                        <div class="chips-row">
                `;
                items.forEach(it => {
                    const escapedPrompt = it.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                    chipsHtml += `
                        <button type="button" class="jarvis-suggestion-chip" onclick="window.sendSuggestedPrompt('${escapedPrompt}')">
                            <span>${escapeHtml(it)}</span>
                            <svg class="chip-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                        </button>
                    `;
                });
                chipsHtml += `</div></div>`;
                const sIdx = visualBlocks.length;
                visualBlocks.push({ html: chipsHtml, fallback: suggMatch[0] });
                working = working.substring(0, suggMatch.index) + makeBlockPlaceholder(sIdx) + working.substring(suggMatch.index + suggMatch[0].length);
            }
        }

        // 2. Normalizar texto markdown general
        const clean = beautifyMarkdownText(working);

        // 3. Renderizar Markdown (marked o nativo)
        let html = "";
        if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
            try {
                marked.setOptions({
                    breaks: true,
                    gfm: true
                });
                html = marked.parse(clean);
            } catch (err) {
                console.warn("[Markdown] Error en marked.parse, usando parser nativo:", err);
                html = renderMarkdownNative(clean);
            }
        } else {
            html = renderMarkdownNative(clean);
        }

        // 4. Restaurar bloques visuales interactivos protegidos con regex resiliente
        visualBlocks.forEach((block, idx) => {
            const vHtml = (typeof block === 'object' && block !== null) ? block.html : block;
            const fallback = (typeof block === 'object' && block !== null) ? (block.fallback || "") : "";
            const safeContent = (vHtml && typeof vHtml === 'string' && vHtml.trim())
                ? vHtml
                : (fallback ? renderMarkdownNative(fallback) : "");

            const blockRegex = new RegExp(
                `(?:<p>\\s*)?(?:<div class="jarvis-visual-mount" data-block-id="${idx}"><\\/div>|(?:<strong>|<b>)?(?:__|@@|%%)?(?:JARVIS_)?VISUAL_BLOCK_${idx}(?:__|@@|%%)?(?:<\\/b>|<\\/strong>)?)(?:\\s*<\\/p>)?`,
                'gi'
            );
            html = html.replace(blockRegex, () => safeContent);
        });

        // 4.1 Limpieza final de seguridad: NUNCA exponer marcadores técnicos residuales ni mounts vacíos
        html = html.replace(
            /(?:<p>\s*)?(?:<div class="jarvis-visual-mount"[^>]*><\/div>|(?:<strong>|<b>)?(?:__|@@|%%)?(?:JARVIS_)?VISUAL_BLOCK_\d+(?:__|@@|%%)?(?:<\/b>|<\/strong>)?)(?:\s*<\/p>)?/gi,
            ''
        );
        html = html.replace(/<p>\s*(?:<br\s*\/?>)?\s*<\/p>/gi, '');

        // 5. Convertir casillas inline de tareas [ ] o ☐ en checkboxes interactivos
        html = html.replace(/(?:<li>|\n|^)[ \t]*(?:\[ \]|☐)\s*([^\n<]+)/g, (match, txt) => {
            return `<div class="checklist-item inline" onclick="window.toggleChecklistItem(this)"><span class="custom-checkbox"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg></span><span class="item-text">${txt.trim()}</span></div>`;
        });
        html = html.replace(/(?:<li>|\n|^)[ \t]*(?:\[x\]|☑)\s*([^\n<]+)/g, (match, txt) => {
            return `<div class="checklist-item inline checked" onclick="window.toggleChecklistItem(this)"><span class="custom-checkbox"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg></span><span class="item-text">${txt.trim()}</span></div>`;
        });
        // 6. Activar resolución asíncrona de imágenes reales para tarjetas showcase
        setTimeout(() => {
            if (typeof window.resolveShowcaseCardImages === 'function') {
                window.resolveShowcaseCardImages();
            }
        }, 40);

        return html;
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
                        const chunkText = event.text || "";
                        const needsDoubleBreak = chunkText.startsWith("#") || chunkText.startsWith("###") || chunkText.startsWith("-") || chunkText.startsWith("*") || /^\d+\./.test(chunkText);
                        const sep = !uiState.activeAssistantBubble.dataset.rawText ? "" : (needsDoubleBreak ? "\n\n" : " ");
                        uiState.activeAssistantBubble.dataset.rawText += sep + chunkText;
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
                        <span class="msg-sender-tag">
                            <span class="pulse-indicator"></span>
                            <span class="sender-name">JARVIS</span>
                        </span>
                        <span class="msg-time-tag">${new Date().toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'})}</span>
                    </div>
                    <div class="msg-content"><span style="display:inline-flex; align-items:center; gap:6px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00F2FE" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg> <strong>${title}</strong></span><br>${message}</div>
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

    // --- GESTOR DE VENTANA CONVERSACIONAL Y FLUIDEZ DE DIÁLOGO MANOS LIBRES ---
    let conversationWindowTimer = null;
    let speechSilenceTimer = null;
    let lastProcessedTranscript = "";
    const CONVERSATION_WINDOW_MS = 8000; // 8 segundos de atención tras hablar

    const WAKE_ACKNOWLEDGMENTS = [
        "¿Dígame, señor?",
        "¿Sí? Te escucho.",
        "¿En qué puedo ayudarte?",
        "A tus órdenes."
    ];

    function playSpokenAck() {
        playActivationChime();
        const phrase = WAKE_ACKNOWLEDGMENTS[Math.floor(Math.random() * WAKE_ACKNOWLEDGMENTS.length)];
        enqueueTTSUrl(`/api/tts/stream?text=${encodeURIComponent(phrase)}`);
        openConversationalWindow(8000);
    }

    function openConversationalWindow(durationMs = CONVERSATION_WINDOW_MS) {
        if (!continuousEnabled) return;
        // Si hay música sonando y no fue activación manual del usuario (tap en micrófono u orbe),
        // no abrir ventana de escucha para evitar capturar la letra del altavoz
        if ((window.isStudioPlaying || window.isMusicPlaying) && !window.isManualMicTrigger) return;
        window.isManualMicTrigger = false;

        isConversationActive = true;
        if (conversationWindowTimer) clearTimeout(conversationWindowTimer);

        // Asegurar que el reconocimiento de voz esté activo y escuchando
        startContinuousListening(true);

        setVoiceState("LISTENING", "Te escucho...");
        if (handsfreeHint) handsfreeHint.textContent = "Conversación abierta (8s)";

        conversationWindowTimer = setTimeout(() => {
            closeConversationalWindow();
        }, durationMs);
    }

    function resetConversationTimer(durationMs = CONVERSATION_WINDOW_MS) {
        if (conversationWindowTimer) clearTimeout(conversationWindowTimer);
        if (isConversationActive) {
            conversationWindowTimer = setTimeout(() => {
                closeConversationalWindow();
            }, durationMs);
        }
    }

    function closeConversationalWindow() {
        if (conversationWindowTimer) clearTimeout(conversationWindowTimer);
        conversationWindowTimer = null;
        isConversationActive = false;
        lastProcessedTranscript = "";

        if (uiState.voiceState === "LISTENING") {
            setVoiceState("IDLE", "Listo (escuchando 'Jarvis'...)");
            if (handsfreeHint) handsfreeHint.textContent = "Manos Libres Activo";
        }
    }

    // --- RECONOCIMIENTO DE VOZ WEB SPEECH API CON VAD Y BARGE-IN ---
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
                if (!rawTranscript) return;

                // 1. BARGE-IN REAL: Si JARVIS está hablando y el usuario empieza a hablar
                const isJarvisSpeaking = (uiState.voiceState === "SPEAKING" || window.isSpeakingAudio || currentTTSAudio !== null);
                if (isJarvisSpeaking && rawTranscript.length > 0) {
                    console.log("[Barge-In] Usuario habló mientras JARVIS hablaba. Interrumpiendo reproducción...");
                    clearTTSAudioQueue();
                    uiState.voiceState = "INTERRUPTED";
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        try { ws.send(JSON.stringify({ type: "barge_in" })); } catch (e) {}
                    }
                    setVoiceState("LISTENING", "Te escucho...");
                    openConversationalWindow(8000);
                }

                // 2. FEEDBACK VISUAL EN TIEMPO REAL: Mostrar lo que el usuario va diciendo
                if (interimTranscript.trim() && uiState.voiceState === "LISTENING" && voiceStatusText) {
                    voiceStatusText.textContent = `Escuchando: "${interimTranscript.trim()}"`;
                }

                // 3. MODO STANDBY (esperando wake word "Jarvis")
                if (!isConversationActive) {
                    if (WAKE_WORD_REGEX.test(rawTranscript)) {
                        let cleanCommand = rawTranscript.replace(WAKE_WORD_REGEX, '').trim();
                        // Si dijo solo "Jarvis" o "Oye Jarvis"
                        if (cleanCommand.length <= 2) {
                            playSpokenAck();
                        } else {
                            // Dijo "Jarvis, [comando]"
                            playActivationChime();
                            isConversationActive = true;
                            setVoiceState("PROCESSING", "Procesando...");
                            handleSendMessage(cleanCommand);
                        }
                    }
                    return;
                }

                // 4. MODO CONVERSACIÓN ACTIVA (dentro de la ventana conversacional fluida)
                resetConversationTimer(8000);

                // 4.1 Debounce inteligente de silencio en interimResults (reduce latencia de turno en 900ms)
                if (interimTranscript.trim().length > 3) {
                    if (speechSilenceTimer) clearTimeout(speechSilenceTimer);
                    speechSilenceTimer = setTimeout(() => {
                        if (isConversationActive && interimTranscript.trim().length > 3 && uiState.voiceState !== "PROCESSING") {
                            const clean = interimTranscript.replace(WAKE_WORD_REGEX, '').trim() || interimTranscript.trim();
                            if (clean && clean !== lastProcessedTranscript) {
                                lastProcessedTranscript = clean;
                                if (conversationWindowTimer) clearTimeout(conversationWindowTimer);
                                handleSendMessage(clean);
                            }
                        }
                    }, 850);
                }

                // 4.2 Envío inmediato al completarse el turno final de voz
                if (finalTranscript.trim().length > 1) {
                    if (speechSilenceTimer) clearTimeout(speechSilenceTimer);
                    const cleanFinal = finalTranscript.replace(WAKE_WORD_REGEX, '').trim() || finalTranscript.trim();
                    if (cleanFinal && cleanFinal !== lastProcessedTranscript) {
                        lastProcessedTranscript = cleanFinal;
                        if (conversationWindowTimer) clearTimeout(conversationWindowTimer);
                        handleSendMessage(cleanFinal);
                    }
                }
            };

            rec.onerror = () => {
                isSpeechActive = false;
            };

            rec.onend = () => {
                isSpeechActive = false;
                if (continuousEnabled && !window.isStudioPlaying && !window.isMusicPlaying) {
                    setTimeout(() => {
                        if (!isSpeechActive && !window.isStudioPlaying && !window.isMusicPlaying) {
                            startContinuousListening();
                        }
                    }, 120);
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
        // Si hay música activa y no es una activación manual explícita, no tomar el micrófono
        if ((window.isStudioPlaying || window.isMusicPlaying) && !window.isManualMicTrigger) return;
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

    // Funciones globales para coordinar silencio de micrófono con reproducción musical
    window.stopSpeechForMusicPlayback = function() {
        window.isMusicPlaying = true;
        if (isSpeechActive && recognition) {
            try { recognition.stop(); } catch (e) {}
            isSpeechActive = false;
        }
        if (conversationWindowTimer) {
            clearTimeout(conversationWindowTimer);
            conversationWindowTimer = null;
        }
        isConversationActive = false;
        lastProcessedTranscript = "";
        if (speechSilenceTimer) {
            clearTimeout(speechSilenceTimer);
            speechSilenceTimer = null;
        }
        if (uiState.voiceState === "LISTENING") {
            setVoiceState("IDLE", "Reproduciendo música...");
        }
    };

    window.resumeSpeechAfterMusicPlayback = function() {
        window.isMusicPlaying = false;
        if (continuousEnabled) {
            setTimeout(() => {
                if (!window.isStudioPlaying && !window.isMusicPlaying && !isSpeechActive) {
                    startContinuousListening();
                }
            }, 300);
        }
    };

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
                <div class="msg-header">
                    <span class="msg-sender-tag">
                        <span class="pulse-indicator"></span>
                        <span class="sender-name">JARVIS AI</span>
                    </span>
                    <span class="msg-time-tag">${timeStr}</span>
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
                    const errorMsg = (resJson && resJson.error && resJson.error.message) || data.error || (typeof data === 'string' ? data : 'No se pudo leer el archivo.');
                    alert(errorMsg);
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
                    <span style="display:inline-flex; align-items:center; gap:5px;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#00F2FE" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        Generada con IA
                    </span>
                    <span style="opacity:0.8;">Guardada en Imágenes</span>
                </div>
            `;
            parentItem.appendChild(imgCard);
            scrollToBottom();
        }
        if (generatedDoc && !parentItem.querySelector('.generated-doc-card')) {
            const docCard = document.createElement('div');
            docCard.className = 'generated-doc-card';
            const iconSvg = (generatedDoc.format === 'DOCX') 
                ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38E1FF" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`
                : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF5252" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 13v4M9 15h2a1 1 0 0 0 0-2H9z"/></svg>`;
            docCard.innerHTML = `
                <div class="generated-doc-icon">${iconSvg}</div>
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
                        uiState.activeAssistantBubble.innerHTML = formatAssistantMessage(data.text);
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
                        uiState.activeAssistantBubble.innerHTML = formatAssistantMessage(data.text || "No pude procesar la solicitud.");
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
                    <span class="chat-action-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFB300" stroke-width="2.2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span>
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
                            <span class="chat-action-icon"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00F2FE" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 14"/></svg></span>
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
                            <span class="chat-action-icon"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#FF5252" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg></span>
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
                const iconSvg = (attachment.file_type === 'pdf')
                    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF5252" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 13v4M9 15h2a1 1 0 0 0 0-2H9z"/></svg>`
                    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00F2FE" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`;
                attachHtml = `
                    <div class="chat-attached-doc">
                        <span class="chat-doc-icon">${iconSvg}</span>
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
                window.isManualMicTrigger = true;
                if (window.isStudioPlaying && isPlayerReady && ytPlayer && typeof ytPlayer.pauseVideo === 'function') {
                    window.wasMusicPlayingBeforeMic = true;
                    ytPlayer.pauseVideo();
                }
                playActivationChime();
                openConversationalWindow(8000);
            }
        });
    }

    if (jarvisOrb) {
        const triggerOrbActivation = () => {
            clearTTSAudioQueue();
            if (SpeechRecognition) {
                window.isManualMicTrigger = true;
                if (window.isStudioPlaying && isPlayerReady && ytPlayer && typeof ytPlayer.pauseVideo === 'function') {
                    window.wasMusicPlayingBeforeMic = true;
                    ytPlayer.pauseVideo();
                }
                playActivationChime();
                openConversationalWindow(8000);
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

    // --- MEMORIA PERMANENTE DINÁMICA (CRUD EN VIVO Y SYNC CON SQLITE) ---
    let currentMemCat = 'all';
    let liveMemories = [
        { id: 1, cat: 'gaming', key: 'juegos_favoritos', val: 'Devil May Cry 3 y 5 (Estilo Hack and Slash)' },
        { id: 2, cat: 'music', key: 'artista_favorita', val: 'Billie Eilish (le fascina su voz y estilo melódico)' },
        { id: 3, cat: 'music', key: 'banda_principal', val: 'Queen (Rock Clásico)' },
        { id: 4, cat: 'music', key: 'bandas_destacadas', val: 'My Chemical Romance, System of a Down, Scorpions, Audioslave' },
        { id: 5, cat: 'preference', key: 'color_favorito', val: 'Azul oscuro' },
        { id: 6, cat: 'preference', key: 'estilo_comunicacion', val: 'Compañera conversacional cercana, adaptativa y estructurada (listas y explicaciones claras)' },
        { id: 7, cat: 'preference', key: 'estilo_humor', val: 'Humor inteligente y oportuno (65/100), ironía ligera sin forzar chistes' },
        { id: 8, cat: 'lifestyle', key: 'nombre', val: 'Jhonatan David Torres Patiño (Alias: Dante)' },
        { id: 9, cat: 'lifestyle', key: 'hobby', val: 'Programación en Python' },
        { id: 10, cat: 'lifestyle', key: 'deporte', val: 'Ajedrez' },
        { id: 11, cat: 'lifestyle', key: 'horario_universidad', val: 'Lunes a Viernes | 18:00 - 22:00' }
    ];

    const memoryDrawer = document.getElementById('memory-drawer');
    const btnOpenMemory = document.getElementById('btn-open-memory');
    const btnCloseMemory = document.getElementById('btn-close-memory');
    const btnAddMemory = document.getElementById('btn-add-memory');
    const memoryAddBox = document.getElementById('memory-add-box');
    const btnSaveNewMem = document.getElementById('btn-save-new-mem');
    const btnCancelNewMem = document.getElementById('btn-cancel-new-mem');
    const memoryItemsList = document.getElementById('memory-items-list');

    async function fetchLiveMemories() {
        try {
            const res = await fetch('/api/memories');
            if (res.ok) {
                const json = await res.json();
                const items = (json && json.ok && Array.isArray(json.data)) ? json.data : (Array.isArray(json) ? json : []);
                if (items.length > 0) {
                    liveMemories = items;
                }
            }
        } catch (e) {
            console.debug("[Memoria] Usando fallback local para recuerdos:", e);
        }
        renderMemories(currentMemCat);
    }

    function formatKeyTitle(key) {
        if (!key) return "RECUERDO";
        return key.replace(/_/g, ' ').toUpperCase();
    }

    function renderMemories(category = 'all') {
        currentMemCat = category;
        if (!memoryItemsList) return;
        memoryItemsList.innerHTML = '';
        const filtered = category === 'all' ? liveMemories : liveMemories.filter(m => (m.cat || 'general') === category);

        if (filtered.length === 0) {
            memoryItemsList.innerHTML = `
                <div style="text-align:center; padding: 24px 10px; color: var(--text-tertiary); font-size:12.5px;">
                    No hay recuerdos registrados en esta categoría.
                </div>
            `;
            return;
        }

        filtered.forEach(m => {
            const card = document.createElement('div');
            card.className = 'memory-item-card';
            card.dataset.id = m.id || '';

            card.innerHTML = `
                <div class="mem-card-header">
                    <span class="mem-key">#${m.cat || 'general'} • ${formatKeyTitle(m.key)}</span>
                    <div class="mem-card-actions">
                        <button class="mem-action-btn edit" title="Cambiar / Editar" data-action="edit">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        </button>
                        <button class="mem-action-btn del" title="Eliminar" data-action="delete">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        </button>
                    </div>
                </div>
                <div class="mem-val-container">
                    <div class="mem-val">${escapeHtml(m.val || m.value || '')}</div>
                </div>
            `;

            // Acción Editar / Cambiar
            const btnEdit = card.querySelector('[data-action="edit"]');
            btnEdit.addEventListener('click', () => {
                const valContainer = card.querySelector('.mem-val-container');
                const currentVal = m.val || m.value || '';
                valContainer.innerHTML = `
                    <div class="mem-edit-container">
                        <textarea class="mem-input mem-edit-input" rows="2">${escapeHtml(currentVal)}</textarea>
                        <div style="display:flex; justify-content:flex-end; gap:6px;">
                            <button class="mem-btn-sm save btn-save-edit">Guardar</button>
                            <button class="mem-btn-sm cancel btn-cancel-edit">Cancelar</button>
                        </div>
                    </div>
                `;
                const textarea = valContainer.querySelector('.mem-edit-input');
                textarea.focus();

                valContainer.querySelector('.btn-save-edit').addEventListener('click', async () => {
                    const newVal = textarea.value.trim();
                    if (!newVal) return;
                    m.val = newVal;
                    m.value = newVal;

                    if (m.id) {
                        try {
                            await fetch(`/api/memories/${m.id}`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ key: m.key, val: newVal, cat: m.cat })
                            });
                        } catch (err) {
                            console.error("[Memoria] Error actualizando:", err);
                        }
                    }
                    renderMemories(currentMemCat);
                });

                valContainer.querySelector('.btn-cancel-edit').addEventListener('click', () => {
                    renderMemories(currentMemCat);
                });
            });

            // Acción Eliminar
            const btnDel = card.querySelector('[data-action="delete"]');
            btnDel.addEventListener('click', async () => {
                if (confirm(`¿Eliminar el recuerdo de "${formatKeyTitle(m.key)}"?`)) {
                    if (m.id) {
                        try {
                            await fetch(`/api/memories/${m.id}`, { method: 'DELETE' });
                        } catch (err) {
                            console.error("[Memoria] Error eliminando:", err);
                        }
                    }
                    liveMemories = liveMemories.filter(item => item !== m);
                    renderMemories(currentMemCat);
                }
            });

            memoryItemsList.appendChild(card);
        });
    }

    if (btnOpenMemory && memoryDrawer) {
        btnOpenMemory.addEventListener('click', () => {
            fetchLiveMemories();
            memoryDrawer.classList.toggle('open');
        });
    }
    if (btnCloseMemory && memoryDrawer) {
        btnCloseMemory.addEventListener('click', () => {
            memoryDrawer.classList.remove('open');
        });
    }

    if (btnAddMemory && memoryAddBox) {
        btnAddMemory.addEventListener('click', () => {
            const isVisible = memoryAddBox.style.display !== 'none';
            memoryAddBox.style.display = isVisible ? 'none' : 'flex';
            if (!isVisible) {
                document.getElementById('new-mem-key')?.focus();
            }
        });
    }

    if (btnCancelNewMem && memoryAddBox) {
        btnCancelNewMem.addEventListener('click', () => {
            memoryAddBox.style.display = 'none';
        });
    }

    if (btnSaveNewMem && memoryAddBox) {
        btnSaveNewMem.addEventListener('click', async () => {
            const inputKey = document.getElementById('new-mem-key');
            const inputVal = document.getElementById('new-mem-val');
            const selectCat = document.getElementById('new-mem-cat');

            const key = inputKey?.value.trim();
            const val = inputVal?.value.trim();
            const cat = selectCat?.value || 'general';

            if (!key || !val) {
                alert("Por favor ingresa una clave y un valor.");
                return;
            }

            try {
                const res = await fetch('/api/memories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, val, cat })
                });
                if (res.ok) {
                    const data = await res.json();
                    const newMem = (data && data.data) ? data.data : { key, val, cat };
                    liveMemories.unshift(newMem);
                } else {
                    liveMemories.unshift({ key, val, cat });
                }
            } catch (err) {
                liveMemories.unshift({ key, val, cat });
            }

            if (inputKey) inputKey.value = '';
            if (inputVal) inputVal.value = '';
            memoryAddBox.style.display = 'none';
            renderMemories(currentMemCat);
        });
    }

    document.querySelectorAll('.mem-cat-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mem-cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMemories(btn.getAttribute('data-cat') || 'all');
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

    // =========================================================================
    // MODAL DE CONEXIÓN MÓVIL Y ACCESO POR INTERNET (PWA & CLOUDFLARE TUNNEL)
    // =========================================================================
    const btnOpenMobile = document.getElementById('btn-open-mobile');
    const mobileModal = document.getElementById('mobile-connect-modal');
    const btnCloseMobileModal = document.getElementById('btn-close-mobile-modal');
    const mobileModalBackdrop = document.getElementById('mobile-modal-backdrop');
    const qrSvgWrapper = document.getElementById('qr-svg-wrapper');
    const mobileActiveUrl = document.getElementById('mobile-active-url');
    const btnCopyMobileUrl = document.getElementById('btn-copy-mobile-url');
    const btnToggleTunnel = document.getElementById('btn-toggle-tunnel');
    const tunnelStatusDot = document.getElementById('tunnel-status-dot');
    const tunnelStatusLabel = document.getElementById('tunnel-status-label');
    const localIpHint = document.getElementById('local-ip-hint');

    let currentMobileInfo = null;

    async function loadMobileInfo() {
        try {
            if (tunnelStatusLabel) tunnelStatusLabel.textContent = "Consultando estado de red...";
            const res = await fetch('/api/mobile/info');
            if (res.ok) {
                const json = await res.json();
                const data = json.data || {};
                currentMobileInfo = data;
                
                if (qrSvgWrapper && data.qr_svg) {
                    qrSvgWrapper.innerHTML = data.qr_svg;
                }
                const activeUrl = data.internet_url || data.local_url;
                if (mobileActiveUrl) {
                    mobileActiveUrl.value = activeUrl;
                }
                if (localIpHint) {
                    localIpHint.textContent = `Local: ${data.local_url}`;
                }

                if (tunnelStatusDot && tunnelStatusLabel) {
                    if (data.tunnel_active) {
                        tunnelStatusDot.classList.add('active');
                        tunnelStatusLabel.textContent = "Túnel Cloudflare Activo (Acceso Mundial por Internet)";
                        if (btnToggleTunnel) {
                            btnToggleTunnel.textContent = "Desactivar Túnel Internet";
                            btnToggleTunnel.style.background = "rgba(239, 68, 68, 0.25)";
                            btnToggleTunnel.style.borderColor = "rgba(239, 68, 68, 0.5)";
                        }
                    } else {
                        tunnelStatusDot.classList.remove('active');
                        tunnelStatusLabel.textContent = "Modo Red Local Wi-Fi (Túnel Internet inactivo)";
                        if (btnToggleTunnel) {
                            btnToggleTunnel.textContent = "Activar Túnel Internet (HTTPS)";
                            btnToggleTunnel.style.background = "";
                            btnToggleTunnel.style.borderColor = "";
                        }
                    }
                }
            }
        } catch (e) {
            console.warn("[Mobile Connect] Error cargando información:", e);
        }
    }

    if (btnOpenMobile && mobileModal) {
        btnOpenMobile.addEventListener('click', () => {
            mobileModal.style.display = 'flex';
            loadMobileInfo();
        });
    }

    function closeMobileModal() {
        if (mobileModal) mobileModal.style.display = 'none';
    }

    if (btnCloseMobileModal) btnCloseMobileModal.addEventListener('click', closeMobileModal);
    if (mobileModalBackdrop) mobileModalBackdrop.addEventListener('click', closeMobileModal);

    if (btnCopyMobileUrl && mobileActiveUrl) {
        btnCopyMobileUrl.addEventListener('click', () => {
            if (!mobileActiveUrl.value) return;
            navigator.clipboard.writeText(mobileActiveUrl.value).then(() => {
                const orig = btnCopyMobileUrl.textContent;
                btnCopyMobileUrl.textContent = "¡Copiado!";
                setTimeout(() => { btnCopyMobileUrl.textContent = orig; }, 2000);
            }).catch(() => {
                mobileActiveUrl.select();
                document.execCommand('copy');
            });
        });
    }

    if (btnToggleTunnel) {
        btnToggleTunnel.addEventListener('click', async () => {
            const isCurrentlyActive = currentMobileInfo && currentMobileInfo.tunnel_active;
            const endpoint = isCurrentlyActive ? '/api/mobile/tunnel/stop' : '/api/mobile/tunnel/start';
            btnToggleTunnel.disabled = true;
            btnToggleTunnel.textContent = isCurrentlyActive ? "Deteniendo..." : "Conectando túnel seguro...";
            try {
                const res = await fetch(endpoint, { method: 'POST' });
                await loadMobileInfo();
            } catch (e) {
                console.error("[Tunnel Action Error]", e);
            } finally {
                btnToggleTunnel.disabled = false;
            }
        });
    }

    // --- DESBLOQUEO UNIVERSAL DE AUDIO PARA CELULARES (iOS Safari & Android Chrome) ---
    let mobileAudioUnlocked = false;
    function unlockMobileAudio() {
        if (mobileAudioUnlocked) return;
        mobileAudioUnlocked = true;
        try {
            if (typeof audioCtx !== 'undefined' && audioCtx && audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const silent = new Audio("data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA");
            silent.play().then(() => { silent.pause(); }).catch(() => {});
        } catch (e) {}
    }
    ['touchstart', 'touchend', 'click'].forEach(evt => {
        document.addEventListener(evt, unlockMobileAudio, { once: true, passive: true });
    });
});