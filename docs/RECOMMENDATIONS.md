# MOTOR DE RECOMENDACIÓN EXPLICABLE

## Fórmula de Puntuación de Pistas:
$$	ext{Score} = 	ext{ArtistAffinity} + 	ext{GenreAffinity} + 	ext{ContextMatch} + 	ext{CompletedBonus} - 	ext{SkipPenalty} - 	ext{RecentRepeatPenalty}$$

## Señales de Aprendizaje:
- `TRACK_COMPLETED`: Incrementa afinidad con el artista (+0.05).
- `TRACK_REPLAYED`: Incrementa fuertemente la afinidad (+0.10).
- `TRACK_SKIPPED`: Aplica penalización gradual (-0.05 a -0.08).
- `RecentRepeat`: Excluye de forma determinística temas reproducidos en las últimas 10 canciones para evitar repeticiones continuas.
