// =========================================================================
// JARVIS Assistant — Resilient WebSocket Client Module (v4.0 Mobile-Ready)
// =========================================================================

export class ResilientWebSocket {
    constructor(options = {}) {
        this.urlBuilder = options.urlBuilder || this.defaultUrlBuilder;
        this.onMessage = options.onMessage || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});
        
        this.ws = null;
        this.pingTimer = null;
        this.pongTimeoutTimer = null;
        this.reconnectTimer = null;
        
        // Estrategia de Backoff Exponencial para redes móviles inestables
        this.retryCount = 0;
        this.baseDelayMs = 1000;
        this.maxDelayMs = 30000;
        this.isClosedExplicitly = false;
        this.status = 'DISCONNECTED'; // DISCONNECTED | CONNECTING | CONNECTED | RECONNECTING
    }

    defaultUrlBuilder() {
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const deviceId = window.ApiClient ? window.ApiClient.getDeviceId() : 'default_device';
        const sessionId = window.ApiClient ? window.ApiClient.getSessionId() : 'default_session';
        return `${proto}//${host}/ws/v1/chat?session_id=${encodeURIComponent(sessionId)}&device_id=${encodeURIComponent(deviceId)}`;
    }

    connect() {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        this.isClosedExplicitly = false;
        this._updateStatus(this.retryCount === 0 ? 'CONNECTING' : 'RECONNECTING');

        const wsUrl = this.urlBuilder();
        console.log(`[Jarvis WS] Conectando a WebSocket (${this.status}, intento #${this.retryCount + 1})...`);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('[Jarvis WS] Conexión establecida con éxito.');
                this.retryCount = 0;
                this._updateStatus('CONNECTED');
                this._startHeartbeat();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'pong') {
                        this._handlePong();
                        return;
                    }
                    if (data.type === 'sync_state' && data.session_id) {
                        if (window.ApiClient) {
                            window.ApiClient.setSessionId(data.session_id);
                        }
                    }
                    this.onMessage(data);
                } catch (e) {
                    console.warn('[Jarvis WS] Error procesando mensaje entrante:', e);
                }
            };

            this.ws.onerror = (err) => {
                console.warn('[Jarvis WS] Error en socket:', err);
            };

            this.ws.onclose = (event) => {
                console.log(`[Jarvis WS] Conexión cerrada (code: ${event.code}, clean: ${event.wasClean}).`);
                this._stopHeartbeat();
                this._updateStatus('DISCONNECTED');

                if (!this.isClosedExplicitly) {
                    this._scheduleReconnect();
                }
            };

        } catch (error) {
            console.error('[Jarvis WS] Error al instanciar WebSocket:', error);
            this._scheduleReconnect();
        }
    }

    send(messageObj) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(messageObj));
            return true;
        }
        console.warn('[Jarvis WS] Intento de envío en socket desconectado:', messageObj.type);
        return false;
    }

    close() {
        this.isClosedExplicitly = true;
        this._stopHeartbeat();
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this._updateStatus('DISCONNECTED');
    }

    _updateStatus(newStatus) {
        if (this.status !== newStatus) {
            this.status = newStatus;
            this.onStatusChange(newStatus);
        }
    }

    _scheduleReconnect() {
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

        // Backoff exponencial: delay = min(maxDelay, baseDelay * 2^retryCount) + jitter
        const exponentialFactor = Math.pow(2, Math.min(this.retryCount, 6));
        const calculatedDelay = Math.min(this.baseDelayMs * exponentialFactor, this.maxDelayMs);
        const jitter = Math.floor(Math.random() * 400); // 0 a 400ms de variación para evitar tormentas
        const delay = calculatedDelay + jitter;

        this.retryCount++;
        this._updateStatus('RECONNECTING');
        console.log(`[Jarvis WS] Reconexión programada en ${delay}ms (reintento #${this.retryCount})...`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }

    _startHeartbeat() {
        this._stopHeartbeat();
        // Ping cada 15 segundos para mantener activo el túnel y detectar redes caídas
        this.pingTimer = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
                // Si no hay pong dentro de 5 segundos, la conexión está muerta
                this.pongTimeoutTimer = setTimeout(() => {
                    console.warn('[Jarvis WS] Heartbeat timeout: Pong no recibido en 5s. Forzando reconexión...');
                    if (this.ws) {
                        this.ws.close();
                    }
                }, 5000);
            }
        }, 15000);
    }

    _handlePong() {
        if (this.pongTimeoutTimer) {
            clearTimeout(this.pongTimeoutTimer);
            this.pongTimeoutTimer = null;
        }
    }

    _stopHeartbeat() {
        if (this.pingTimer) clearInterval(this.pingTimer);
        if (this.pongTimeoutTimer) clearTimeout(this.pongTimeoutTimer);
        this.pingTimer = null;
        this.pongTimeoutTimer = null;
    }
}

if (typeof window !== 'undefined') {
    window.ResilientWebSocket = ResilientWebSocket;
}
