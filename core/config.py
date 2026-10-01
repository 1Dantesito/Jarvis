import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env desde la raíz del proyecto
load_dotenv(BASE_DIR / ".env")

def mask_key(key: str) -> str:
    """Enmascara una API key para logging seguro sin exponer secretos."""
    if not key or len(key) < 8:
        return "[NOT_SET]"
    if key.startswith("sk-or-"):
        return f"{key[:9]}...{key[-4:]}"
    elif key.startswith("AIza"):
        return f"{key[:6]}...{key[-4:]}"
    return f"{key[:4]}...{key[-4:]}"

class Settings:
    PROJECT_NAME: str = "JARVIS Assistant"
    VERSION: str = "3.0.0"
    
    # Rutas
    BASE_DIR: Path = BASE_DIR
    DB_PATH: Path = BASE_DIR / "jarvis.db"
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    AUDIO_DIR: Path = STATIC_DIR / "audio"
    
    # Servidor y Entorno
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5001"))
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() in ["true", "1", "yes"]
    ENV: str = os.getenv("ENV", "desktop").strip().lower()
    API_BASE_URL: str = os.getenv("API_BASE_URL", f"http://localhost:{os.getenv('PORT', '5001')}").strip()
    ALLOWED_ORIGINS: List[str] = [
        orig.strip() for orig in os.getenv("ALLOWED_ORIGINS", "*").split(",") if orig.strip()
    ]
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "").strip()
    
    # Contexto Temporal y Ubicación
    TIMEZONE_OVERRIDE: Optional[str] = os.getenv("TIMEZONE_OVERRIDE", "").strip() or None
    ENABLE_LOCATION: bool = os.getenv("ENABLE_LOCATION", "true").lower() in ["true", "1", "yes"]
    ALLOW_EXACT_COORDINATES: bool = os.getenv("ALLOW_EXACT_COORDINATES", "false").lower() in ["true", "1", "yes"]

    # Modelos de IA
    DEFAULT_GEMINI_MODEL: str = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-3.5-flash-lite")
    GEMINI_MODEL_CANDIDATES: List[str] = [
        m.strip() for m in os.getenv(
            "GEMINI_MODEL_CANDIDATES", 
            "gemini-3.5-flash-lite,gemini-3.6-flash"
        ).split(",") if m.strip()
    ]
    
    DEFAULT_OPENROUTER_MODEL: str = os.getenv("DEFAULT_OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_MODEL_CANDIDATES: List[str] = [
        m.strip() for m in os.getenv(
            "OPENROUTER_MODEL_CANDIDATES", 
            "openai/gpt-4o-mini,meta-llama/llama-3.1-8b-instruct,deepseek/deepseek-chat,openrouter/free"
        ).split(",") if m.strip()
    ]

    DEFAULT_CLAUDE_MODEL: str = os.getenv("DEFAULT_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Seguridad y Protocolo de Crisis (Cerebro Relacional D.2/D.3)
    CRISIS_GUARD_TIMEOUT_SECONDS: float = float(os.getenv("CRISIS_GUARD_TIMEOUT_SECONDS", "2.0"))
    CRISIS_GUARD_FAST_MODEL: str = os.getenv("CRISIS_GUARD_FAST_MODEL", "gemini-2.0-flash-lite")
    
    # Escucha Continua y Manos Libres
    WAKE_WORD: str = os.getenv("WAKE_WORD", "jarvis").lower()
    CONVERSATION_WINDOW_SECONDS: int = int(os.getenv("CONVERSATION_WINDOW_SECONDS", "12"))
    END_OF_TURN_SILENCE_MS: int = int(os.getenv("END_OF_TURN_SILENCE_MS", "700"))
    ENABLE_HANDS_FREE: bool = os.getenv("ENABLE_HANDS_FREE", "true").lower() in ["true", "1", "yes"]
    
    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and not self.GEMINI_API_KEY.startswith("your_"))

    @property
    def has_openrouter_key(self) -> bool:
        return bool(self.OPENROUTER_API_KEY and not self.OPENROUTER_API_KEY.startswith("your_"))

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY and not self.ANTHROPIC_API_KEY.startswith("your_"))

    @property
    def default_provider_name(self) -> str:
        if self.has_openrouter_key:
            return "openrouter"
        elif self.has_gemini_key:
            return "gemini"
        elif self.has_anthropic_key:
            return "anthropic"
        return "mock"

settings = Settings()
