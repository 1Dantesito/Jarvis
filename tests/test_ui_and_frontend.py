import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

def test_index_html_renders_boba_and_orb():
    res = client.get("/")
    assert res.status_code == 200
    assert "boba-canvas" in res.text
    assert "jarvis-orb" in res.text
    assert "context-drawer" in res.text


def test_organic_reactive_orb_structure():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert "family=Space+Mono" not in html
    assert "family=Outfit" in html
    assert "family=Plus+Jakarta+Sans" in html
    assert 'id="jarvis-orb"' in html
    assert 'class="orb-halo"' in html
    assert 'class="orb-core"' in html
    assert 'class="orb-inner-center"' in html
    assert 'class="orb-ring ring-1"' in html
    assert 'class="orb-ring ring-2"' in html
    assert 'id="orb-equalizer"' in html


def test_orb_state_idle():
    res_css = client.get("/static/style.css")
    res_js = client.get("/static/script.js")
    assert "--orb-idle-primary:     #9C9289" in res_css.text
    assert ".aura-orb.idle" in res_css.text
    assert "@keyframes orbBreathe" in res_css.text
    assert "jarvisOrb.classList.add('idle')" in res_js.text
    assert "jarvisOrb.setAttribute('aria-label', 'JARVIS en reposo. Haz clic o di Jarvis para interactuar.')" in res_js.text


def test_orb_state_listening():
    res_css = client.get("/static/style.css")
    res_js = client.get("/static/script.js")
    assert "--orb-listening-primary:#48A97A" in res_css.text
    assert ".aura-orb.listening" in res_css.text
    assert "@keyframes orbListenPulse" in res_css.text
    assert "@keyframes orbEqBounce" in res_css.text
    assert "jarvisOrb.classList.add('listening')" in res_js.text
    assert "jarvisOrb.setAttribute('aria-label', 'JARVIS escuchando tu voz...')" in res_js.text


def test_orb_state_processing_thinking():
    res_css = client.get("/static/style.css")
    res_js = client.get("/static/script.js")
    assert "--orb-processing-primary:#7C6DB8" in res_css.text
    assert ".aura-orb.thinking" in res_css.text
    assert ".aura-orb.processing" in res_css.text
    assert "@keyframes orbThinkingPulse" in res_css.text
    assert "jarvisOrb.classList.add('thinking')" in res_js.text
    assert "jarvisOrb.setAttribute('aria-label', 'JARVIS procesando respuesta...')" in res_js.text


def test_orb_state_speaking():
    res_css = client.get("/static/style.css")
    res_js = client.get("/static/script.js")
    assert "--orb-speaking-primary: #E5A83B" in res_css.text
    assert ".aura-orb.speaking" in res_css.text
    assert "@keyframes orbSpeakWave" in res_css.text
    assert "jarvisOrb.classList.add('speaking')" in res_js.text
    assert "jarvisOrb.setAttribute('aria-label', 'JARVIS respondiendo con voz...')" in res_js.text


def test_orb_state_error():
    res_css = client.get("/static/style.css")
    res_js = client.get("/static/script.js")
    assert "--orb-error-primary:    #D34537" in res_css.text
    assert ".aura-orb.error" in res_css.text
    assert "@keyframes orbErrorPulse" in res_css.text
    assert "jarvisOrb.classList.add('error')" in res_js.text
    assert "jarvisOrb.setAttribute('aria-label', 'JARVIS ha encontrado un error. Haz clic para reintentar.')" in res_js.text


def test_orb_gpu_compositing_and_motion_accessibility():
    res_css = client.get("/static/style.css")
    css = res_css.text
    assert "will-change: transform" in css
    assert "prefers-reduced-motion" in css
    # Asegura que las animaciones clave no animen box-shadow o filter en keyframes
    assert "box-shadow:" not in css[css.find("@keyframes orbBreathe"):css.find("/* Texto de Estado")]
    assert "filter:" not in css[css.find("@keyframes orbBreathe"):css.find("/* Texto de Estado")]


def test_orb_keyboard_and_touch_accessibility():
    res_html = client.get("/")
    res_js = client.get("/static/script.js")
    assert 'role="button"' in res_html.text
    assert 'tabindex="0"' in res_html.text
    assert "jarvisOrb.addEventListener('keydown'" in res_js.text
    assert "jarvisOrb.classList.remove('idle', 'listening', 'thinking', 'processing', 'speaking', 'error')" in res_js.text


def test_theme_wcag_contrast_ratios_mathematical():
    def lum(r, g, b):
        def ch(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def contrast(c1, c2):
        l1, l2 = lum(*hex_to_rgb(c1)), lum(*hex_to_rgb(c2))
        return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

    themes = [
        ("Carbón Cálido", "#1E1C1A", "#F5F2EB", "#A8A196"),
        ("Lino Crema", "#FAF7F2", "#262320", "#686058"),
        ("Ámbar Dorado", "#FDF8F0", "#2A1F17", "#665446"),
        ("Espresso Moka", "#201A18", "#F5ECE7", "#B09E96")
    ]

    for name, bg, pri, sec in themes:
        c_pri = contrast(pri, bg)
        c_sec = contrast(sec, bg)
        assert c_pri >= 4.5, f"Texto primario en {name} ({pri} sobre {bg}) no cumple WCAG AA: {c_pri:.2f}:1"
        assert c_sec >= 4.5, f"Texto secundario en {name} ({sec} sobre {bg}) no cumple WCAG AA: {c_sec:.2f}:1"

    # Verificación matemática del botón crítico de confirmación destructiva (.chat-confirm-btn)
    c_btn = contrast("#FFFFFF", "#B83A2E")
    assert c_btn >= 4.5, f"Texto blanco sobre #B83A2E de confirmación no cumple WCAG AA: {c_btn:.2f}:1"
    assert c_btn >= 5.5, f"El contraste de confirmación debería superar 5.5:1, dio {c_btn:.2f}:1"


def test_chat_bubbles_and_input_bar_styling():
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    css = res_css.text

    # Separación visual entre CTA (#D97736) y Acción Destructiva (#B83A2E)
    assert "--accent-primary:       #D97736" in css
    assert "--action-destructive:   #B83A2E" in css
    assert "rgba(184, 58, 46, 0.08)" in css

    # Burbujas de usuario y Jarvis con radios orgánicos asimétricos
    assert ".message-item.user .bubble" in css
    assert "border-radius: 20px 20px 4px 20px" in css
    assert ".message-item.jarvis .bubble" in css
    assert "border-radius: 20px 20px 20px 4px" in css

    # Input bar con font-size 16px (evita auto-zoom en Safari iOS)
    assert "font-size: 16px; /* Evita auto-zoom en iOS Safari */" in css
    assert ".input-wrapper:focus-within" in css

    # Touch targets >= 44px
    assert "min-height: 44px" in css
    assert "min-width: 44px" in css

    # Cards de confirmación de seguridad con fondo y botón destructivo rojo óxido
    assert ".chat-action-card.confirmation" in css
    assert ".chat-confirm-btn" in css
    assert "var(--action-destructive, #B83A2E)" in css
    assert ".chat-cancel-btn" in css

    # Animaciones GPU-only
    assert "@keyframes msgIn" in css
    assert "@keyframes micListenPulse" in css


def test_script_chat_message_rendering_and_confirmation_cards():
    res_js = client.get("/static/script.js")
    assert res_js.status_code == 200
    js = res_js.text

    # Manejo de sender jarvis y user en appendMessage
    assert "if (sender === 'jarvis')" in js
    assert "msg-time-user" in js

    # Soporte interactivo de tarjetas de confirmación en appendActionBadge
    assert 'actionType === "security_confirmation"' in js
    assert "chat-confirm-btn" in js
    assert "chat-cancel-btn" in js
    assert 'handleSendMessage("Sí, confirmo la acción")' in js


def test_header_brand_status_and_quick_pills():
    res_html = client.get("/")
    res_css = client.get("/static/style.css")
    assert res_html.status_code == 200
    assert res_css.status_code == 200
    html = res_html.text
    css = res_css.text

    # Presencia en el DOM
    assert 'class="app-header"' in html
    assert 'class="status-dot online"' in html
    assert 'class="brand-title">JARVIS</h1>' in html
    assert 'id="version-tag">v4.0<' in html
    assert 'id="live-provider-badge"' in html
    assert 'id="btn-open-memory"' in html
    assert 'id="btn-open-ambient"' in html
    assert 'id="btn-open-themes"' in html
    assert 'id="btn-toggle-drawer"' in html

    # Status dot con verde esmeralda cálido / jade (#48A97A)
    assert "--state-success, #48A97A" in css

    # Touch targets >= 44px para píldoras e iconos de navegación superior
    assert ".live-provider-badge {" in css
    assert ".quick-nav-pill {" in css
    assert ".icon-btn-pill {" in css
    assert "min-height: 44px" in css[css.find(".quick-nav-pill {"):css.find(".pill-count {")]
    start_icon = css.find(".icon-btn-pill {")
    end_icon = css.find(".mini-player {", start_icon)
    assert "min-width: 44px" in css[start_icon:end_icon]
    assert "min-height: 44px" in css[start_icon:end_icon]


def test_mini_player_vinyl_rotation_gpu_composited_and_reduced_motion():
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    css = res_css.text

    # Vinilo con GPU compositing
    assert ".vinyl-disc {" in css
    assert "will-change: transform" in css[css.find(".vinyl-disc {"):css.find(".mini-player.playing .vinyl-disc")]
    assert "transform: translateZ(0)" in css[css.find(".vinyl-disc {"):css.find(".mini-player.playing .vinyl-disc")]

    # Animación de rotación en bucle con transform puro
    assert "animation: spinVinyl 4s linear infinite" in css
    spin_block = css[css.find("@keyframes spinVinyl"):css.find(".track-meta")]
    assert "transform: rotate(0deg)" in spin_block
    assert "transform: rotate(360deg)" in spin_block
    # Prohibido animar propiedades de layout en keyframes continuos
    for prop in ["margin", "padding", "width", "height", "top", "left", "box-shadow", "filter"]:
        assert f"{prop}:" not in spin_block, f"Propiedad {prop} no permitida en keyframe de vinilo"

    # Ecualizador musical con GPU transform: scaleY (no layout height)
    assert "@keyframes musicWaveGPU" in css
    wave_block = css[css.find("@keyframes musicWaveGPU"):css.find(".player-actions")]
    assert "transform: scaleY" in wave_block
    assert "height:" not in wave_block

    # Respeto estricto a prefers-reduced-motion (desactiva rotación y ecualizador)
    assert "prefers-reduced-motion" in css
    start_reduced = css.find("@media (prefers-reduced-motion: reduce)")
    end_reduced = css.find(".music-studio-modal {", start_reduced)
    reduced_block = css[start_reduced:end_reduced]
    assert ".mini-player.playing .vinyl-disc" in reduced_block
    assert ".music-studio-modal.playing .studio-vinyl-disc" in reduced_block
    assert ".mini-player.playing .music-wave span" in reduced_block
    assert "animation: none !important" in reduced_block

    # Controles del reproductor con touch targets >= 44px
    ctrl_block = css[css.find(".player-ctrl-btn {"):css.find(".player-ctrl-btn:hover")]
    assert "min-width: 44px" in ctrl_block
    assert "min-height: 44px" in ctrl_block


def test_music_studio_modal_and_drawers_styling_and_touch_targets():
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    css = res_css.text

    # Paleta Warm Companion en estudio musical (cero residuo neon red #FF1E42)
    assert ".music-studio-card {" in css
    studio_block = css[css.find(".music-studio-card {"):css.find(".close-modal-btn {")]
    assert "#FF1E42" not in studio_block
    assert "var(--bg-surface)" in studio_block

    # Touch targets >= 44px en controles de estudio musical y drawers
    close_btn_block = css[css.find(".close-modal-btn {"):css.find(".close-modal-btn:hover")]
    assert "min-width: 44px" in close_btn_block
    assert "min-height: 44px" in close_btn_block

    play_circle_block = css[css.find(".studio-play-circle-btn {"):css.find(".studio-play-circle-btn:hover")]
    assert "min-width: 48px" in play_circle_block
    assert "min-height: 48px" in play_circle_block

    mem_cat_block = css[css.find(".mem-cat-btn {"):css.find(".mem-cat-btn:hover")]
    assert "min-height: 44px" in mem_cat_block

    style_btn_block = css[css.find(".style-btn {"):css.find(".style-btn:hover")]
    assert "min-height: 44px" in style_btn_block

    # Drawers con transformación acelerada por GPU translate3d
    drawer_block = css[css.find(".memory-drawer, .context-drawer {"):css.find(".memory-drawer.open")]
    assert "transform: translate3d(120%, 0, 0)" in drawer_block
    assert "will-change: transform, opacity" in drawer_block


def test_mobile_first_responsive_breakpoints():
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    css = res_css.text

    # Breakpoint para móviles compactos (<480px)
    assert "@media (max-width: 480px)" in css
    mobile_block = css[css.find("@media (max-width: 480px)"):css.find("@media (min-width: 481px)")]

    # Los header pills NO se ocultan en móvil: se adaptan fluidamente
    assert "display: flex" in mobile_block
    assert "overflow-x: auto" in mobile_block
    # Drawers aprovechan el ancho de pantalla móvil
    assert "calc(100vw - 24px)" in mobile_block


def test_pwa_manifest_and_lighthouse_installability():
    # 1. Manifest válido y criterios Lighthouse
    res_manifest = client.get("/static/manifest.json")
    assert res_manifest.status_code == 200
    manifest = res_manifest.json()

    assert manifest.get("name") == "JARVIS Assistant"
    assert manifest.get("short_name") == "JARVIS"
    assert manifest.get("start_url") == "/"
    assert manifest.get("display") == "standalone"
    assert manifest.get("theme_color") == "#141312"
    assert manifest.get("background_color") == "#141312"

    icons = manifest.get("icons", [])
    assert len(icons) >= 2
    sizes = [icon.get("sizes") for icon in icons]
    assert "192x192" in sizes
    assert "512x512" in sizes
    assert any("maskable" in icon.get("purpose", "") for icon in icons)

    # 2. Enlaces en index.html
    res_html = client.get("/")
    assert res_html.status_code == 200
    html = res_html.text
    assert '<link rel="manifest" href="/static/manifest.json">' in html
    assert '<meta name="theme-color" content="#141312">' in html
    assert 'viewport-fit=cover' in html
    assert 'apple-touch-icon' in html


def test_pwa_service_worker_exclusions_and_offline_shell():
    # 1. Service Worker servido correctamente
    res_sw = client.get("/static/sw.js")
    assert res_sw.status_code == 200
    sw_code = res_sw.text

    # 2. Exclusiones críticas de streaming y audio
    assert "url.pathname.startsWith('/api/tts/stream')" in sw_code
    assert "url.pathname.includes('/stream')" in sw_code
    assert "url.pathname.startsWith('/static/audio/')" in sw_code
    assert "text/event-stream" in sw_code

    # 3. Pre-cache del shell estático
    assert "'/static/style.css'" in sw_code
    assert "'/static/script.js'" in sw_code
    assert "'/static/manifest.json'" in sw_code

    # 4. Registro en index.html
    res_html = client.get("/")
    assert "serviceWorker.register('/static/sw.js')" in res_html.text




