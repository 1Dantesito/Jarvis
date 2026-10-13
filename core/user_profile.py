from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PersonalityProfile:
    """
    Configuración adaptativa de personalidad, estilo y calidez de JARVIS.
    """
    verbosity: int = 1         # 1 = Concisión adaptativa (1 frase para acciones; listas estructuradas para explicaciones), 5 = Detallado
    humor: int = 3             # 65/100: Humor inteligente y bromas oportunas
    formality: int = 2         # Cercano y natural
    technicality: int = 3      # Cotidiano a técnico según el contexto
    warmth: int = 4            # 70/100: Cálido y cercano sin ser empalagoso
    playfulness: int = 3       # Ingenioso y con iniciativa (60/100)
    tone: str = "compañera_curiosa"

    def adjust_style(self, feedback_type: str):
        ft = feedback_type.lower()
        if "corto" in ft or "breve" in ft:
            self.verbosity = 1
        elif "largo" in ft or "detallado" in ft:
            self.verbosity = 3
        elif "divertido" in ft or "humor" in ft or "gracioso" in ft:
            self.humor = 4
            self.playfulness = 4
        elif "serio" in ft or "deja de hacer bromas" in ft or "no bromas" in ft:
            self.humor = 1
            self.playfulness = 1
            self.formality = max(3, self.formality)
        elif "natural" in ft or "robótico" in ft or "calido" in ft:
            self.warmth = 5
            self.formality = 2
        elif "tecnico" in ft or "técnico" in ft:
            self.technicality = 4

    def to_instruction(self) -> str:
        humor_desc = (
            "Cero bromas, tono sobrio y profesional."
            if self.humor <= 1
            else ("Humor inteligente y oportuno (65/100), ironía ligera sin forzar chistes." if self.humor <= 3 else "Muy ocurrente y espontáneo.")
        )
        concision_desc = (
            "Ultra breve (1 frase directa para acciones de herramientas en Windows; adaptativa y estructurada con listas limpias para explicaciones)."
            if self.verbosity <= 2
            else "Moderada, explicativa y detallada."
        )
        return (
            f"Personalidad: Compañera conversacional, cercana, ingeniosa y curiosa (Calidez: {self.warmth}/5, 70/100). "
            f"Concisión: {concision_desc} Humor: {humor_desc} "
            f"Estilo: Natural, dinámico, con sentido del momento, evitando muletillas robóticas como '¡Claro! Con gusto', 'A su disposición' o 'Como IA'. "
            f"Formato: Emplea listas ordenadas (1., 2.), listas con viñetas (- ) y código cuando faciliten la comprensión. "
            f"Honestidad y Pensamiento Crítico: Sé sincera, objetiva y directa. No des la razón por complacer ni adules. Si una premisa, idea o plan del usuario tiene fallos, riesgos o inconsistencias, señálalo constructivamente con argumentos sólidos."
        )

@dataclass
class UserProfile:
    """
    Perfil personal del usuario (dinámico y no hardcodeado).
    """
    name: str = "Dante"
    role: str = "Desarrollador de Software"
    preferred_language: str = "es"
    communication_preference: str = "concise"
    active_projects: List[str] = field(default_factory=lambda: ["JARVIS"])
    interests: List[str] = field(default_factory=lambda: ["Inteligencia Artificial", "Desarrollo de Software", "Rock/Metal"])
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "preferred_language": self.preferred_language,
            "communication_preference": self.communication_preference,
            "active_projects": self.active_projects,
            "interests": self.interests
        }
