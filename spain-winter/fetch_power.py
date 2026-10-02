#!/usr/bin/env python3
"""Monthly climate grid for Spain, 2016–2025, from NASA POWER (MERRA-2).

Open-Meteo's ERA5 archive hit its hourly quota while a 0.25° download was
in progress, so this uses NASA POWER's native 0.5° × 0.625° monthly fields:
temperature, cloud amount, and bias-corrected precipitation.
"""

from __future__ import annotations

import calendar
import csv
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEOJSON = ROOT / "spain-provinces.geojson"
RAW = ROOT / "power_raw"
OUT = ROOT / "climate.json"

START_YEAR = 2016
END_YEAR = 2025
PARAMS = ("T2M", "CLOUD_AMT", "PRECTOTCORR")

# Each box stays under the regional API limit of 4.5° × 4.5°.
TILES = [
    (35.9, 40.2, -9.8, -5.4),
    (35.9, 40.2, -5.6, -1.2),
    (35.9, 40.2, -1.4, 3.0),
    (35.9, 40.2, 2.5, 4.7),
    (40.0, 44.1, -9.8, -5.4),
    (40.0, 44.1, -5.6, -1.2),
    (40.0, 44.1, -1.4, 3.0),
    (40.0, 44.1, 2.5, 4.7),
    (27.4, 29.7, -18.5, -15.6),
    (27.4, 29.7, -15.8, -13.1),
]


def pip_ring(x: float, y: float, ring: list) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def pip_geom(x: float, y: float, geom: dict) -> bool:
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        if not pip_ring(x, y, poly[0]):
            continue
        if any(pip_ring(x, y, hole) for hole in poly[1:]):
            continue
        return True
    return False


def load_provinces() -> list[tuple]:
    data = json.loads(GEOJSON.read_text())
    prepped = []
    for feature in data["features"]:
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        pts = [pt for poly in polys for ring in poly for pt in ring]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        prepped.append((min(xs), max(xs), min(ys), max(ys), feature["properties"]["name"], geom))
    return prepped


def province_at(lon: float, lat: float, prepped: list[tuple]) -> str | None:
    for minx, maxx, miny, maxy, name, geom in prepped:
        if lon < minx or lon > maxx or lat < miny or lat > maxy:
            continue
        if pip_geom(lon, lat, geom):
            return name
    return None


def cell_province(lat: float, lon: float, prepped: list[tuple]) -> str | None:
    center = province_at(lon, lat, prepped)
    if center:
        return center
    # Keep a coastal cell when Spain occupies part of the MERRA-2 footprint.
    for dy in (-0.22, 0.0, 0.22):
        for dx in (-0.28, 0.0, 0.28):
            if dy == 0 and dx == 0:
                continue
            name = province_at(lon + dx, lat + dy, prepped)
            if name:
                return name
    return None


def fetch_tile(param: str, south: float, north: float, west: float, east: float) -> str:
    RAW.mkdir(exist_ok=True)
    path = RAW / f"{param}_{south}_{north}_{west}_{east}.csv"
    if path.exists() and path.stat().st_size > 200:
        return path.read_text()
    query = urllib.parse.urlencode(
        {
            "latitude-min": south,
            "latitude-max": north,
            "longitude-min": west,
            "longitude-max": east,
            "parameters": param,
            "community": "AG",
            "start": START_YEAR,
            "end": END_YEAR,
            "format": "CSV",
        }
    )
    url = "https://power.larc.nasa.gov/api/temporal/monthly/regional?" + query
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "spain-winter-climate-map/1.0 (personal research)"},
    )
    delay = 2.0
    last = "no response"
    for _ in range(5):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                text = response.read().decode()
            if "-END HEADER-" not in text or "PARAMETER" not in text:
                raise RuntimeError(text[:300])
            path.write_text(text)
            return text
        except Exception as exc:  # noqa: BLE001 — retry transient API failures
            last = str(exc)
            time.sleep(delay)
            delay = min(delay * 2, 30)
    raise RuntimeError(f"{param} {south,north,west,east} failed: {last}")


def parse_rows(text: str) -> list[dict]:
    body = text.split("-END HEADER-", 1)[1].strip()
    reader = csv.DictReader(io.StringIO(body))
    rows = []
    for row in reader:
        if not row.get("PARAMETER") or row["PARAMETER"] not in PARAMS:
            continue
        rows.append(row)
    return rows


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def accumulate(text: str, param: str, store: dict) -> None:
    for row in parse_rows(text):
        lat = round(float(row["LAT"]), 3)
        lon = round(float(row["LON"]), 3)
        year = int(row["YEAR"])
        series = store.setdefault((lat, lon), [dict() for _ in range(12)])
        for mi, name in enumerate(MONTHS):
            value = float(row[name])
            if value < -100:
                continue
            if param == "PRECTOTCORR":
                value *= calendar.monthrange(year, mi + 1)[1]
            series[mi][year] = value


def nearest(origin: tuple[float, float], keys: list[tuple[float, float]]) -> tuple[float, float] | None:
    lat, lon = origin
    best = None
    best_d = 1.6 ** 2
    for key in keys:
        dist = (lat - key[0]) ** 2 + (lon - key[1]) ** 2
        if dist < best_d:
            best_d = dist
            best = key
    return best


def mean_months(series: list[dict]) -> list[float] | None:
    out = []
    for month in series:
        if len(month) < 8:
            return None
        out.append(round(sum(month.values()) / len(month), 2))
    return out


def main() -> None:
    prepped = load_provinces()
    temp: dict[tuple[float, float], list] = {}
    cloud: dict[tuple[float, float], list] = {}
    rain: dict[tuple[float, float], list] = {}
    stores = {"T2M": temp, "CLOUD_AMT": cloud, "PRECTOTCORR": rain}
    for south, north, west, east in TILES:
        for param in PARAMS:
            print(f"fetch {param} {south},{west} → {north},{east}", flush=True)
            text = fetch_tile(param, south, north, west, east)
            accumulate(text, param, stores[param])
            time.sleep(0.15)

    cloud_keys = list(cloud)
    points = []
    for lat, lon in sorted(temp):
        if (lat, lon) not in rain:
            continue
        province = cell_province(lat, lon, prepped)
        if not province:
            continue
        center_on_land = province_at(lon, lat, prepped) is not None
        cloud_key = nearest((lat, lon), cloud_keys)
        if cloud_key is None:
            print(f"skip no cloud {lat},{lon}")
            continue
        temp_m = mean_months(temp[(lat, lon)])
        rain_m = mean_months(rain[(lat, lon)])
        cloud_m = mean_months(cloud[cloud_key])
        if not temp_m or not rain_m or not cloud_m:
            print(f"skip incomplete {lat},{lon}")
            continue
        points.append(
            {
                "lat": lat,
                "lon": lon,
                "province": province,
                "center_on_land": center_on_land,
                "temp_c": temp_m,
                "cloud_pct": cloud_m,
                "precip_mm": rain_m,
            }
        )

    payload = {
        "source": "NASA POWER monthly API. Temperature and precipitation are MERRA-2; cloud amount is CERES SYN1Deg.",
        "resolution": "Temperature and precipitation: 0.5° × 0.625° (about 55 × 50 km). Cloud amount: 1° × 1°, assigned to the nearest temperature cell.",
        "start": f"{START_YEAR}-01",
        "end": f"{END_YEAR}-12",
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "notes": [
            "Each number is the mean of that calendar month across 2016–2025.",
            "Precipitation is the mean monthly total in millimetres.",
            "Cloud amount is the mean cloud fraction in percent, from the 1° SYN1Deg product, copied onto the nearest temperature cell.",
            "A cell is kept when its footprint touches Spanish land. center_on_land is false when the cell center is offshore and the value mixes coast and sea.",
        ],
        "points": points,
    }
    OUT.write_text(json.dumps(payload))
    print(f"wrote {OUT} cells={len(points)} bytes={OUT.stat().st_size}")
    sanity(points)


def winter(row: dict, key: str, how: str) -> float:
    vals = [row[key][11], row[key][0], row[key][1]]
    return sum(vals) if how == "sum" else sum(vals) / 3


def sanity(rows: list[dict]) -> None:
    canary = {"Las Palmas", "Santa Cruz De Tenerife"}

    def show(title: str, subset: list[dict]) -> None:
        temps = [winter(r, "temp_c", "mean") for r in subset]
        clouds = [winter(r, "cloud_pct", "mean") for r in subset]
        rains = [winter(r, "precip_mm", "sum") for r in subset]
        if len(subset) < 2:
            print(f"\n{title}: {len(subset)} cells")
            return
        t0, t1 = min(temps), max(temps)
        c0, c1 = min(clouds), max(clouds)
        r0, r1 = min(rains), max(rains)
        scored = []
        for r, t, c, p in zip(subset, temps, clouds, rains):
            score = (
                (0 if t1 == t0 else (t - t0) / (t1 - t0))
                + (0 if c1 == c0 else (c1 - c) / (c1 - c0))
                + (0 if r1 == r0 else (r1 - p) / (r1 - r0))
            ) / 3
            scored.append((score, t, c, p, r))
        scored.sort(reverse=True)
        print(f"\n{title}")
        for score, t, c, p, r in scored[:15]:
            print(
                f"  {score:.3f}  {t:5.1f}°C  cloud {c:5.1f}%  rain {p:6.1f} mm  "
                f"{r['province']:24} {r['lat']:.3f},{r['lon']:.3f}"
            )

    show("Peninsula + Balearics", [r for r in rows if r["province"] not in canary])
    show("Canaries", [r for r in rows if r["province"] in canary])


if __name__ == "__main__":
    main()
