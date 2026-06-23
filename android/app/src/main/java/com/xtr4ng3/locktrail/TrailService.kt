package com.xtr4ng3.locktrail

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.IBinder
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat

class TrailService : Service(), LocationListener {
    private lateinit var locationManager: LocationManager

    override fun onCreate() {
        super.onCreate()
        locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager
        createChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val stop = intent?.getBooleanExtra("stop", false) == true
        if (stop) {
            stopTracking()
            return START_NOT_STICKY
        }

        startForeground(1001, NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("LOCKTRAIL activo")
            .setContentText("Registro visible de ubicación en curso")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setOngoing(true)
            .build())

        startTracking()
        return START_STICKY
    }

    private fun startTracking() {
        val fine = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        val coarse = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
        if (!fine && !coarse) {
            stopSelf()
            return
        }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                30_000L,
                25f,
                this
            )
        } catch (_: Exception) { }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.NETWORK_PROVIDER,
                60_000L,
                50f,
                this
            )
        } catch (_: Exception) { }
    }

    private fun stopTracking() {
        try {
            locationManager.removeUpdates(this)
        } catch (_: Exception) { }
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onLocationChanged(location: Location) {
        TrailStorage.appendLocation(this, location)
    }

    override fun onProviderEnabled(provider: String) {}
    override fun onProviderDisabled(provider: String) {}
    @Deprecated("Deprecated in Android framework")
    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createChannel() {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel = NotificationChannel(
            CHANNEL_ID,
            "LOCKTRAIL visible tracking",
            NotificationManager.IMPORTANCE_LOW
        )
        manager.createNotificationChannel(channel)
    }

    companion object {
        const val CHANNEL_ID = "locktrail_visible_tracking"
    }
}
