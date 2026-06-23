package com.xtr4ng3.locktrail

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider

class MainActivity : AppCompatActivity() {
    private lateinit var status: TextView

    private val permissionRequest = 4001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(resources.getIdentifier("activity_main", "layout", packageName))

        status = findViewById(resources.getIdentifier("status", "id", packageName))

        findViewById<Button>(resources.getIdentifier("btnPermissions", "id", packageName)).setOnClickListener {
            requestPermissions()
        }

        findViewById<Button>(resources.getIdentifier("btnStart", "id", packageName)).setOnClickListener {
            if (!hasLocationPermission()) {
                requestPermissions()
            } else {
                ContextCompat.startForegroundService(this, Intent(this, TrailService::class.java))
                updateStatus("Registro visible activado.")
            }
        }

        findViewById<Button>(resources.getIdentifier("btnStop", "id", packageName)).setOnClickListener {
            val i = Intent(this, TrailService::class.java)
            i.putExtra("stop", true)
            startService(i)
            updateStatus("Registro detenido.")
        }

        findViewById<Button>(resources.getIdentifier("btnExport", "id", packageName)).setOnClickListener {
            val uri = TrailStorage.exportLatestToDownloads(this)
            if (uri != null) {
                updateStatus("Exportado a Downloads/LockTrail.\n$uri")
            } else {
                updateStatus("No hay registros para exportar.")
            }
        }

        findViewById<Button>(resources.getIdentifier("btnShare", "id", packageName)).setOnClickListener {
            shareLatest()
        }

        updateStatus("LOCKTRAIL listo.\n${TrailStorage.latestSummary(this)}")
    }

    private fun hasLocationPermission(): Boolean {
        val fine = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        val coarse = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
        return fine || coarse
    }

    private fun requestPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )

        if (android.os.Build.VERSION.SDK_INT >= 33) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        ActivityCompat.requestPermissions(this, permissions.toTypedArray(), permissionRequest)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == permissionRequest) {
            if (hasLocationPermission()) {
                updateStatus("Permisos concedidos.\n${TrailStorage.latestSummary(this)}")
            } else {
                updateStatus("Permisos de ubicación no concedidos.")
                Toast.makeText(this, "LOCKTRAIL necesita ubicación para registrar trayectos.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun shareLatest() {
        val file = TrailStorage.latestFile(this)
        if (file == null) {
            updateStatus("No hay registros para compartir.")
            return
        }

        val uri = FileProvider.getUriForFile(this, "$packageName.files", file)

        val text = """
            LOCKTRAIL owner recovery report

            Archivo: ${file.name}
            ${TrailStorage.latestSummary(this)}

            Uso legítimo: dispositivo propio / reporte a autoridades.
        """.trimIndent()

        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/csv"
            putExtra(Intent.EXTRA_SUBJECT, "LOCKTRAIL recovery report")
            putExtra(Intent.EXTRA_TEXT, text)
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        startActivity(Intent.createChooser(intent, "Compartir reporte LOCKTRAIL"))
    }

    private fun updateStatus(msg: String) {
        status.text = "Estado:\n$msg\n\nPrivacidad: registro visible, exportación local, uso propio."
    }
}
