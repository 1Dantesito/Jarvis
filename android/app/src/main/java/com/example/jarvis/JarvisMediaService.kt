package com.example.jarvis

import android.app.*
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.media.AudioManager
import android.media.MediaMetadata
import android.media.session.MediaSession
import android.media.session.PlaybackState
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager

class JarvisMediaService : Service() {

    companion object {
        const val CHANNEL_ID = "jarvis_music_playback_channel"
        const val NOTIFICATION_ID = 2001

        const val ACTION_START = "com.example.jarvis.action.START"
        const val ACTION_PAUSE = "com.example.jarvis.action.PAUSE"
        const val ACTION_PLAY = "com.example.jarvis.action.PLAY"
        const val ACTION_NEXT = "com.example.jarvis.action.NEXT"
        const val ACTION_PREV = "com.example.jarvis.action.PREV"
        const val ACTION_STOP = "com.example.jarvis.action.STOP"

        const val EXTRA_TITLE = "extra_title"
        const val EXTRA_ARTIST = "extra_artist"
        const val EXTRA_IS_PLAYING = "extra_is_playing"

        var isServiceRunning = false
        var playbackListener: PlaybackControlListener? = null
    }

    interface PlaybackControlListener {
        fun onNativePlay()
        fun onNativePause()
        fun onNativeNext()
        fun onNativePrev()
    }

    private var mediaSession: MediaSession? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private var wifiLock: WifiManager.WifiLock? = null

    private var currentTitle: String = "Música"
    private var currentArtist: String = "JARVIS AI"
    private var isPlaying: Boolean = false

    // Receptor para detectar desconexión de audífonos (cable o Bluetooth)
    private val noisyReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == AudioManager.ACTION_AUDIO_BECOMING_NOISY) {
                // Al desconectar audífonos, pausar automáticamente para no sonar por el altavoz
                playbackListener?.onNativePause()
                updatePlaybackState(false)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        isServiceRunning = true

        createNotificationChannel()
        initMediaSession()
        initLocks()

        try {
            registerReceiver(noisyReceiver, IntentFilter(AudioManager.ACTION_AUDIO_BECOMING_NOISY))
        } catch (e: Exception) {
            // Ignorar si ya está registrado
        }
    }

    private fun initMediaSession() {
        mediaSession = MediaSession(this, "JarvisMediaSession").apply {
            setCallback(object : MediaSession.Callback() {
                override fun onPlay() {
                    playbackListener?.onNativePlay()
                    updatePlaybackState(true)
                }

                override fun onPause() {
                    playbackListener?.onNativePause()
                    updatePlaybackState(false)
                }

                override fun onSkipToNext() {
                    playbackListener?.onNativeNext()
                }

                override fun onSkipToPrevious() {
                    playbackListener?.onNativePrev()
                }

                override fun onMediaButtonEvent(mediaButtonIntent: Intent): Boolean {
                    // Manejo nativo de botones de audífonos cableados y Bluetooth
                    return super.onMediaButtonEvent(mediaButtonIntent)
                }
            })
            isActive = true
        }
    }

    private fun initLocks() {
        try {
            val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
            wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "JARVIS:MusicWakeLock").apply {
                setReferenceCounted(false)
            }
        } catch (e: Exception) {}

        try {
            val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            wifiLock = wifiManager.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "JARVIS:MusicWifiLock").apply {
                setReferenceCounted(false)
            }
        } catch (e: Exception) {}
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "JARVIS Reproducción en Segundo Plano",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Mantiene la reproducción activa con pantalla apagada y en audífonos"
                setShowBadge(false)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action

        intent?.getStringExtra(EXTRA_TITLE)?.let {
            if (it.isNotBlank()) currentTitle = it
        }
        intent?.getStringExtra(EXTRA_ARTIST)?.let {
            if (it.isNotBlank()) currentArtist = it
        }

        when (action) {
            ACTION_PLAY -> {
                isPlaying = true
                acquireLocks()
                updatePlaybackState(true)
                playbackListener?.onNativePlay()
            }
            ACTION_PAUSE -> {
                isPlaying = false
                releaseLocks()
                updatePlaybackState(false)
                playbackListener?.onNativePause()
            }
            ACTION_NEXT -> {
                playbackListener?.onNativeNext()
            }
            ACTION_PREV -> {
                playbackListener?.onNativePrev()
            }
            ACTION_STOP -> {
                stopSelf()
                return START_NOT_STICKY
            }
            else -> {
                val state = intent?.getBooleanExtra(EXTRA_IS_PLAYING, true) ?: true
                isPlaying = state
                if (isPlaying) acquireLocks() else releaseLocks()
                updatePlaybackState(isPlaying)
            }
        }

        return START_STICKY
    }

    private fun acquireLocks() {
        try {
            if (wakeLock?.isHeld != true) {
                wakeLock?.acquire(8 * 60 * 60 * 1000L) // 8 horas máximo de wakelock para no drenar batería indefinidamente
            }
            if (wifiLock?.isHeld != true) {
                wifiLock?.acquire()
            }
        } catch (e: Exception) {}
    }

    private fun releaseLocks() {
        try {
            if (wakeLock?.isHeld == true) wakeLock?.release()
            if (wifiLock?.isHeld == true) wifiLock?.release()
        } catch (e: Exception) {}
    }

    private fun updatePlaybackState(playing: Boolean) {
        isPlaying = playing

        // 1. Actualizar metadata de MediaSession (para pantalla de bloqueo, audífonos y smartwatch)
        mediaSession?.setMetadata(
            MediaMetadata.Builder()
                .putString(MediaMetadata.METADATA_KEY_TITLE, currentTitle)
                .putString(MediaMetadata.METADATA_KEY_ARTIST, currentArtist)
                .build()
        )

        val stateCode = if (playing) PlaybackState.STATE_PLAYING else PlaybackState.STATE_PAUSED
        val actions = PlaybackState.ACTION_PLAY or
                PlaybackState.ACTION_PAUSE or
                PlaybackState.ACTION_PLAY_PAUSE or
                PlaybackState.ACTION_SKIP_TO_NEXT or
                PlaybackState.ACTION_SKIP_TO_PREVIOUS

        mediaSession?.setPlaybackState(
            PlaybackState.Builder()
                .setActions(actions)
                .setState(stateCode, PlaybackState.PLAYBACK_POSITION_UNKNOWN, 1.0f)
                .build()
        )

        // 2. Construir notificación con MediaStyle
        val notification = buildMediaNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun buildMediaNotification(): Notification {
        val openAppIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            },
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val prevIntent = createServicePendingIntent(ACTION_PREV)
        val playPauseIntent = if (isPlaying) createServicePendingIntent(ACTION_PAUSE) else createServicePendingIntent(ACTION_PLAY)
        val nextIntent = createServicePendingIntent(ACTION_NEXT)

        val playPauseIcon = if (isPlaying) android.R.drawable.ic_media_pause else android.R.drawable.ic_media_play
        val playPauseTitle = if (isPlaying) "Pausar" else "Reproducir"

        val builder = Notification.Builder(this, CHANNEL_ID)
            .setContentTitle(currentTitle)
            .setContentText(currentArtist)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setContentIntent(openAppIntent)
            .setVisibility(Notification.VISIBILITY_PUBLIC)
            .setOngoing(isPlaying)
            .addAction(
                Notification.Action.Builder(
                    android.R.drawable.ic_media_previous,
                    "Anterior",
                    prevIntent
                ).build()
            )
            .addAction(
                Notification.Action.Builder(
                    playPauseIcon,
                    playPauseTitle,
                    playPauseIntent
                ).build()
            )
            .addAction(
                Notification.Action.Builder(
                    android.R.drawable.ic_media_next,
                    "Siguiente",
                    nextIntent
                ).build()
            )

        if (mediaSession != null) {
            builder.style = Notification.MediaStyle()
                .setMediaSession(mediaSession!!.sessionToken)
                .setShowActionsInCompactView(0, 1, 2)
        }

        return builder.build()
    }

    private fun createServicePendingIntent(action: String): PendingIntent {
        val intent = Intent(this, JarvisMediaService::class.java).apply {
            this.action = action
        }
        return PendingIntent.getService(
            this,
            action.hashCode(),
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
    }

    override fun onDestroy() {
        isServiceRunning = false
        releaseLocks()

        try {
            unregisterReceiver(noisyReceiver)
        } catch (e: Exception) {}

        mediaSession?.isActive = false
        mediaSession?.release()
        mediaSession = null

        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
