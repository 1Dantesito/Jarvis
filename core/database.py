import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

def _utcnow():
    return datetime.now(timezone.utc)

engine = create_engine(
    f"sqlite:///{settings.DB_PATH}",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), index=True, default="PERSONAL")
    category = Column(String(50), index=True, default="general")
    key = Column(String(100), index=True, nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=0.9)
    importance = Column(Float, default=0.5)
    source = Column(String(50), default="user_explicit")
    active = Column(Boolean, default=True)
    tags = Column(String(200), default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    last_used_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)

class ReminderModel(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_datetime_iso = Column(String(50), nullable=False)
    display_datetime = Column(String(100), nullable=True)
    timezone = Column(String(50), default="Local")
    priority = Column(String(20), default="NORMAL")
    status = Column(String(20), default="PENDING")
    stages_notified = Column(String(100), default="")
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project = Column(String(100), default="General")
    priority = Column(String(20), default="NORMAL")
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class UserProfileModel(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

# ==============================================================================
# Modelos Aditivos de Fase D (Cerebro Relacional y Memoria Semántica)
# ==============================================================================

class SemanticMemoryModel(Base):
    """
    Modelo estructurado para la memoria semántica profunda (Esquema D.2: semantic_memory_entry.json).
    Almacena embeddings locales normalizados (128 floats) y scoring multidimensional.
    """
    __tablename__ = "semantic_memories"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String(50), unique=True, index=True, nullable=False)
    key = Column(String(100), index=True, nullable=False)
    value = Column(Text, nullable=False)
    memory_type = Column(String(50), index=True, default="PERSONAL")
    category = Column(String(50), index=True, default="general")
    tags = Column(Text, default="[]")  # JSON list
    confidence = Column(Float, default=0.90)
    importance = Column(Float, default=0.50)
    emotional_valence = Column(Float, default=0.0)
    source = Column(String(50), default="user_explicit")
    
    # Metadatos temporales y ley de olvido
    access_count = Column(Integer, default=1)
    reinforcement_count = Column(Integer, default=0)
    half_life_days = Column(Float, default=30.0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    last_accessed_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Vector denso 128D (JSON list de 128 floats)
    embedding = Column(Text, default="[]")
    embedding_provider = Column(String(50), default="local_hybrid")
    embedding_hash = Column(String(64), nullable=True)
    active = Column(Boolean, default=True)

class RelationshipStateModel(Base):
    """
    Modelo de estado relacional continuo y memoria afectiva (Esquema D.2: relationship_state.json).
    """
    __tablename__ = "relationship_state"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, default="dante")
    affinity_score = Column(Float, default=50.0)
    intimacy_level = Column(String(30), default="COMPANION")
    total_interactions = Column(Integer, default=0)
    
    # Estado afectivo en tiempo real
    affective_valence = Column(Float, default=0.0)
    affective_arousal = Column(Float, default=0.3)
    dominant_emotion = Column(String(50), default="calm")
    affective_confidence = Column(Float, default=0.8)
    
    # Modo y límites éticos (JSON object)
    active_conversation_mode = Column(String(50), default="BALANCED_COMPANION")
    ethical_boundaries = Column(Text, default="{}")
    narrative_milestones = Column(Text, default="[]")
    
    first_interaction_at = Column(DateTime, default=_utcnow)
    last_interaction_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class PersonalityTraitsModel(Base):
    """
    Modelo de rasgos dinámicos de personalidad de JARVIS (Esquema D.2: personality_traits.json).
    """
    __tablename__ = "personality_traits"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String(50), unique=True, index=True, default="default")
    humor = Column(Float, default=1.0)
    verbosity = Column(Float, default=0.8)
    formality = Column(Float, default=0.5)
    empathy = Column(Float, default=1.0)
    active_style = Column(String(50), default="warm_companion")
    custom_rules = Column(Text, default="[]")  # JSON list
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            for col_def in [
                "ALTER TABLE memories ADD COLUMN type VARCHAR(50) DEFAULT 'PERSONAL'",
                "ALTER TABLE memories ADD COLUMN confidence FLOAT DEFAULT 0.9",
                "ALTER TABLE memories ADD COLUMN importance FLOAT DEFAULT 0.5",
                "ALTER TABLE memories ADD COLUMN source VARCHAR(50) DEFAULT 'user_explicit'",
                "ALTER TABLE memories ADD COLUMN active BOOLEAN DEFAULT 1",
                "ALTER TABLE memories ADD COLUMN tags VARCHAR(200) DEFAULT ''",
                "ALTER TABLE memories ADD COLUMN last_used_at DATETIME",
                "ALTER TABLE memories ADD COLUMN expires_at DATETIME",
                "ALTER TABLE tasks ADD COLUMN project VARCHAR(100) DEFAULT 'General'",
                "ALTER TABLE reminders ADD COLUMN is_recurring BOOLEAN DEFAULT 0",
                "ALTER TABLE reminders ADD COLUMN recurrence_rule VARCHAR(100)"
            ]:
                try:
                    conn.exec_driver_sql(col_def)
                except Exception:
                    pass
    except Exception:
        pass
