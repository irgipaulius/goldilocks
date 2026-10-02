#!/usr/bin/env python3
"""0.125° Spain climate grid for 2016–2025.

Temperature and precipitation come from TerraClimate (~4 km monthly fields),
averaged onto cells of 0.125° (about 14 km), four times finer than the
previous 0.5° latitude spacing. Cloud amount stays the 1° CERES field from
the earlier NASA POWER grid, copied onto the nearest fine cell.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from fetch_power import load_provinces, province_at  # noqa: E402

TC = Path("/tmp/tc")
YEARS = range(2016, 2026)
DLAT = 0.125
DLON = 0.125
# TerraClimate cell edges sit on multiples of 1/24°, so groups of three
# pixels land on multiples of 0.125°.
LAT_MIN, LAT_MAX = 27.2, 44.1
LON_MIN, LON_MAX = -18.8, 4.8


def open_slice(path: Path, name: str):
    import netCDF4 as nc

    ds = nc.Dataset(path)
    lat = np.asarray(ds.variables["lat"][:], dtype=np.float64)
    lon = np.asarray(ds.variables["lon"][:], dtype=np.float64)
    # Latitude runs north to south.
    i0 = int(np.argmin(np.abs(lat - LAT_MAX)))
    i1 = int(np.argmin(np.abs(lat - LAT_MIN)))
    j0 = int(np.argmin(np.abs(lon - LON_MIN)))
    j1 = int(np.argmin(np.abs(lon - LON_MAX)))
    if i0 > i1:
        i0, i1 = i1, i0
    raw = ds.variables[name][:, i0 : i1 + 1, j0 : j1 + 1]
    data = np.ma.filled(np.ma.array(raw, dtype=np.float32), np.nan)
    lat_s = lat[i0 : i1 + 1]
    lon_s = lon[j0 : j1 + 1]
    ds.close()
    return data, lat_s, lon_s


def accumulate(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    total = None
    count = None
    lat_s = lon_s = None
    for year in YEARS:
        path = TC / f"TerraClimate_{name}_{year}.nc"
        data, lat_s, lon_s = open_slice(path, name)
        valid = np.isfinite(data)
        if total is None:
            total = np.zeros(data.shape, dtype=np.float64)
            count = np.zeros(data.shape, dtype=np.int16)
        data = np.where(valid, data, 0.0)
        total += data
        count += valid.astype(np.int16)
        print(f"  {name} {year}", flush=True)
    return total, count, lat_s, lon_s


def bin_means(total, count, lat_s, lon_s):
    """Average native ~4 km pixels into 0.125° cells. Lat runs north to south."""
    lat_key = np.floor(lat_s / DLAT).astype(np.int32)
    lon_key = np.floor(lon_s / DLON).astype(np.int32)
    mean = np.divide(total, count, out=np.full(total.shape, np.nan), where=count > 0)
    keys = {}
    for i, ilat in enumerate(lat_key):
        for j, ilon in enumerate(lon_key):
            keys.setdefault((int(ilat), int(ilon)), []).append((i, j))
    out = {}
    for key, pixels in keys.items():
        ii = np.array([p[0] for p in pixels])
        jj = np.array([p[1] for p in pixels])
        block = mean[:, ii[:, None], jj[None, :]]
        # block shape is wrong if I broadcast that way. Do it month by month.
        acc = np.zeros(12, dtype=np.float64)
        n = np.zeros(12, dtype=np.int32)
        for i, j in pixels:
            col = mean[:, i, j]
            ok = np.isfinite(col)
            acc[ok] += col[ok]
            n[ok] += 1
        if n.min() == 0:
            continue
        center_lat = (key[0] + 0.5) * DLAT
        center_lon = (key[1] + 0.5) * DLON
        out[key] = (center_lat, center_lon, acc / n)
    return out


def touches_spain(lat: float, lon: float, prepped) -> str | None:
    center = province_at(lon, lat, prepped)
    if center:
        return center
    step = DLAT * 0.42
    for dy in (-step, step):
        for dx in (-step, step):
            name = province_at(lon + dx, lat + dy, prepped)
            if name:
                return name
    return None


def nearest_cloud(lat: float, lon: float, clouds: list[tuple]) -> list[float]:
    best = None
    best_d = 1e9
    for clat, clon, series in clouds:
        d = (lat - clat) ** 2 + (lon - clon) ** 2
        if d < best_d:
            best_d = d
            best = series
    return best


def main() -> None:
    missing = [
        name
        for name in ("ppt", "tmax", "tmin")
        for year in YEARS
        if not (TC / f"TerraClimate_{name}_{year}.nc").exists()
    ]
    if missing:
        raise SystemExit(f"missing TerraClimate files: {', '.join(missing)}")
    old = json.loads((ROOT / "climate.json").read_text())
    clouds = [(p["lat"], p["lon"], p["cloud_pct"]) for p in old["points"]]
    print("reading precipitation", flush=True)
    ppt_sum, ppt_n, lat_s, lon_s = accumulate("ppt")
    print("reading tmax", flush=True)
    tmax_sum, tmax_n, _, _ = accumulate("tmax")
    print("reading tmin", flush=True)
    tmin_sum, tmin_n, _, _ = accumulate("tmin")
    print("binning", lat_s.shape, lon_s.shape, flush=True)
    ppt = bin_means(ppt_sum, ppt_n, lat_s, lon_s)
    tmax = bin_means(tmax_sum, tmax_n, lat_s, lon_s)
    tmin = bin_means(tmin_sum, tmin_n, lat_s, lon_s)
    prepped = load_provinces()
    points = []
    for key, (lat, lon, rain) in ppt.items():
        if key not in tmax or key not in tmin:
            continue
        province = touches_spain(lat, lon, prepped)
        if not province:
            continue
        temp = (tmax[key][2] + tmin[key][2]) / 2
        cloud = nearest_cloud(lat, lon, clouds)
        points.append(
            {
                "lat": round(float(lat), 4),
                "lon": round(float(lon), 4),
                "province": province,
                "center_on_land": province_at(lon, lat, prepped) is not None,
                "temp_c": [round(float(v), 2) for v in temp],
                "cloud_pct": [round(float(v), 2) for v in cloud],
                "precip_mm": [round(float(v), 2) for v in rain],
            }
        )
    points.sort(key=lambda p: (p["lat"], p["lon"]))
    payload = {
        "source": "TerraClimate monthly tmax, tmin, and ppt for temperature and precipitation. Cloud amount is CERES SYN1Deg from the NASA POWER grid.",
        "resolution": "Temperature and precipitation: TerraClimate ~4 km, averaged to 0.125° (about 14 km). Cloud amount: 1°, assigned from the nearest previous cell.",
        "dlat": DLAT,
        "dlon": DLON,
        "start": "2016-01",
        "end": "2025-12",
        "months": old["months"],
        "notes": [
            "Each number is the mean of that calendar month across 2016–2025.",
            "Temperature is the mean of TerraClimate monthly maximum and minimum, in °C.",
            "Precipitation is the mean monthly total in millimetres.",
            "Cloud amount is the 1° CERES SYN1Deg mean, copied from the nearest cell of the previous grid.",
            "A cell is kept when its footprint touches Spanish land. center_on_land is false when the cell center is offshore.",
        ],
        "points": points,
    }
    (ROOT / "climate.json").write_text(json.dumps(payload, separators=(",", ":")))
    land = sum(1 for p in points if p["center_on_land"])
    print(f"wrote {len(points)} cells, {land} with center on land")
    winter = []
    for p in points:
        if p["lat"] < 32:
            continue
        t = (p["temp_c"][11] + p["temp_c"][0] + p["temp_c"][1]) / 3
        c = (p["cloud_pct"][11] + p["cloud_pct"][0] + p["cloud_pct"][1]) / 3
        r = p["precip_mm"][11] + p["precip_mm"][0] + p["precip_mm"][1]
        winter.append((t, c, r, p))
    winter.sort(key=lambda row: (-row[0], row[1], row[2]))
    print("warmest mainland winter cells:")
    for t, c, r, p in winter[:8]:
        print(f"  {p['province']:24} {p['lat']:.3f},{p['lon']:.3f} land={p['center_on_land']} {t:.1f}C {c:.0f}% {r:.0f}mm")


if __name__ == "__main__":
    main()
