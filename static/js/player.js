// =========================================================================
// JARVIS Assistant — Music & Player Module (v4.0 Mobile-Ready)
// =========================================================================

export class PlayerEngine {
    constructor(options = {}) {
        this.onTrackChange = options.onTrackChange || (() => {});
        this.onPlaybackStateChange = options.onPlaybackStateChange || (() => {});

        this.ytPlayer = null;
        this.isReady = false;
        this.currentTrack = null;
        this.playlist = [];
        this.isPlaying = false;
    }

    initYouTubePlayer(elementId = 'ytplayer') {
        if (typeof YT !== 'undefined' && YT.Player) {
            this._createYT(elementId);
        } else {
            window.onYouTubeIframeAPIReady = () => {
                this._createYT(elementId);
            };
        }
    }

    _createYT(elementId) {
        try {
            this.ytPlayer = new YT.Player(elementId, {
                height: '0',
                width: '0',
                playerVars: {
                    autoplay: 1,
                    controls: 0,
                    disablekb: 1,
                    fs: 0,
                    rel: 0
                },
                events: {
                    onReady: () => {
                        this.isReady = true;
                        console.log('[PlayerEngine] YouTube IFrame Player listo.');
                    },
                    onStateChange: (event) => {
                        if (event.data === YT.PlayerState.PLAYING) {
                            this.isPlaying = true;
                            this.onPlaybackStateChange(true);
                        } else if (event.data === YT.PlayerState.PAUSED || event.data === YT.PlayerState.ENDED) {
                            this.isPlaying = false;
                            this.onPlaybackStateChange(false);
                            if (event.data === YT.PlayerState.ENDED) {
                                this.nextTrack();
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.warn('[PlayerEngine] No se pudo inicializar YouTube Player:', e);
        }
    }

    playTrack(track) {
        if (!track) return;
        this.currentTrack = track;
        this.onTrackChange(track);

        const videoId = track.youtube_id || track.video_id || track.id;
        if (videoId && this.ytPlayer && this.isReady) {
            this.ytPlayer.loadVideoById(videoId);
            this.isPlaying = true;
            this.onPlaybackStateChange(true);
        }
    }

    togglePlayPause() {
        if (!this.ytPlayer || !this.isReady) return;
        if (this.isPlaying) {
            this.ytPlayer.pauseVideo();
        } else {
            this.ytPlayer.playVideo();
        }
    }

    pause() {
        if (this.ytPlayer && this.isReady && this.isPlaying) {
            this.ytPlayer.pauseVideo();
        }
    }

    resume() {
        if (this.ytPlayer && this.isReady && !this.isPlaying) {
            this.ytPlayer.playVideo();
        }
    }

    nextTrack() {
        if (this.playlist.length > 0) {
            const next = this.playlist.shift();
            this.playTrack(next);
        }
    }

    setVolume(volumePercent) {
        if (this.ytPlayer && this.isReady) {
            this.ytPlayer.setVolume(Math.max(0, Math.min(100, volumePercent)));
        }
    }
}

if (typeof window !== 'undefined') {
    window.PlayerEngine = PlayerEngine;
}
