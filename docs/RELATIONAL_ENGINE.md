# Cerebro Relacional de JARVIS — Diagnóstico y Arquitectura (Fase D.1)

> **Documento:** `/docs/RELATIONAL_ENGINE.md`  
> **Fase:** D.1 — Diagnóstico Técnico de Limitaciones Actuales  
> **Estado:** Completado para revisión  
> **Fecha:** 2026-09-23  

---

## 1. INTRODUCCIÓN Y ALCANCE

La **Fase D** tiene como objetivo transformar a JARVIS de un ejecutor reactivo de comandos y asistente conversacional de tono estático en un **compañero relacional con empatía adaptativa, memoria semántica profunda y percepción afectiva longitudinal**.

Antes de introducir nuevos esquemas de datos (D.2) o refactorizar el código fuente, este documento expone una **auditoría técnica exhaustiva de los dos componentes que hoy gestionan la interacción social y la recuperación de memoria**:
1. `SocialResponseLayer` ([`core/social_layer.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/social_layer.py))
2. `MemoryRetriever` ([`core/memory_retriever.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_retriever.py)) y su orquestación en [`core/memory_manager.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_manager.py) y [`core/orchestrator.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/orchestrator.py).

---

## 2. DIAGNÓSTICO: LIMITACIONES DE `SocialResponseLayer`

### 2.1. Detección de Estado Superficial y Frágil (Keywords / Regex Naive)
- **Implementación actual:** `SocialResponseLayer.detect_state(user_text)` aplica evaluaciones `any(w in low for w in [...])` sobre listas hardcodeadas de 3 a 8 cadenas literales.
- **Vulnerabilidad a Negaciones y Contexto:**
  - Si el usuario dice *"No estoy cansado, solo quiero terminar rápido"*, el substring `"estoy cansado"` se activa y clasifica el turno erróneamente como `ConversationState.EMPATHETIC`.
  - Frases humanas naturales como *"ha sido un día demoledor"*, *"no doy más del estrés"*, *"me despidieron"* o *"siento que no avanzo"* no coinciden con las 5 palabras clave de empatía (`"estoy cansado"`, `"tuve un mal día"`, `"estoy agotado"`, `"me siento mal"`, `"estoy estresado"`) y caen silenciosamente por defecto en `ConversationState.CASUAL`.
- **Incapacidad de Graduación Afectiva:** Trata el estado como un enum binario y discreto, sin valencia (-1.0 a +1.0), ni nivel de activación/arousal (baja energía vs. alta angustia/urgencia).

### 2.2. Amnesia Multiturno y Ausencia de Estado Relacional
- **Stateless absoluto:** El método `detect_state` recibe únicamente el texto del turno en curso (`user_text: str`). No conoce el turno previo ni el flujo conversacional.
- **Efecto en la experiencia:**
  - *Turno 1:* Usuario: *"Hoy fue uno de los peores días de mi vida..."* $\rightarrow$ Clasificado como `EMPATHETIC`.
  - *Turno 2:* JARVIS: *"Lo lamento mucho. ¿Quieres que hablemos o prefieres desconectar?"*
  - *Turno 3:* Usuario: *"No sé, tal vez desconectar un rato..."* $\rightarrow$ Como el turno 3 no contiene las palabras mágicas, el clasificador lo etiqueta como `CASUAL` y responde con tono neutro o conversacional genérico, rompiendo la empatía alcanzada.
- **Falta de vínculo persistente (`RelationshipState`):** No existe registro de afinidad acumulada, nivel de intimidad o familiaridad (ej. primer día de uso vs. 6 meses de pair-programming diario), ni seguimiento de temas sensibles para el usuario.

### 2.3. Respuestas de Herramientas Estáticas (`format_social_tool_phrase`)
- En [`core/social_layer.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/social_layer.py#L53), las confirmaciones de herramientas se resuelven mediante cadenas fijas con branching `if/elif` o un `random.choice` de 2 elementos.
- No existe modulación situacional: un recordatorio creado bajo un contexto de urgencia médica o estrés se confirma con la misma frase idéntica que uno creado en un momento de ocio.

### 2.4. Desconexión de `PersonalityProfile` frente a la Inferencia Real
- [`core/user_profile.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/user_profile.py) declara 6 dimensiones numéricas (1 a 5): `verbosity`, `humor`, `formality`, `technicality`, `warmth`, `playfulness`.
- **Brecha en el código:** Solo `verbosity` y `humor` alteran realmente el string generado por `to_instruction()`. Los parámetros `formality`, `technicality`, `warmth` y `playfulness` son campos pasivos que no impactan de forma diferenciada las instrucciones del sistema ni los parámetros de muestreo del LLM.

---

## 3. DIAGNÓSTICO: LIMITACIONES DE `MemoryRetriever`

### 3.1. Scoring Léxico Literal y Cero Comprensión Semántica
- **Implementación actual:**
  ```python
  words = set(re.findall(r'\w+', clean_q))
  mem_words = set(re.findall(r'\w+', mem_text))
  overlap = len(words.intersection(mem_words))
  relevance = min(1.0, overlap * 0.4)
  ```
- **Fallas críticas:**
  - Si el usuario pregunta *"¿Qué videojuegos me recomiendas?"*, y en memoria está guardado `key="gusto_gaming", value="Fanático de Devil May Cry y shooters de acción"`, la intersección léxica entre `{qué, videojuegos, me, recomiendas}` y `{gusto, gaming, fanático, de, devil, may, cry, y, shooters, de, acción}` es prácticamente nula (solo conectores comunes), arrojando `relevance = 0.0`.
  - Sinónimos universales (*auto/coche/carro*, *trabajo/empleo/empresa*, *tristeza/desánimo*, *canción/tema/track*) son invisibles para el motor.

### 3.2. Falso Cálculo de Recencia (`Recency = 0.20` Constante)
- En [`core/memory_retriever.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_retriever.py#L37):
  ```python
  final_score = (relevance * 0.35) + (importance * 0.25) + (confidence * 0.20) + (0.20)
  ```
  El término `0.20` representa la recencia según la docstring del componente, pero está **fijado como una constante estática**. No calcula diferencias temporales ($\Delta t$) respecto a `created_at` o `last_used_at`, ni aplica decaimiento temporal exponencial o logarítmico. Una memoria creada hace 2 años tiene exactamente el mismo score de recencia que una creada hace 2 minutos.

### 3.3. Inversión de Selección y Cuello de Botella en SQLite
- En [`core/memory_manager.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_manager.py#L172):
  ```python
  def get_contextual_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
      all_mems = self.recall_memories(limit=50)
      return MemoryRetriever.retrieve_relevant(all_mems, query, limit=limit)
  ```
  `recall_memories(limit=50)` hace un `SELECT ... ORDER BY id DESC LIMIT 50`.
  - Si el usuario tiene 150 recuerdos acumulados, y un recuerdo fundamental sobre su salud, preferencias familiares o configuración laboral quedó en la posición 51 hacia atrás, **jamás entrará al filtro de relevancia**, independientemente de lo crítico que sea para la pregunta actual.

### 3.4. Reglas Heurísticas Invasivas y No Escalables
- Líneas 29-33 de `memory_retriever.py`:
  ```python
  if any(w in clean_q for w in ["música", "musica", "cancion", "rock", "metal"]) and mem.get("type") == "MEDIA_PREFERENCE":
      relevance = max(relevance, 0.8)
  elif any(w in clean_q for w in ["proyecto", "tesis", "jarvis", "trabajo"]) and mem.get("type") == "PROJECT":
      relevance = max(relevance, 0.85)
  ```
  El motor tiene favoritismos explícitos cableados solo para "música" y "proyectos". Cualquier otra categoría (relaciones personales, salud, deportes, finanzas, hábitos alimenticios) carece de este boost artificial y es tratada con inferioridad en el ranking.

### 3.5. Ausencia de Token Budget y Desincronización de Caché del Orquestador
1. **Presupuesto de tokens ficticio:** A pesar de que la clase proclama un *"presupuesto de tokens"*, simplemente aplica un slice estático `[:limit]`, sin calcular tokens reales ni adaptarse al límite de la ventana de contexto.
2. **Caché de Sistema Ciego de 20 Segundos:** En [`core/orchestrator.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/orchestrator.py#L170), el método `_build_system_instruction` tiene una caché `_sysinstruction_cache` con TTL de 20 segundos. Si el usuario hace dos preguntas seguidas con temas dispares dentro de ese intervalo, la segunda pregunta se ejecuta con los recuerdos contextuales inyectados para la primera.

---

## 4. MATRIZ COMPARATIVA: ESTADO ACTUAL VS. OBJETIVO FASE D

| Dimensión | Estado Actual (JARVIS v3.x / Pre-D) | Objetivo Fase D (Cerebro Relacional) |
| :--- | :--- | :--- |
| **Detección de Afecto** | Keywords fijas en string; sensible a fallos por negación y vocabulario. | Análisis de valencia (-1.0 a +1.0) y activación emocional, con fallback probabilístico / LLM. |
| **Continuidad Emocional** | Mono-turno amnésico. Cada turno reinicia a `CASUAL`. | `RelationshipState` continuo con inercia afectiva y seguimiento multiturno. |
| **Dimensiones de Personalidad** | 6 variables en UserProfile, solo 2 usadas en el prompt. | Esquema unificado `personality_traits` con traducción dinámica y calibración continua. |
| **Recuperación de Memoria** | Intersección de sets de palabras (`len(words & mem_words)`). | Búsqueda semántica (embeddings / similitud coseno) + BM25 híbrido + normalización léxica. |
| **Decaimiento Temporal** | Constante fija `+0.20`. | Fórmula real de decaimiento temporal basada en medio-vida y frecuencia de refuerzo ($e^{-\lambda \Delta t}$). |
| **Filtrado en Base de Datos** | Trae los últimos 50 por ID y descarta el resto. | Búsqueda indexada en base de datos sin límite prematuro antes del ranking. |
| **Caché Contextual** | Caché estático de 20 segundos que mezcla recuerdos entre temas. | Inyección de memoria contextual recalculada por intención sin romper el event loop. |

---

## 5. PLAN TÉCNICO DE EJECUCIÓN PARA FASE D

Una vez aprobado este diagnóstico (D.1), la secuencia rigurosa de desarrollo será:

1. **Sub-fase D.2:** Definición y validación de los 3 esquemas JSON fundamentales (`relationship_state.json`, `personality_traits.json`, `semantic_memory_entry.json`).
2. **Sub-fase D.3:** Implementación del motor de memoria semántica con ranking híbrido y decaimiento exponencial real sin dependencias externas pesadas.
3. **Sub-fase D.4:** Implementación de la capa relacional multiturno y guardián de seguridad (`CrisisSafetyGuard`) en el orquestador.
4. **Sub-fase D.5:** Suite de pruebas automatizadas dedicadas (`tests/test_relational_engine.py`) con cobertura completa y 0 regresiones en las 194 pruebas existentes.

---

## 6. ARQUITECTURA DE SEGURIDAD EN DOS CAPAS: `CrisisSafetyGuard`

Dado que el riesgo autolítico y la aflicción extrema constituyen el vector de seguridad más crítico del asistente, este componente opera bajo una **arquitectura híbrida de dos capas diseñada para superar el techo estructural de los sistemas basados únicamente en reglas**:

> [!CAUTION]
> **DECLARACIÓN EXPLÍCITA DE LÍMITES CLÍNICOS:**  
> `CrisisSafetyGuard` es un **módulo heurístico y algorítmico de mitigación de daños**, **NO** un dispositivo médico ni un clasificador psicométrico clínicamente validado. No sustituye la intervención psiquiátrica ni el criterio humano calificado. Su propósito exclusivo es la contención primaria inmediata y la derivación urgente a líneas profesionales acreditadas. Requiere auditoría y revisión humana periódica.

### 6.1. Evidencia Empírica del Techo de Generalización (Colapso al 27.3%)

Durante la auditoría de D.1/D.2 se comprobó experimentalmente que un enfoque exclusivo de expresiones regulares tiene un **techo estructural insalvable**:
- En un **lote adversarial ciego de 22 frases** formuladas con lenguaje coloquial real (sin tildes, con metáforas poéticas, llanto o desesperanza velada), el detector basado puramente en regex rígido **colapsó a un 27.3% de efectividad (6 de 22 aciertos)**.
- Parchear expresiones regulares ad-hoc para alcanzar el 100% sobre un conjunto conocido simplemente traslada el sobre-ajuste al siguiente lote. La ambigüedad humana, el sarcasmo, el dolor velado y las paráfrasis inéditas exigen comprensión contextual profunda.
- **Conclusión arquitectónica:** Ningún sistema de reglas estáticas puede ser la única barrera de contención para riesgo vital. Se requiere una arquitectura en dos capas.

### 6.2. Arquitectura en Dos Capas (Fast-Path Determinista + Clasificador LLM Aislado)

```
                            [Mensaje del Usuario]
                                      │
                   [Normalización Unicode NFD previa]
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │ CAPA 1: Fast-Path Determinista (Regex Normalizado) │
             │ - Latencia 0 ms                                  │
             │ - Solo casos explícitos de máxima confianza:     │
             │   método letal, acopio, despedida inequívoca     │
             └────────────────────────┬─────────────────────────┘
                                      │
                      ¿Disparo de alta confianza?
                                     ╱ ╲
                               SI  ╱     ╲  NO / Dudoso
                                 ▼         ▼
                    ┌─────────────────┐  ¿Contiene carga emocional negativa,
                    │ CRISIS INMEDIATA│  tristeza, fatiga o dolor existencial?
                    │ (Líneas Ayuda)  │             │
                    └─────────────────┘      SI    ╱ ╲   NO (Neutro/Técnico)
                                                   ▼   ▼
             ┌──────────────────────────────────────────────┐  ┌──────────────┐
             │ CAPA 2: Evaluador LLM Aislado y Especializado │  │ Flujo Normal │
             │ - Invocación independiente al proveedor      │  └──────────────┘
             │ - Prompt dedicado de seguridad:              │
             │   "¿Indicios directos/indirectos de autolisis│
             │    o autolesión? [SI / NO / AMBIGUO]"        │
             └───────────────────────┬──────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ▼               ▼               ▼
                 Respuesta:      Respuesta:      Respuesta:
                     SI           AMBIGUO            NO
                     │               │               │
                     ▼               ▼               ▼
               [MODO CRISIS]   [CONTENCIÓN     [Flujo Normal]
                                  SUAVE]
```

#### Capa 1: Red de Seguridad Determinista (Latencia 0 ms)
- Opera en memoria local en $<0.5$ ms.
- Limitada estrictamente a **casos explícitos de máxima confianza**: menciones directas de métodos, veneno/fármacos, precipitación, armas o despedidas inequívocas de muerte inminente.
- Si dispara: activa `CRISIS` de inmediato sin esperar a la red ni al LLM.

#### Capa 2: Clasificador Aislado de Seguridad con LLM
- Si la Capa 1 no dispara con alta confianza, pero el mensaje presenta carga afectiva negativa o ambigüedad existencial:
- El orquestador ejecuta una evaluación específica e independiente hacia el proveedor de IA configurado (Gemini / OpenRouter), **totalmente separada del prompt conversacional general**.
- **Prompt dedicado del clasificador de seguridad:**
  > *"Actúa como un evaluador de seguridad clínica estricto. Analiza el siguiente mensaje del usuario: '{mensaje}'. ¿Contiene indicios directos, indirectos, velados o metafóricos de ideación suicida, autolesión o desesperanza terminal? Responde ÚNICAMENTE con una de estas tres palabras: SI, NO o AMBIGUO."*
- Esta capa comprende metáforas (*"me rindo, ganó la oscuridad"*), despedidas sutiles (*"gracias por todo lo que hiciste jarvis, adiós"*) y paráfrasis que escapan al análisis de cadenas.

#### Regla de Sesgo Conservador Estricto
- Si la Capa 2 responde **`SI`** $\rightarrow$ Clasifica incondicionalmente como **`CRISIS`**.
- Si la Capa 2 responde **`AMBIGUO`**, o si la llamada al LLM falla o tiene latencia anormal $\rightarrow$ Clasifica automáticamente como mínimo en **`MILD` (Contención Suave)**. **NUNCA clasifica como `NORMAL` por defecto ante la duda.**
- Solo si responde **`NO`** con certeza y no hay marcadores de riesgo $\rightarrow$ Permite la continuidad del diálogo normal.

### 6.3. Comportamiento en Banda Intermedia ("Contención Suave" / AMBIGUO)
- **Bloqueo preventivo de automatizaciones:** Prohibida la ejecución de herramientas de escritorio o comandos operativos.
- **Tono y Voz:** Cadencia pausada (`tempo_factor: 0.90`), estilo `gentle_grounded`.
- **Respuesta canónica:** Validación empática sin juicios, presencia de escucha activa y pregunta abierta sobre su bienestar inmediato, sin emitir diagnósticos.

### 6.4. Directorio Dinámico de Crisis Vía `LocationProvider` (Zero-Latency / Cache-Only)
- **Acceso exclusivo a memoria RAM:** Lee `LocationProvider.get_cached_country_code()` en $<0.1$ ms. Cero llamadas HTTP bloqueantes durante la emergencia.
- **Mapeo:** CO (106 / 192), MX (800 911 2000), ES (024 / 717 033 717), US (988), AR (135), CL (*4141).
- **Fallback Universal Inmediato:** Si no hay caché o el país no está listado:
  *"Por favor, comunícate de inmediato con el número de emergencias de tu localidad (como el 123 o 911), acude al centro de salud más cercano o habla con alguien de tu entera confianza ahora mismo."*
- **Auditoría periódica:** Directorio sujeto a verificación humana al menos semestral.

### 6.5. Mecanismo de Salida Multiturno Sostenido (Anti-Enmascaramiento)
- **Prohibida la salida en un solo turno:** Frases como *"ya estoy bien"* o *"tranquilo"* no apagan el protocolo (riesgo de enmascaramiento).
- **Estabilidad dialogada mínima de 2 turnos:**
  - *Turno 1 post-crisis:* JARVIS valida el alivio y explora si el usuario cuenta con acompañamiento real.
  - *Turno 2 post-crisis:* Solo si se confirma estabilidad reflexiva y ausencia de riesgo, pasa a `MONITORING_COOLDOWN`.
- **Cool-down de 3 turnos:** Herramientas de impacto bloqueadas bajo confirmación reforzada y estilo en `gentle_grounded`.

---

## 7. REGISTRO DE IMPLEMENTACIÓN Y VALIDACIÓN (Sub-fases D.2, D.3 & D.4 Checkpoint)

| Componente | Archivo | Estado | Cobertura / Pruebas |
| :--- | :--- | :--- | :--- |
| **CrisisSafetyGuard** | [`core/crisis_guard.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/crisis_guard.py) | **Implementado** | 14 pruebas unitarias + E2E integradas con Orquestador |
| **Circuit Breaker Capa 2** | [`core/crisis_guard.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/crisis_guard.py) | **Implementado** | Trip a 3 fallos -> Cooldown -> Recuperación HALF-OPEN a CLOSED |
| **Gating Permisivo de Afecto** | [`core/crisis_guard.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/crisis_guard.py) | **Implementado** | Normalización NFD idéntica a Capa 1 y 21 familias de patrones |
| **Location Cache Zero-Latency** | [`core/location_provider.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/location_provider.py) | **Implementado** | `get_cached_country_code()` en RAM (0 ms) |
| **LocalSemanticVectorizer (128D)** | [`core/semantic_vectorizer.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/semantic_vectorizer.py) | **Implementado** | Feature Hashing determinista L2 offline (0 ms / 0 tokens) |
| **Modelos Aditivos SQLite (D.3)** | [`core/database.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/database.py) | **Implementado** | `semantic_memories`, `relationship_state`, `personality_traits` |
| **MemoryRetriever Híbrido & Recency** | [`core/memory_retriever.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_retriever.py) | **Implementado** | Híbrido léxico/semántico + decaimiento exponencial real ($e^{-\Delta t / 30}$) |
| **Dual-Write Memoria Semántica** | [`core/memory_manager.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/memory_manager.py) | **Implementado** | Escritura dual `memories`/`semantic_memories` + pool extendido de 500 |
| **RelationshipManager (D.4)** | [`core/relationship_manager.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/relationship_manager.py) | **Implementado** | Inercia afectiva (60/40), modos conversacionales y límites éticos |
| **Wiring Orquestador Multiturno** | [`core/orchestrator.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/core/orchestrator.py) | **Implementado** | `record_turn` fail-silent en sync/stream, prompt relacional y caché por query |
| **Tests Aislados Componentes** | [`tests/test_relational_components.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/tests/test_relational_components.py) | **Implementado** | 21 pruebas unitarias independientes |
| **Tests Integración Orquestador** | [`tests/test_relational_orchestrator.py`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/tests/test_relational_orchestrator.py) | **Implementado** | 10 pruebas de integración multiturno |
| **Suite Completa del Proyecto** | `tests/` | **247 / 247 Pasadas** | Cero fallos, cero regresiones en toda la base de código |

---

## 8. HITOS CULMINADOS EN FASE D.4

1. **Inercia Afectiva Multiturno (Anti-Amnesia):** Ponderación $60\%$ de estado previo y $40\%$ de estímulo actual para mitigar el colapso abrupto de tono entre turnos sucesivos.
2. **Límites Éticos Explícitos (D.4):** Reglas inviolables inyectadas en el prompt del sistema que impiden simular biología humana, brindar asesoría clínica/médica o generar dependencia afectiva artificial.
3. **Recuperación Semántica de Pool Completo:** Se eliminó el cuello de botella previo de los 50 elementos arbitrarios en SQLite, ampliando la evaluación contextual a 500 registros con scoring multivariable.
4. **Caché Inteligente por Consulta:** El orquestador ya no reutiliza ciegamente un prompt de sistema si la intención del usuario cambió respecto a la interacción previa.




