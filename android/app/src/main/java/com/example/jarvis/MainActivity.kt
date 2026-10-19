package com.example.jarvis

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.webkit.*
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity(), JarvisMediaService.PlaybackControlListener {

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var errorLayout: LinearLayout
    private lateinit var prefs: SharedPreferences

    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private var cameraPhotoPath: String? = null
    private var isMusicPlaying: Boolean = false

    private val PREFS_NAME = "jarvis_mobile_prefs"
    private val KEY_SERVER_URL = "server_url"
    private val DEFAULT_URL = "http://192.168.1.62:5001"

    private val requestPermissionsLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { _ ->
        // Permisos concedidos para audio y cámara
    }

    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (filePathCallback != null) {
            val results: Array<Uri>? = if (result.resultCode == RESULT_OK) {
                if (result.data?.data != null) {
                    arrayOf(result.data!!.data!!)
                } else if (cameraPhotoPath != null) {
                    val file = File(cameraPhotoPath!!)
                    if (file.exists()) arrayOf(Uri.fromFile(file)) else null
                } else {
                    null
                }
            } else null
            filePathCallback?.onReceiveValue(results)
            filePathCallback = null
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        JarvisMediaService.playbackListener = this
        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        // 1. Solicitar permisos de micrófono y cámara en tiempo de ejecución
        requestRuntimePermissions()

        // 2. Construir Layout nativo de alta estética Dark Glassmorphic
        val rootLayout = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#080D14"))
        }

        // WebView principal
        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#080D14"))
            setupWebView(this)
        }
        rootLayout.addView(webView)

        // Barra de progreso cian neon
        progressBar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dpToPx(3)
            ).apply {
                gravity = Gravity.TOP
            }
            isIndeterminate = false
            max = 100
            progressDrawable = createProgressBarDrawable()
            visibility = View.GONE
        }
        rootLayout.addView(progressBar)

        // Botón flotante estilizado para ajustes de servidor (Gear)
        val btnSettings = Button(this).apply {
            val size = dpToPx(42)
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.TOP or Gravity.END
                setMargins(0, dpToPx(16), dpToPx(16), 0)
            }
            text = "⚙️"
            textSize = 18f
            setTextColor(Color.WHITE)
            background = createGlassButtonDrawable()
            elevation = dpToPx(6).toFloat()
            setOnClickListener { showServerUrlDialog() }
        }
        rootLayout.addView(btnSettings)

        // Pantalla de error / reconexión estética
        errorLayout = createErrorLayout()
        rootLayout.addView(errorLayout)

        setContentView(rootLayout)

        // 3. Cargar la URL guardada o predeterminada
        loadSavedServerUrl()
    }

    private fun requestRuntimePermissions() {
        val permissions = mutableListOf<String>()
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.RECORD_AUDIO)
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.CAMERA)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
        if (permissions.isNotEmpty()) {
            requestPermissionsLauncher.launch(permissions.toTypedArray())
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView(wv: WebView) {
        val s = wv.settings
        s.javaScriptEnabled = true
        s.domStorageEnabled = true
        s.databaseEnabled = true
        s.mediaPlaybackRequiresUserGesture = false // Permite que JARVIS hable sin requerir clics previos
        s.allowFileAccess = true
        s.allowContentAccess = true
        s.loadWithOverviewMode = true
        s.useWideViewPort = true
        s.cacheMode = WebSettings.LOAD_DEFAULT
        s.setOffscreenPreRaster(true)

        // Habilitar cookies de terceros para YouTube y servicios de streaming
        CookieManager.getInstance().setAcceptThirdPartyCookies(wv, true)

        // Registrar puente nativo para sincronizar estado de música y controles de audífonos
        wv.addJavascriptInterface(JarvisJsBridge(this), "AndroidJarvis")

        // Eliminar 'wv' del User-Agent para compatibilidad total con YouTube y SpeechRecognition
        val defaultUa = s.userAgentString
        s.userAgentString = defaultUa.replace("; wv", "")

        wv.setLayerType(View.LAYER_TYPE_HARDWARE, null)

        wv.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(request: PermissionRequest) {
                // Conceder automáticamente micrófono y audio capture dentro de JARVIS
                runOnUiThread {
                    request.grant(request.resources)
                }
            }

            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress < 100) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = newProgress
                } else {
                    progressBar.visibility = View.GONE
                }
            }

            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.filePathCallback?.onReceiveValue(null)
                this@MainActivity.filePathCallback = filePathCallback

                val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                val photoFile: File? = try {
                    createImageFile()
                } catch (ex: IOException) {
                    null
                }

                if (photoFile != null) {
                    cameraPhotoPath = photoFile.absolutePath
                    val photoURI: Uri = FileProvider.getUriForFile(
                        this@MainActivity,
                        applicationContext.packageName + ".fileprovider",
                        photoFile
                    )
                    takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                }

                val contentSelectionIntent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }

                val intentArray: Array<Intent?> = if (photoFile != null) arrayOf(takePictureIntent) else arrayOfNulls(0)
                val chooserIntent = Intent(Intent.ACTION_CHOOSER).apply {
                    putExtra(Intent.EXTRA_INTENT, contentSelectionIntent)
                    putExtra(Intent.EXTRA_TITLE, "Adjuntar en JARVIS")
                    putExtra(Intent.EXTRA_INITIAL_INTENTS, intentArray)
                }

                fileChooserLauncher.launch(chooserIntent)
                return true
            }
        }

        wv.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                val currentServer = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
                val serverHost = try { Uri.parse(currentServer).host } catch (e: Exception) { null }
                val requestHost = request?.url?.host

                if (url.startsWith(currentServer) || 
                    (serverHost != null && requestHost != null && requestHost.equals(serverHost, ignoreCase = true)) ||
                    url.contains("trycloudflare.com") || 
                    url.contains("onrender.com") || 
                    url.contains("railway.app") || 
                    url.contains("koyeb.app") || 
                    url.contains("youtube.com") || 
                    url.contains("lrclib.net")) {
                    return false
                }

                // Enlaces externos abrir en navegador del sistema
                try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    startActivity(intent)
                    return true
                } catch (e: Exception) {
                    return false
                }
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                errorLayout.visibility = View.GONE
                webView.visibility = View.VISIBLE
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                if (request?.isForMainFrame == true) {
                    webView.visibility = View.GONE
                    errorLayout.visibility = View.VISIBLE
                }
            }
        }
    }

    private fun loadSavedServerUrl() {
        val url = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        webView.loadUrl(url)
    }

    private fun showServerUrlDialog() {
        val currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        val input = EditText(this).apply {
            setText(currentUrl)
            setHint("https://xxxx.trycloudflare.com o http://192.168.1.x:5001")
            setPadding(dpToPx(16), dpToPx(12), dpToPx(16), dpToPx(12))
            setTextColor(Color.WHITE)
            setHintTextColor(Color.GRAY)
            setBackgroundColor(Color.parseColor("#152233"))
        }

        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dpToPx(24), dpToPx(16), dpToPx(24), dpToPx(16))
            setBackgroundColor(Color.parseColor("#0C1522"))
            addView(TextView(this@MainActivity).apply {
                text = "Ingresa la dirección de JARVIS (enlace Cloudflare HTTPS o IP local Wi-Fi):"
                setTextColor(Color.LTGRAY)
                textSize = 13f
                setPadding(0, 0, 0, dpToPx(12))
            })
            addView(input)
        }

        AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Configurar Servidor JARVIS")
            .setView(container)
            .setPositiveButton("Conectar") { _, _ ->
                val newUrl = input.text.toString().trim()
                if (newUrl.isNotEmpty()) {
                    var formatted = newUrl
                    if (!formatted.startsWith("http://") && !formatted.startsWith("https://")) {
                        formatted = "https://$formatted"
                    }
                    prefs.edit().putString(KEY_SERVER_URL, formatted).apply()
                    errorLayout.visibility = View.GONE
                    webView.visibility = View.VISIBLE
                    webView.loadUrl(formatted)
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun createErrorLayout(): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#080D14"))
            visibility = View.GONE
            setPadding(dpToPx(32), dpToPx(32), dpToPx(32), dpToPx(32))

            // Ícono de reactor
            addView(TextView(this@MainActivity).apply {
                text = "⚡"
                textSize = 52f
                gravity = Gravity.CENTER
            })

            // Título
            addView(TextView(this@MainActivity).apply {
                text = "JARVIS DESCONECTADO"
                textSize = 20f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(Color.parseColor("#00F2FE"))
                gravity = Gravity.CENTER
                setPadding(0, dpToPx(16), 0, dpToPx(8))
            })

            // Mensaje
            addView(TextView(this@MainActivity).apply {
                text = "No se pudo conectar con el servidor de JARVIS.\nAsegúrate de que 'Iniciar_Jarvis_Celular.bat' esté corriendo en tu computadora."
                textSize = 14f
                setTextColor(Color.parseColor("#88A6C2"))
                gravity = Gravity.CENTER
                setPadding(0, 0, 0, dpToPx(24))
            })

            // Botón Reintentar
            addView(Button(this@MainActivity).apply {
                text = "Reintentar Conexión"
                setTextColor(Color.WHITE)
                background = createCyanButtonDrawable()
                setOnClickListener {
                    errorLayout.visibility = View.GONE
                    webView.visibility = View.VISIBLE
                    loadSavedServerUrl()
                }
            })

            // Botón Cambiar URL
            addView(Button(this@MainActivity).apply {
                text = "Cambiar URL del Servidor"
                setTextColor(Color.parseColor("#00F2FE"))
                background = createGlassButtonDrawable()
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply {
                    setMargins(0, dpToPx(12), 0, 0)
                }
                setOnClickListener { showServerUrlDialog() }
            })
        }
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile("JARVIS_${timeStamp}_", ".jpg", storageDir)
    }

    private fun createGlassButtonDrawable(): GradientDrawable {
        return GradientDrawable().apply {
            setColor(Color.parseColor("#44102030"))
            setStroke(dpToPx(1), Color.parseColor("#5500F2FE"))
            cornerRadius = dpToPx(21).toFloat()
        }
    }

    private fun createCyanButtonDrawable(): GradientDrawable {
        return GradientDrawable().apply {
            setColor(Color.parseColor("#0088FF"))
            cornerRadius = dpToPx(12).toFloat()
        }
    }

    private fun createProgressBarDrawable(): GradientDrawable {
        return GradientDrawable().apply {
            setColor(Color.parseColor("#00F2FE"))
        }
    }

    private fun dpToPx(dp: Int): Int {
        return TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            dp.toFloat(),
            resources.displayMetrics
        ).toInt()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    // --- INTEGRACIÓN DE REPRODUCCIÓN EN SEGUNDO PLANO Y AUDÍFONOS ---

    override fun onNativePlay() {
        runOnUiThread {
            webView.evaluateJavascript("window.togglePlayPauseFromNative && window.togglePlayPauseFromNative(true);", null)
        }
    }

    override fun onNativePause() {
        runOnUiThread {
            webView.evaluateJavascript("window.togglePlayPauseFromNative && window.togglePlayPauseFromNative(false);", null)
        }
    }

    override fun onNativeNext() {
        runOnUiThread {
            webView.evaluateJavascript("window.skipNextFromNative && window.skipNextFromNative();", null)
        }
    }

    override fun onNativePrev() {
        runOnUiThread {
            webView.evaluateJavascript("window.skipPrevFromNative && window.skipPrevFromNative();", null)
        }
    }

    fun updateMediaPlayback(isPlaying: Boolean, title: String, artist: String) {
        isMusicPlaying = isPlaying
        val serviceIntent = Intent(this, JarvisMediaService::class.java).apply {
            action = if (isPlaying) JarvisMediaService.ACTION_PLAY else JarvisMediaService.ACTION_PAUSE
            putExtra(JarvisMediaService.EXTRA_TITLE, title)
            putExtra(JarvisMediaService.EXTRA_ARTIST, artist)
            putExtra(JarvisMediaService.EXTRA_IS_PLAYING, isPlaying)
        }
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    override fun onPause() {
        super.onPause()
        if (!isMusicPlaying) {
            webView.onPause()
        } else {
            // Mantiene los timers de JavaScript y audio activos para reproducción ininterrumpida con pantalla apagada
            webView.resumeTimers()
        }
    }

    override fun onStop() {
        super.onStop()
        if (isMusicPlaying) {
            webView.resumeTimers()
        }
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
        webView.resumeTimers()
    }

    override fun onDestroy() {
        JarvisMediaService.playbackListener = null
        if (!isMusicPlaying) {
            try {
                stopService(Intent(this, JarvisMediaService::class.java))
            } catch (e: Exception) {}
        }
        super.onDestroy()
    }

    class JarvisJsBridge(private val activity: MainActivity) {
        @JavascriptInterface
        fun onMusicStateChanged(isPlaying: Boolean, title: String?, artist: String?) {
            activity.runOnUiThread {
                activity.updateMediaPlayback(isPlaying, title ?: "Música", artist ?: "JARVIS AI")
            }
        }
    }
}
