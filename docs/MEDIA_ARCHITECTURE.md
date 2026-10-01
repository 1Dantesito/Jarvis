# ARQUITECTURA MULTIMEDIA DE JARVIS

```
[Usuario / Voz]
       │
[JarvisOrchestrator]
       │
[ToolRouter]
  ├── play_music
  ├── pause_music
  ├── resume_music
  ├── skip_music
  ├── get_now_playing
  ├── get_music_queue
  ├── recommend_music
  └── search_videos
       │
[MusicEngine]
  ├── MusicQueue & SmartQueue (Buffer de 10 canciones continuo)
  ├── RecommendationEngine (Scoring multivariable y contexto)
  ├── MusicHistory & MusicPreferences (Aprendizaje de señales)
  └── Proveedores
        ├── YouTubeProvider (ytmusicapi + IFrame Player)
        └── SpotifyProvider (Spotipy + Web API)
```
