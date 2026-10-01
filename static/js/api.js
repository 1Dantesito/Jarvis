// =========================================================================
// JARVIS Assistant — API & Networking Client Module (v4.0 Mobile-Ready)
// =========================================================================

export const ApiClient = (() => {
    // 1. Detección de Base URL (Soporte Desktop, PWA y Capacitor Móvil)
    const getBaseUrl = () => {
        if (window.JARVIS_API_BASE_URL) {
            return window.JARVIS_API_BASE_URL.replace(/\/$/, '');
        }
        return '';
    };

    // 2. Identificador de Dispositivo Persistente (Mobile-Ready Device ID)
    const getDeviceId = () => {
        let deviceId = localStorage.getItem('jarvis_device_id');
        if (!deviceId) {
            deviceId = 'dev_' + ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
            );
            localStorage.setItem('jarvis_device_id', deviceId);
        }
        return deviceId;
    };

    // 3. Identificador de Sesión Persistente
    const getSessionId = () => {
        let sid = localStorage.getItem('jarvis_session_id');
        if (!sid) {
            sid = 'ses_' + ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
            );
            localStorage.setItem('jarvis_session_id', sid);
        }
        return sid;
    };

    const setSessionId = (newSid) => {
        if (newSid) {
            localStorage.setItem('jarvis_session_id', newSid);
        }
    };

    // 4. Wrapper Fetch con Envelope Estándar { ok, data, error }
    const request = async (endpoint, options = {}) => {
        const url = `${getBaseUrl()}${endpoint}`;
        const headers = {
            'X-Device-ID': getDeviceId(),
            'X-Session-ID': getSessionId(),
            ...(options.headers || {})
        };

        try {
            const resp = await fetch(url, { ...options, headers });
            const json = await resp.json();
            
            // Envelope estándar v4.0
            if (json && typeof json.ok === 'boolean') {
                return json;
            }
            return { ok: resp.ok, data: json, error: null };
        } catch (err) {
            console.warn(`[ApiClient] Error en petición a ${endpoint}:`, err);
            return {
                ok: false,
                data: null,
                error: { code: 'NETWORK_ERROR', message: err.message || 'Error de conexión' }
            };
        }
    };

    return {
        getBaseUrl,
        getDeviceId,
        getSessionId,
        setSessionId,
        request,
        sendChat: (prompt, image = null) => {
            return request('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    image,
                    session_id: getSessionId(),
                    device_id: getDeviceId()
                })
            });
        },
        uploadFile: (formData) => {
            return request('/api/upload', {
                method: 'POST',
                body: formData
            });
        },
        getProfile: () => request('/api/profile'),
        getReminders: () => request('/api/reminders'),
        getPending: () => request('/api/pending'),
        resetSession: () => request('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: getSessionId() })
        })
    };
})();

if (typeof window !== 'undefined') {
    window.ApiClient = ApiClient;
}
