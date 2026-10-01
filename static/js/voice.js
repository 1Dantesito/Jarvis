// =========================================================================
// JARVIS Assistant — Voice, Audio & Speech Module (v4.0 Mobile-Ready)
// =========================================================================

export class VoiceEngine {
    constructor(options = {}) {
        this.onTranscript = options.onTranscript || (() => {});
        this.onInterruption = options.onInterruption || (() => {});
        this.onStateChange = options.onStateChange || (() => {});
        this.onError = options.onError || (() => {});

        this.recognition = null;
        this.isListening = false;
        this.handsFreeEnabled = true;
        this.audioCtx = null;
        this.activeAudio = null;
        this.ttsQueue = [];
        this.isPlayingTTS = false;

        this._initSpeechRecognition();
    }

    _initSpeechRecognition() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            console.warn('[VoiceEngine] Web Speech API no soportada en este entorno. Degradando a modo texto (ISS-02).');
            this.onError({ code: 'SPEECH_UNSUPPORTED', message: 'Reconocimiento de voz no soportado. Usa el teclado.' });
            return;
        }

        try {
            this.recognition = new SpeechRec();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'es-ES';

            this.recognition.onstart = () => {
                this.isListening = true;
                this.onStateChange('LISTENING');
            };

            this.recognition.onresult = (event) => {
                let interim = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    const item = event.results[i];
                    if (item.isFinal) {
                        finalTranscript += item[0].transcript;
                    } else {
                        interim += item[0].transcript;
                    }
                }

                if (interim && this.isPlayingTTS) {
                    // Barge-in: el usuario comenzó a hablar mientras JARVIS habla
                    this.stopPlayback();
                    this.onInterruption();
                }

                if (finalTranscript.trim()) {
                    this.onTranscript(finalTranscript.trim());
                }
            };

            this.recognition.onerror = (err) => {
                // Degradación segura sin interrumpir la app
                if (err.error === 'not-allowed' || err.error === 'service-not-allowed') {
                    console.warn('[VoiceEngine] Permiso de micrófono denegado. Modo texto activado (ISS-02).');
                    this.onError({ code: 'MIC_DENIED', message: 'Permiso de micrófono denegado.' });
                } else if (err.error !== 'no-speech') {
                    console.debug('[VoiceEngine] Evento recognition error:', err.error);
                }
            };

            this.recognition.onend = () => {
                this.isListening = false;
                // Si manos libres está activo, reconectar escucha si no estamos procesando
                if (this.handsFreeEnabled) {
                    setTimeout(() => {
                        if (this.handsFreeEnabled && !this.isListening) {
                            try { this.recognition.start(); } catch (e) {}
                        }
                    }, 500);
                } else {
                    this.onStateChange('IDLE');
                }
            };
        } catch (e) {
            console.warn('[VoiceEngine] Error inicializando SpeechRecognition:', e);
        }
    }

    startListening() {
        if (!this.recognition) return false;
        try {
            this.recognition.start();
            return true;
        } catch (e) {
            return false;
        }
    }

    stopListening() {
        if (!this.recognition) return;
        try {
            this.recognition.stop();
            this.isListening = false;
        } catch (e) {}
    }

    playChime() {
        try {
            if (!this.audioCtx) {
                this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (this.audioCtx.state === 'suspended') {
                this.audioCtx.resume();
            }
            const now = this.audioCtx.currentTime;
            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.exponentialRampToValueAtTime(880.00, now + 0.10); // A5
            gain.gain.setValueAtTime(0.09, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
            osc.connect(gain);
            gain.connect(this.audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.22);
        } catch (e) {
            console.debug('[VoiceEngine] Error reproduciendo chime:', e);
        }
    }

    enqueueTTS(audioUrl) {
        if (!audioUrl) return;
        this.ttsQueue.push(audioUrl);
        if (!this.isPlayingTTS) {
            this._processTTSQueue();
        }
    }

    _processTTSQueue() {
        if (this.ttsQueue.length === 0) {
            this.isPlayingTTS = false;
            this.onStateChange('IDLE');
            return;
        }

        this.isPlayingTTS = true;
        this.onStateChange('SPEAKING');
        const nextUrl = this.ttsQueue.shift();

        this.activeAudio = new Audio(nextUrl);
        this.activeAudio.onended = () => {
            this._processTTSQueue();
        };
        this.activeAudio.onerror = (e) => {
            console.warn('[VoiceEngine] Error reproduciendo segmento TTS:', e);
            this._processTTSQueue();
        };

        this.activeAudio.play().catch((err) => {
            console.debug('[VoiceEngine] Reproducción de audio rechazada por navegador:', err);
            this._processTTSQueue();
        });
    }

    stopPlayback() {
        this.ttsQueue = [];
        if (this.activeAudio) {
            this.activeAudio.pause();
            this.activeAudio.currentTime = 0;
            this.activeAudio = null;
        }
        this.isPlayingTTS = false;
        this.onStateChange('IDLE');
    }
}

if (typeof window !== 'undefined') {
    window.VoiceEngine = VoiceEngine;
}
