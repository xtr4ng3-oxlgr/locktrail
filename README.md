# LOCKTRAIL

<img width="1080" height="920" alt="lt" src="https://github.com/user-attachments/assets/8152c75c-d602-4968-954f-ea47749819a1" />


## Advertencia legal y ética

El mal uso de esta herramienta puede violar leyes de privacidad, acoso, vigilancia y protección de datos.

El autor no avala ni promueve el uso de LOCKTRAIL contra dispositivos o personas sin permiso.  
Cualquier modificación orientada a rastreo oculto, exfiltración silenciosa o vigilancia no consentida va contra el propósito del proyecto.


**LOCKTRAIL** es una herramienta defensiva para propietarios de dispositivos Android.  
Permite registrar ubicaciones de forma visible, exportar el historial por USB y generar mapas locales desde una aplicación de escritorio.

Creado por **xtr4ng3**.

## Uso prohibido

No se permite usar LOCKTRAIL para:

- espiar personas,
- rastrear parejas, familiares, empleados o terceros sin consentimiento,
- instalar la app de forma oculta,
- eliminar avisos de permisos o notificaciones,
- modificar el código para ocultar rastreo,
- enviar ubicación sin intervención del usuario,
- evadir controles de privacidad de Android.

Si un fork, modificación o publicación deriva en uso abusivo, invasivo o ilegal, no está avalado por este proyecto.


---

## Propósito

LOCKTRAIL está pensado para un uso legítimo y propio:

- registrar trayectos del dispositivo personal,
- conservar evidencia local de recorridos,
- exportar registros cuando el teléfono vuelve a estar en manos del propietario,
- generar mapas y reportes desde una PC,
- entregar información ordenada a autoridades si hubo robo o extravío.

LOCKTRAIL no está diseñado para vigilar personas.  
LOCKTRAIL no debe instalarse en dispositivos ajenos.  
LOCKTRAIL no debe ocultarse.  
LOCKTRAIL no envía ubicación en silencio.

---

## Arquitectura

```text
Android Kotlin App
  -> foreground service visible
  -> location logs CSV
  -> export bundle to Downloads/LockTrail

Desktop Companion
  -> import CSV / Google Takeout JSON propio
  -> build route map
  -> generate HTML report
```

---

## Componentes

```text
android/    -> aplicación Android en Kotlin
desktop/    -> software de PC en Python/Tkinter
docs/       -> instalación, flujo USB, mapas y normas
examples/   -> CSV de ejemplo
```

---

## Flujo de uso

1. Instalar la app Android en el teléfono propio.
2. Abrir LOCKTRAIL.
3. Conceder permisos de ubicación.
4. Activar el registro visible.
5. Cuando el dispositivo vuelva a casa, exportar el CSV.
6. Conectar el teléfono a la PC.
7. Copiar la carpeta `Downloads/LockTrail`.
8. Abrir `desktop/locktrail_studio.py`.
9. Importar los registros.
10. Generar mapa y reporte HTML.

---

## Android

Funciones:

- UI simple.
- Registro de ubicación con servicio visible.
- Notificación permanente mientras registra.
- CSV local.
- Exportación a `Downloads/LockTrail`.
- Botón de compartir reporte por email mediante apps instaladas.

Permisos usados:

- ubicación precisa/aproximada,
- notificaciones,
- foreground service de tipo location.

---

## PC Companion

El software de escritorio permite:

- importar una carpeta con CSV,
- importar JSON de Google Takeout propio si el usuario lo tiene,
- ver puntos detectados,
- generar un HTML con mapa,
- trazar ruta,
- marcar inicio y fin,
- guardar reporte en `reports/`.

No requiere API key de Google.

---

## Comandos de escritorio

```bash
cd desktop
python locktrail_studio.py
```

---

## Importar Google Takeout

LOCKTRAIL Studio puede intentar leer archivos tipo:

```text
Records.json
```

si fueron exportados por el propio dueño de la cuenta.

El uso de datos de otra persona sin permiso no está permitido.

---

## Uso permitido

LOCKTRAIL puede usarse para:

- dispositivo propio,
- dispositivo familiar con consentimiento claro,
- documentación para denuncia,
- revisión personal de trayectos,
- recuperación con asistencia de autoridades.

---

## Estado del proyecto

Versión inicial profesional:

- Android Kotlin app base.
- Servicio visible de registro.
- Exportación CSV.
- Desktop Studio.
- Generador de mapa HTML.
- Documentación de seguridad.

---

# Licencia

<img width="384" height="384" alt="giphy (4)" src="https://github.com/user-attachments/assets/18d64b9e-fba8-493e-8462-f6722e0e64b7" />

**xtr4ng3**

MIT.

