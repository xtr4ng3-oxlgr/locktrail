#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOCKTRAIL Studio

Desktop companion for importing owner-controlled location logs and building
local map reports.

Created by xtr4ng3.
"""

from __future__ import annotations

import csv
import datetime as dt
import html
import json
import math
import os
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP = "LOCKTRAIL Studio"
AUTHOR = "xtr4ng3"
BASE = Path.cwd()
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)

points = []


def parse_float(value):
    try:
        return float(value)
    except Exception:
        return None


def import_csv_folder(folder: Path):
    imported = []
    for file in folder.rglob("*.csv"):
        with file.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = parse_float(row.get("latitude", ""))
                lon = parse_float(row.get("longitude", ""))
                if lat is None or lon is None:
                    continue
                imported.append({
                    "timestamp": row.get("timestamp_iso", ""),
                    "lat": lat,
                    "lon": lon,
                    "accuracy": row.get("accuracy_m", ""),
                    "provider": row.get("provider", ""),
                    "source": str(file),
                })
    return imported


def import_google_takeout_json(file: Path):
    imported = []
    data = json.loads(file.read_text(encoding="utf-8", errors="ignore"))

    records = []
    if isinstance(data, dict):
        records = data.get("locations") or data.get("records") or []
    elif isinstance(data, list):
        records = data

    for item in records:
        lat = None
        lon = None
        ts = item.get("timestamp") or item.get("timestampMs") or item.get("serverTimestamp")

        if "latitudeE7" in item and "longitudeE7" in item:
            lat = item.get("latitudeE7") / 10_000_000
            lon = item.get("longitudeE7") / 10_000_000
        elif "latitude" in item and "longitude" in item:
            lat = parse_float(item.get("latitude"))
            lon = parse_float(item.get("longitude"))

        if lat is None or lon is None:
            continue

        if ts and str(ts).isdigit():
            try:
                ts = dt.datetime.fromtimestamp(int(ts) / 1000).isoformat(timespec="seconds")
            except Exception:
                ts = str(ts)

        imported.append({
            "timestamp": str(ts or ""),
            "lat": lat,
            "lon": lon,
            "accuracy": str(item.get("accuracy", "")),
            "provider": "google-takeout",
            "source": str(file),
        })

    return imported


def haversine(a, b):
    r = 6371.0
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lon"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    x = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def total_distance_km(items):
    total = 0.0
    for a, b in zip(items, items[1:]):
        total += haversine(a, b)
    return total


def generate_map(items):
    if not items:
        raise ValueError("No hay puntos cargados.")

    items = sorted(items, key=lambda x: x.get("timestamp", ""))
    center = items[len(items) // 2]
    coords = [[p["lat"], p["lon"]] for p in items]
    markers = []

    for i, p in enumerate(items):
        if i == 0:
            label = "INICIO"
        elif i == len(items) - 1:
            label = "FIN"
        else:
            label = f"Punto {i+1}"

        markers.append({
            "lat": p["lat"],
            "lon": p["lon"],
            "label": label,
            "timestamp": p.get("timestamp", ""),
            "accuracy": p.get("accuracy", ""),
            "provider": p.get("provider", ""),
        })

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REPORTS / f"locktrail_route_{stamp}.html"
    distance = total_distance_km(items)

    doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>LOCKTRAIL Route Report</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
body{{margin:0;background:#05070b;color:#e8f6ff;font-family:Consolas,Segoe UI,Arial}}
header{{padding:22px 28px;background:#090d14;border-bottom:1px solid #263246}}
h1{{color:#7ef9ff;margin:0;font-size:34px;letter-spacing:3px}}
.sub{{color:#ff304f;margin-top:4px}}
#map{{height:72vh}}
.panel{{padding:18px 28px;background:#0b1018;border-top:1px solid #263246}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}
td,th{{border-bottom:1px solid #1a2130;padding:8px;text-align:left}}
th{{color:#7ef9ff}}
code{{color:#d6f7ff}}
.small{{color:#9fb1c7}}
</style>
</head>
<body>
<header>
<h1>LOCKTRAIL</h1>
<div class="sub">Owner route evidence report · xtr4ng3</div>
</header>
<div id="map"></div>
<div class="panel">
<b>Puntos:</b> {len(items)} · <b>Distancia aproximada:</b> {distance:.2f} km · <b>Generado:</b> {html.escape(dt.datetime.now().isoformat(timespec="seconds"))}
<table>
<tr><th>Timestamp</th><th>Lat</th><th>Lon</th><th>Accuracy</th><th>Provider</th><th>Source</th></tr>
{''.join(f"<tr><td>{html.escape(str(p.get('timestamp','')))}</td><td>{p['lat']:.7f}</td><td>{p['lon']:.7f}</td><td>{html.escape(str(p.get('accuracy','')))}</td><td>{html.escape(str(p.get('provider','')))}</td><td><code>{html.escape(str(p.get('source','')))}</code></td></tr>" for p in items[:500])}
</table>
<p class="small">Reporte local. Usar solamente con datos propios o autorizados. Para recuperación por robo, entregar a autoridades.</p>
</div>
<script>
const coords = {json.dumps(coords)};
const markers = {json.dumps(markers, ensure_ascii=False)};
const map = L.map('map').setView([{center["lat"]}, {center["lon"]}], 13);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
const line = L.polyline(coords, {{color: '#ff304f', weight: 4}}).addTo(map);
map.fitBounds(line.getBounds(), {{padding: [30, 30]}});
markers.forEach((m, idx) => {{
    const color = idx === 0 ? 'green' : (idx === markers.length - 1 ? 'red' : 'cyan');
    L.circleMarker([m.lat, m.lon], {{
        radius: idx === 0 || idx === markers.length - 1 ? 8 : 5,
        color: color,
        fillColor: color,
        fillOpacity: 0.8
    }}).addTo(map).bindPopup(`<b>${{m.label}}</b><br>${{m.timestamp}}<br>Accuracy: ${{m.accuracy}}<br>Provider: ${{m.provider}}`);
}});
</script>
</body>
</html>"""
    out.write_text(doc, encoding="utf-8")
    return out


class Studio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LOCKTRAIL Studio // xtr4ng3")
        self.root.geometry("1050x720")
        self.root.configure(bg="#05070b")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background="#05070b", foreground="#e8f6ff", fieldbackground="#0b1018")
        style.configure("TButton", background="#121927", foreground="#e8f6ff", padding=8)
        style.configure("Accent.TButton", background="#5b0f1a", foreground="#ffffff", padding=8)
        style.configure("Treeview", background="#090d14", foreground="#e8f6ff", fieldbackground="#090d14", rowheight=26)
        style.configure("Treeview.Heading", background="#11192a", foreground="#7ef9ff")

        self.status = tk.StringVar(value="Sin datos cargados.")

        header = tk.Frame(self.root, bg="#05070b")
        header.pack(fill="x", padx=16, pady=12)
        tk.Label(header, text="LOCKTRAIL STUDIO", bg="#05070b", fg="#7ef9ff", font=("Consolas", 26, "bold")).pack(anchor="w")
        tk.Label(header, text="Route importer / map reports / owner evidence", bg="#05070b", fg="#ff304f", font=("Consolas", 10)).pack(anchor="w")

        bar = tk.Frame(self.root, bg="#05070b")
        bar.pack(fill="x", padx=16, pady=6)

        ttk.Button(bar, text="Importar carpeta CSV", style="Accent.TButton", command=self.load_folder).pack(side="left", padx=4)
        ttk.Button(bar, text="Importar Google Takeout JSON", command=self.load_takeout).pack(side="left", padx=4)
        ttk.Button(bar, text="Generar mapa HTML", command=self.build_map).pack(side="left", padx=4)
        ttk.Button(bar, text="Abrir reportes", command=lambda: webbrowser.open(REPORTS.resolve().as_uri())).pack(side="left", padx=4)

        tk.Label(self.root, textvariable=self.status, bg="#05070b", fg="#e8f6ff", font=("Consolas", 10)).pack(anchor="w", padx=20, pady=4)

        self.tree = ttk.Treeview(self.root, columns=("ts", "lat", "lon", "acc", "provider", "source"), show="headings")
        for col, title, width in [
            ("ts", "Timestamp", 180),
            ("lat", "Lat", 110),
            ("lon", "Lon", 110),
            ("acc", "Accuracy", 90),
            ("provider", "Provider", 110),
            ("source", "Source", 420),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True, padx=16, pady=12)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for p in points[:2000]:
            self.tree.insert("", "end", values=(
                p.get("timestamp", ""),
                f"{p['lat']:.7f}",
                f"{p['lon']:.7f}",
                p.get("accuracy", ""),
                p.get("provider", ""),
                p.get("source", ""),
            ))
        dist = total_distance_km(sorted(points, key=lambda x: x.get("timestamp", ""))) if len(points) > 1 else 0
        self.status.set(f"Puntos cargados: {len(points)} · Distancia aproximada: {dist:.2f} km")

    def load_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta con CSV LOCKTRAIL")
        if not folder:
            return
        imported = import_csv_folder(Path(folder))
        points.extend(imported)
        self.refresh_table()

    def load_takeout(self):
        file = filedialog.askopenfilename(title="Seleccionar Records.json / JSON", filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if not file:
            return
        try:
            imported = import_google_takeout_json(Path(file))
            points.extend(imported)
            self.refresh_table()
        except Exception as exc:
            messagebox.showerror(APP, str(exc))

    def build_map(self):
        try:
            out = generate_map(points)
            self.status.set(f"Mapa generado: {out}")
            webbrowser.open(out.resolve().as_uri())
        except Exception as exc:
            messagebox.showerror(APP, str(exc))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Studio().run()
