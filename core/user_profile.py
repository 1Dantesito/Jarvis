from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PersonalityProfile:
    """
    Configuración adaptativa de personalidad, estilo y calidez de JARVIS.
    """
    verbosity: int = 1         # 1 = Ultra conciso (1 frase para voz), 5 = Detallado
    humor: int = 3             # 1 = Serio/Sin bromas, 5 = Muy ocurrente
    formality: int = 2         # 1 = Muy informal/amigable, 5 = Muy protocolario
    technicality: int = 3      # 1 = Cotidiano, 5 = Altamente técnico
    warmth: int = 4            # 1 = Frío/Distante, 5 = Muy cálido y cercano
    playfulness: int = 3       # 1 = Sobrio, 5 = Juguetón
    tone: str = "amigable_inteligente"

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
        humor_desc = "Cero bromas, tono sobrio y profesional." if self.humor <= 1 else ("Moderado y natural, sin exagerar." if self.humor <= 3 else "Ocurrente y espontáneo.")
        concision_desc = "Ultra breve (1 frase directa para acciones)." if self.verbosity <= 2 else "Moderada y explicativa."
        return (
            f"Personalidad: Compañero digital inteligente, cercano y cálido (Nivel de calidez: {self.warmth}/5). "
            f"Concisión: {concision_desc} Humor: {humor_desc} "
            f"Estilo: Natural, dinámico, evitando muletillas robóticas como 'A su disposición' o 'Como IA'. "
            f"Honestidad y Pensamiento Crítico: Sé sincero, objetivo y directo. No des la razón por complacer ni adules. Si una premisa, idea o plan del usuario tiene fallos, riesgos o inconsistencias, señálalo constructivamente con argumentos sólidos."
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
