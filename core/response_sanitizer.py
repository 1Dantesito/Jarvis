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

        # 6. Embellecer formato Markdown (separar listas pegadas en renglones limpios)
        s = cls.format_beautiful_markdown(s)

        # 7. Si después de limpiar el texto queda vacío o solo signos
        if not s or s in [".", ",", "!", "?", "-", ":"]:
            return "Entendido."

        return s

    @classmethod
    def format_beautiful_markdown(cls, text: str) -> str:
        """
        Formatea y embellece la estructura del texto para presentación en pantalla.
        Convierte listas pegadas o inline (ej. ': 1. ... 2. ...') en listas Markdown
        con saltos de línea elegantes y separación de párrafos.
        """
        if not text:
            return ""

        # 0. Proteger bloques de código (```...```) para no alterar JSONs o scripts
        blocks = []
        def _save_block(m):
            blocks.append(m.group(0))
            return f"__CODE_BLOCK_PRESERVE_{len(blocks)-1}__"

        s = re.sub(r'```[a-zA-Z0-9_\-]*\n[\s\S]*?```', _save_block, text)

        # 1. Separar encabezado previo a una lista numerada (ej. 'menos pensado: 1. ' -> 'menos pensado:\n\n1. ')
        s = re.sub(r'([:;])\s+(?=\d+\.\s+)', r'\1\n\n', s)

        # 2. Separar elementos de lista numerada pegados en el mismo renglón (ej. 'intento. 2. ' -> 'intento.\n\n2. ')
        s = re.sub(r'([.?!])\s+(?=\d+\.\s+)', r'\1\n\n', s)

        # 3. Separar elementos de viñetas pegados (ej. 'opciones: - ' o '. - ')
        s = re.sub(r'([:;.?!])\s+(?=[-•*]\s+)', r'\1\n\n', s)
        s = re.sub(r'(?<=[^\s:;.?!])\s+[-•*]\s+(?=[A-ZÁÉÍÓÚ]|\*\*)', r'\n\n- ', s)

        # 4. Normalizar viñetas unicode (•, ·) a guiones markdown estándar
        s = re.sub(r'(?:^|\n)[ \t]*[•·]\s+', r'\n- ', s)

        # 5. Separar preguntas o conclusiones finales después de una lista numerada
        s = re.sub(r'(\d+\.[^\n]+?[.?!])\s+([¿¡A-ZÁÉÍÓÚ][^\n]{3,})', r'\1\n\n\2', s)

        # 6. Normalizar saltos excesivos a máximo 2 saltos
        s = re.sub(r'\n{3,}', '\n\n', s)

        # 7. Restaurar bloques de código preservados
        for idx, block in enumerate(blocks):
            s = s.replace(f"__CODE_BLOCK_PRESERVE_{idx}__", block)

        return s.strip()

    @classmethod
    def sanitize_for_speech(cls, text: str, user_name: Optional[str] = None) -> str:
        """
        Especialmente adaptado para TTS: expande abreviaturas comunes y elimina símbolos que suenan mal.
        Convierte bloques interactivos (cards, checklist, comparativa) en descripciones auditivas naturales.
        """
        if not text:
            return ""

        s = text

        # Convertir bloques interactivos JSON en habla natural
        def _speech_cards(m):
            raw_json = m.group(1).strip()
            try:
                import json
                items = json.loads(raw_json)
                if isinstance(items, list):
                    titles = [item.get("title", "") for item in items if isinstance(item, dict) and item.get("title")]
                    if titles:
                        if len(titles) <= 4:
                            return " Aquí tienes: " + ", ".join(titles) + ". "
                        return " Te he preparado varias opciones en tarjetas en tu pantalla. "
            except Exception:
                pass
            return " Te muestro las tarjetas detalladas en pantalla. "

        def _speech_checklist(m):
            raw_json = m.group(1).strip()
            try:
                import json
                data = json.loads(raw_json)
                title = data.get("title", "la lista interactiva")
                return f" He preparado {title} en pantalla para que puedas verificar los puntos. "
            except Exception:
                pass
            return " He preparado la guía interactiva en pantalla. "

        def _speech_comparativa(m):
            raw_json = m.group(1).strip()
            try:
                import json
                data = json.loads(raw_json)
                title = data.get("title", "el cuadro comparativo")
                return f" He organizado {title} en pantalla. "
            except Exception:
                pass
            return " He organizado el cuadro comparativo en pantalla. "

        s = re.sub(r'```(?:cards|flashcards)\s*\n([\s\S]*?)```', _speech_cards, s)
        s = re.sub(r'```checklist\s*\n([\s\S]*?)```', _speech_checklist, s)
        s = re.sub(r'```(?:comparativa|comparison)\s*\n([\s\S]*?)```', _speech_comparativa, s)
        # Limpiar cualquier otro bloque de código restante para que no lea código crudo
        s = re.sub(r'```[a-zA-Z0-9_\-]*\n[\s\S]*?```', ' ', s)

        s = cls.sanitize(s, user_name=user_name)
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
