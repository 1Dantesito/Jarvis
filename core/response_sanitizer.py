import re
from typing import Optional

class ResponseSanitizer:
    """
    Sanitizador central de respuestas para JARVIS.
    Garantiza que ningún placeholder técnico, sintaxis interna, markdown roto
    o repetición artificial de nombres llegue al usuario o al motor TTS.
    """

    PLACEHOLDERS_PATTERN = re.compile(
        r'(\{(?:usuario|nombre|user|username|user_name|usuario_nombre)\}|<(?:usuario|nombre|user|username)>|\[(?:usuario|nombre|user|username)\])',
        re.IGNORECASE
    )

    TECHNICAL_TOKENS_PATTERN = re.compile(
        r'\b(None|null|undefined|NaN|call_[a-zA-Z0-9_]+|function_call)\b',
        re.IGNORECASE
    )

    MARKDOWN_CLEAN_PATTERN = re.compile(r'[*#_~`>]')
    URL_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\([^\)]+\)')

    THINK_TAG_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL | re.IGNORECASE)

    # Filtra el chain-of-thought / razonamiento interno explícito que algunos LLMs filtran al output
    # Solo filtra meta-razonamiento real de la IA sobre sus instrucciones o llamadas a herramientas
    CHAIN_OF_THOUGHT_PATTERN = re.compile(
        r'^(?:\[thinking\]|\*thinking\*|thought:|thinking process:|\*reasoning\*|'
        r'[\-•]\s*(?:I need to determine|The user is asking me to|I will call the tool|I should call the function|Let me check my instructions)).*$',
        re.MULTILINE | re.IGNORECASE
    )

    @classmethod
    def sanitize(cls, text: str, user_name: Optional[str] = None) -> str:
        """
        Limpia y valida un texto para presentación en pantalla y pronunciación TTS.
        """
        if not text:
            return ""

        s = text.strip()

        # 1. Eliminar bloques de JSON o llamadas de funciones filtradas accidentalmente
        if s.startswith("{") and s.endswith("}") and ("tool" in s or "name" in s or "arguments" in s):
            return "Listo."

        # 2. Eliminar etiquetas think y líneas de razonamiento interno (chain-of-thought)
        s = cls.THINK_TAG_PATTERN.sub('', s)
        s = cls.CHAIN_OF_THOUGHT_PATTERN.sub('', s)

        # 3. Reemplazar enlaces markdown [texto](url) por solo 'texto'
        s = cls.URL_LINK_PATTERN.sub(r'\1', s)

        # 3. Eliminar placeholders técnicos
        s = cls.PLACEHOLDERS_PATTERN.sub('', s)
        s = cls.TECHNICAL_TOKENS_PATTERN.sub('', s)

        # 4. Evitar repetición excesiva del nombre del usuario
        if user_name:
            clean_name = user_name.strip()
            pattern_name = re.compile(rf'\b{re.escape(clean_name)}\b', re.IGNORECASE)
            matches = list(pattern_name.finditer(s))
            if len(matches) > 1:
                first_end = matches[0].end()
                rest = s[first_end:]
                rest_cleaned = pattern_name.sub('', rest)
                s = s[:first_end] + rest_cleaned

        # 5. Limpieza de puntuación y espacios duplicados (preservando saltos de línea)
        s = re.sub(r'[ \t]+([,.:;?!])', r'\1', s)
        s = re.sub(r'([,.:;?!])\1+', r'\1', s)
        s = re.sub(r'[ \t]{2,}', ' ', s)
        s = re.sub(r'\n{3,}', '\n\n', s).strip()

        # 6. Si después de limpiar el texto queda vacío o solo signos
        if not s or s in [".", ",", "!", "?", "-", ":"]:
            return "Entendido."

        return s

    @classmethod
    def sanitize_for_speech(cls, text: str, user_name: Optional[str] = None) -> str:
        """
        Especialmente adaptado para TTS: expande abreviaturas comunes y elimina símbolos que suenan mal.
        """
        s = cls.sanitize(text, user_name=user_name)
        # Limpiar símbolos markdown que no deben ser leídos en voz alta
        s = cls.MARKDOWN_CLEAN_PATTERN.sub(' ', s)
        
        replacements = [
            (r'\bDr\.', 'Doctor'),
            (r'\bSr\.', 'Señor'),
            (r'\bSra\.', 'Señora'),
            (r'\bvs\b', 'versus'),
            (r'\bej\.', 'por ejemplo'),
            (r'\bapp\b', 'aplicación'),
            (r'\bapps\b', 'aplicaciones'),
            (r'\bPC\b', 'computadora'),
            (r'&', 'y'),
            (r'/', ' o '),
            (r'\\', ' '),
            (r'[%]', ' por ciento'),
            (r'[$]', ' dólares '),
            (r'[€]', ' euros ')
        ]
        for pattern, repl in replacements:
            s = re.sub(pattern, repl, s, flags=re.IGNORECASE)

        s = re.sub(r'\s{2,}', ' ', s).strip()
        return s
