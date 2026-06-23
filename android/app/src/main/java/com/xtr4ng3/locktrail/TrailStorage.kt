package com.xtr4ng3.locktrail

import android.content.ContentValues
import android.content.Context
import android.location.Location
import android.net.Uri
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object TrailStorage {
    private const val HEADER = "timestamp_iso,latitude,longitude,accuracy_m,provider,speed_mps,bearing\n"

    fun logDir(context: Context): File {
        val dir = File(context.getExternalFilesDir(null), "locktrail_logs")
        if (!dir.exists()) dir.mkdirs()
        return dir
    }

    fun activeLogFile(context: Context): File {
        val day = SimpleDateFormat("yyyyMMdd", Locale.US).format(Date())
        return File(logDir(context), "locktrail_$day.csv")
    }

    fun appendLocation(context: Context, location: Location) {
        val file = activeLogFile(context)
        if (!file.exists()) {
            file.writeText(HEADER)
        }

        val ts = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.US).format(Date(location.time))
        val line = listOf(
            ts,
            location.latitude.toString(),
            location.longitude.toString(),
            location.accuracy.toString(),
            location.provider ?: "",
            if (location.hasSpeed()) location.speed.toString() else "",
            if (location.hasBearing()) location.bearing.toString() else ""
        ).joinToString(",") + "\n"

        file.appendText(line)
    }

    fun latestFile(context: Context): File? {
        return logDir(context)
            .listFiles { f -> f.isFile && f.name.endsWith(".csv") }
            ?.maxByOrNull { it.lastModified() }
    }

    fun latestSummary(context: Context): String {
        val file = latestFile(context) ?: return "Sin registros todavía."
        val lines = file.readLines()
        val points = (lines.size - 1).coerceAtLeast(0)
        return "Último archivo: ${file.name}\nPuntos registrados: $points\nRuta: ${file.absolutePath}"
    }

    fun exportLatestToDownloads(context: Context): Uri? {
        val file = latestFile(context) ?: return null

        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, file.name)
            put(MediaStore.Downloads.MIME_TYPE, "text/csv")
            put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/LockTrail")
        }

        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values) ?: return null
        resolver.openOutputStream(uri)?.use { out ->
            file.inputStream().use { input -> input.copyTo(out) }
        }
        return uri
    }
}
