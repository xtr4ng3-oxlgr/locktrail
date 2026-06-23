# LOCKTRAIL Studio

Companion de escritorio para importar registros propios de LOCKTRAIL y generar mapas.

## Ejecutar

```bash
python locktrail_studio.py
```

## Entradas compatibles

- CSV exportado por LOCKTRAIL Android.
- JSON de Google Takeout propio, cuando esté disponible.

## Salida

```text
reports/
└─ locktrail_route_<timestamp>.html
```

El mapa usa OpenStreetMap mediante Leaflet.
