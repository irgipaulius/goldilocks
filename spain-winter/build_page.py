#!/usr/bin/env python3
"""Embed climate.json into a standalone map page."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "climate.json").read_text())
payload = json.dumps(data, separators=(",", ":"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Goldilocks</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<style>
  :root {
    --paper: #f4f0e6;
    --panel: #f7f4ee;
    --ink: #1c1915;
    --muted: #5e584e;
    --line: #ddd4c4;
    --accent: #9a3412;
    --chip: #efeae0;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; }
  body {
    display: flex;
    color: var(--ink);
    background: var(--paper);
    font-family: "Avenir Next", "Segoe UI", sans-serif;
  }
  #panel {
    width: 400px;
    flex: none;
    overflow: auto;
    padding: 22px 20px 36px;
    background: var(--panel);
    border-right: 1px solid var(--line);
  }
  #map { flex: 1; min-height: 100%; background: #e7e1d6; }
  .kicker {
    margin: 0 0 6px;
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
  }
  h1 {
    margin: 0 0 10px;
    font-family: Palatino, "Iowan Old Style", Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1.05;
  }
  p { margin: 0 0 12px; }
  .lede, .note, .src { color: var(--muted); font-size: 13px; line-height: 1.45; }
  #answer {
    margin: 14px 0 16px;
    padding-top: 12px;
    border-top: 1px solid var(--line);
  }
  #answer h2 {
    margin: 0 0 4px;
    font-family: Palatino, Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    line-height: 1.15;
  }
  .stats { display: flex; gap: 14px; margin: 8px 0; }
  .stats div { min-width: 70px; }
  .stats b { display: block; font-size: 16px; font-variant-numeric: tabular-nums; }
  .stats span { color: var(--muted); font-size: 11px; letter-spacing: 0.04em; text-transform: uppercase; }
  .sev { font-size: 13px; line-height: 1.4; }
  h3 {
    margin: 18px 0 8px;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
  }
  .row { display: flex; flex-wrap: wrap; gap: 6px; }
  button, .check {
    font: inherit;
    color: var(--ink);
    background: var(--chip);
    border: 1px solid transparent;
    border-radius: 999px;
    padding: 5px 10px;
    cursor: pointer;
  }
  button.on { background: var(--ink); color: var(--paper); }
  button.preset { border-radius: 6px; }
  label.slider, .check {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    margin: 6px 0;
  }
  input[type="range"] { flex: 1; accent-color: var(--accent); }
  .place {
    display: grid;
    grid-template-columns: 22px 1fr auto;
    gap: 2px 8px;
    width: 100%;
    text-align: left;
    border-radius: 8px;
    padding: 8px;
    background: transparent;
    border: 1px solid transparent;
  }
  .place:hover { background: #efeae0; }
  .place .rank { color: var(--accent); font-variant-numeric: tabular-nums; }
  .place .name { font-weight: 600; }
  .place .meta, .place .nums { color: var(--muted); font-size: 12px; grid-column: 2 / span 2; }
  .place .nums { font-variant-numeric: tabular-nums; }
  #detail { margin-top: 8px; }
  .bars { display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; align-items: end; height: 64px; margin-top: 6px; }
  .bars i {
    display: block;
    background: var(--accent);
    min-height: 2px;
    border-radius: 2px 2px 0 0;
  }
  .mlabels { display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; color: var(--muted); font-size: 9px; }
  .leaflet-div-icon.rank-pin {
    background: #1c1915;
    color: #f4f0e6;
    border: 2px solid #f4f0e6;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font: 700 13px "Avenir Next", "Segoe UI", sans-serif;
  }
  .legend {
    position: absolute;
    z-index: 500;
    left: 12px;
    bottom: 12px;
    background: var(--panel);
    border: 1px solid var(--line);
    padding: 8px 10px;
    width: 210px;
    font-size: 12px;
  }
  .swatch { height: 10px; margin: 6px 0; }
  .legend .ends { display: flex; justify-content: space-between; color: var(--muted); }
  .src a { color: var(--accent); }
  @media (max-width: 800px) {
    body { flex-direction: column; }
    #panel { width: auto; max-height: 48vh; }
    #map { min-height: 52vh; }
  }
</style>
</head>
<body>
<aside id="panel">
  <p class="kicker">Goldilocks · Spain · 2016–2025</p>
  <h1>Where winter is warm, clear, and dry</h1>
  <p class="lede">December, January, and February, averaged over 2016–2025. Cells are about 14 km across. The five highest scores are numbered. Every cell at or above the 95th percentile is outlined.</p>
  <div id="answer"></div>
  <h3>Months</h3>
  <div class="row" id="presets"></div>
  <div class="row" id="months" style="margin-top:8px"></div>
  <h3>Color the map by</h3>
  <div class="row" id="layers"></div>
  <p class="note">Each factor is stretched from the worst cell to the best cell on this map, including coastal cells you have hidden. The sliders are shares of that mix. Hiding cells does not recolor the ones that stay.</p>
  <div id="weights"></div>
  <h3>Map</h3>
  <div class="row" id="views"></div>
  <label class="check"><input type="checkbox" id="offshore" checked> Include coastal cells whose center is just offshore</label>
  <h3>Top 5 tiles</h3>
  <p class="note" id="p95"></p>
  <div id="places"></div>
  <h3>Selected cell</h3>
  <div id="detail" class="note">Click a cell.</div>
  <p class="src">Temperature and precipitation: TerraClimate monthly means for 2016–2025, averaged onto a 0.125° grid (about 14 km), four times finer than the previous 0.5° grid. Cloud amount: CERES SYN1Deg at 1°, copied from the nearest cloud cell. A coastal cell can still mix shoreline and sea. Official station maps, not combined into one score: <a href="https://www.aemet.es/es/conocermas/recursos_en_linea/publicaciones_y_estudios/publicaciones/detalles/MapasclimaticosdeEspana">AEMET climate maps, 1991–2020</a>.</p>
</aside>
<div id="map"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script id="climate-data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("climate-data").textContent);
const MONTHS = DATA.months;
const CITIES = [
  ["Seville", 37.389, -5.984], ["Córdoba", 37.889, -4.779], ["Granada", 37.178, -3.598],
  ["Málaga", 36.721, -4.421], ["Marbella", 36.510, -4.885], ["Almería", 36.834, -2.463],
  ["Cabo de Gata", 36.728, -2.191], ["Motril", 36.745, -3.518], ["Almuñécar", 36.734, -3.691],
  ["Nerja", 36.745, -3.875], ["Cádiz", 36.527, -6.289], ["Jerez", 36.685, -6.126],
  ["Tarifa", 36.014, -5.603], ["Huelva", 37.262, -6.945], ["Murcia", 37.992, -1.131],
  ["Cartagena", 37.606, -0.986], ["Águilas", 37.411, -1.582], ["Alicante", 38.346, -0.491],
  ["Benidorm", 38.541, -0.123], ["Valencia", 39.470, -0.377], ["Castellón", 39.986, -0.037],
  ["Tarragona", 41.119, 1.245], ["Barcelona", 41.388, 2.169], ["Girona", 41.979, 2.821],
  ["Palma", 39.569, 2.650], ["Ibiza", 38.909, 1.433], ["Mahón", 39.889, 4.266],
  ["Madrid", 40.417, -3.704], ["Toledo", 39.858, -4.024], ["Badajoz", 38.879, -6.971],
  ["Zaragoza", 41.649, -0.889], ["Bilbao", 43.263, -2.935], ["San Sebastián", 43.318, -1.981],
  ["Santander", 43.462, -3.810], ["Oviedo", 43.362, -5.849], ["A Coruña", 43.362, -8.411],
  ["Vigo", 42.241, -8.721], ["León", 42.598, -5.567], ["Burgos", 42.344, -3.697],
  ["Valladolid", 41.652, -4.724], ["Logroño", 42.466, -2.445], ["Pamplona", 42.812, -1.645],
  ["Albacete", 38.994, -1.858], ["Ciudad Real", 38.986, -3.930], ["Jaén", 37.779, -3.785],
  ["Las Palmas", 28.124, -15.430], ["Maspalomas", 27.760, -15.586],
  ["Santa Cruz de Tenerife", 28.464, -16.252], ["Los Cristianos", 28.050, -16.716],
  ["Arrecife", 28.963, -13.548], ["Puerto del Rosario", 28.500, -13.863],
  ["Santa Cruz de La Palma", 28.684, -17.765], ["Valverde", 27.810, -17.915]
];

const state = {
  months: new Set([11, 0, 1]),
  layer: "score",
  weights: { temp: 1, cloud: 1, rain: 1 },
  view: "peninsula",
  offshore: true,
  selected: null,
  fit: true
};

const map = L.map("map", { zoomControl: true, attributionControl: true, preferCanvas: true });
L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", {
  attribution: "Tiles &copy; Esri",
  maxZoom: 14
}).addTo(map);
const layer = L.layerGroup().addTo(map);
const legend = L.control({ position: "bottomleft" });
legend.onAdd = function () {
  const div = L.DomUtil.create("div", "legend");
  div.id = "legend";
  return div;
};
legend.addTo(map);

function km(a, b) {
  const x = (a.lon - b.lon) * 111.32 * Math.cos(((a.lat + b.lat) / 2) * Math.PI / 180);
  const y = (a.lat - b.lat) * 110.57;
  return Math.hypot(x, y);
}
function nearestCity(p) {
  let best = null;
  let bestD = 1e9;
  for (const [name, lat, lon] of CITIES) {
    const d = km(p, { lat, lon });
    if (d < bestD) { bestD = d; best = name; }
  }
  return bestD <= 75 ? best : null;
}
function placeName(p) {
  const city = nearestCity(p);
  const base = city || p.province;
  if (!p.center_on_land) return base + " coast";
  return base;
}
function metrics(p) {
  const idx = [...state.months];
  let t = 0, c = 0, r = 0;
  for (const i of idx) {
    t += p.temp_c[i];
    c += p.cloud_pct[i];
    r += p.precip_mm[i];
  }
  const n = idx.length || 1;
  return { temp: t / n, cloud: c / n, rain: r };
}
function inView(p) {
  const canary = p.lat < 32;
  if (state.view === "peninsula" && canary) return false;
  if (state.view === "canaries" && !canary) return false;
  return true;
}
function onMap(p) {
  return inView(p) && (state.offshore || p.center_on_land);
}
function weightShares() {
  let wT = state.weights.temp, wC = state.weights.cloud, wR = state.weights.rain;
  if (wT + wC + wR === 0) { wT = wC = wR = 1; }
  const sum = wT + wC + wR;
  return { wT, wC, wR, sum };
}
function scoredSet(points) {
  const rows = points.map(p => ({ ...p, ...metrics(p) }));
  const t0 = Math.min(...rows.map(r => r.temp)), t1 = Math.max(...rows.map(r => r.temp));
  const c0 = Math.min(...rows.map(r => r.cloud)), c1 = Math.max(...rows.map(r => r.cloud));
  const r0 = Math.min(...rows.map(r => r.rain)), r1 = Math.max(...rows.map(r => r.rain));
  const span = (v, a, b) => b === a ? 0.5 : (v - a) / (b - a);
  const { wT, wC, wR, sum } = weightShares();
  for (const row of rows) {
    row.tScore = span(row.temp, t0, t1);
    row.cScore = 1 - span(row.cloud, c0, c1);
    row.rScore = 1 - span(row.rain, r0, r1);
    row.score = 100 * (wT * row.tScore + wC * row.cScore + wR * row.rScore) / sum;
  }
  rows.sort((a, b) => b.score - a.score);
  return rows;
}
function scored() {
  // Scale weighted scores against every cell in this view, including hidden coastal cells,
  // so turning those cells off does not recolor the ones that stay.
  const domain = scoredSet(DATA.points.filter(inView));
  return domain.filter(onMap);
}
function mix(a, b, t) {
  const p = x => parseInt(x, 16);
  const c1 = [p(a.slice(1, 3)), p(a.slice(3, 5)), p(a.slice(5, 7))];
  const c2 = [p(b.slice(1, 3)), p(b.slice(3, 5)), p(b.slice(5, 7))];
  const v = c1.map((n, i) => Math.round(n + (c2[i] - n) * t));
  return "#" + v.map(n => n.toString(16).padStart(2, "0")).join("");
}
function ramp(stops, t) {
  const x = Math.min(0.999, Math.max(0, t)) * (stops.length - 1);
  const i = Math.floor(x);
  return mix(stops[i], stops[i + 1], x - i);
}
const RAMPS = {
  score: ["#efe6d6", "#e4c2a4", "#c2410c", "#7c2d12"],
  temp: ["#d5e2ec", "#8aa8be", "#e0b07a", "#9a3412"],
  cloud: ["#f4ead4", "#c8c2b4", "#6d7c8a", "#1f2937"],
  rain: ["#f4ead4", "#9bb8c9", "#3d6f99", "#1e3a5f"]
};
function colorOf(row) {
  const t = state.layer === "score" ? row.score / 100
    : state.layer === "temp" ? row.tScore
    : state.layer === "cloud" ? 1 - row.cScore
    : 1 - row.rScore;
  return ramp(RAMPS[state.layer], t);
}
function fmt(row) {
  return {
    temp: row.temp.toFixed(1) + "°C",
    cloud: Math.round(row.cloud) + "% cloud",
    rain: Math.round(row.rain) + " mm"
  };
}

function renderAnswer(rows) {
  const best = rows[0];
  const mainland = scoredSet(DATA.points.filter(p => p.lat >= 32)).filter(p => state.offshore || p.center_on_land);
  const seville = mainland.slice().sort((a, b) => km(a, { lat: 37.389, lon: -5.984 }) - km(b, { lat: 37.389, lon: -5.984 }))[0];
  const rank = mainland.findIndex(r => r.lat === seville.lat && r.lon === seville.lon) + 1;
  const f = fmt(best);
  const s = fmt(seville);
  const coast = best.center_on_land ? "" : " This cell’s center is just offshore, so the number mixes the shoreline with the sea beside it.";
  const compare = state.view === "canaries"
    ? `On the mainland, Seville’s nearest cell scores ${Math.round(seville.score)} (${s.temp}, ${s.cloud}, ${s.rain}), rank ${rank} of ${mainland.length}.`
    : `Seville’s nearest cell scores ${Math.round(seville.score)} (${s.temp}, ${s.cloud}, ${s.rain}), rank ${rank} of ${rows.length} in this view.`;
  document.getElementById("answer").innerHTML =
    `<h2>${placeName(best)}</h2>
     <p class="note" style="margin:0 0 6px">${best.province}${best.center_on_land ? "" : " · coastal cell"} · ${best.lat.toFixed(2)}°N, ${Math.abs(best.lon).toFixed(2)}°${best.lon < 0 ? "W" : "E"}</p>
     <div class="stats">
       <div><b>${Math.round(best.score)}</b><span>score</span></div>
       <div><b>${f.temp}</b><span>temperature</span></div>
       <div><b>${Math.round(best.cloud)}%</b><span>cloud</span></div>
       <div><b>${Math.round(best.rain)} mm</b><span>rain</span></div>
     </div>
     <p class="sev">${compare}${coast}</p>`;
}

function percentile(values, p) {
  const s = values.slice().sort((a, b) => a - b);
  if (!s.length) return 0;
  const i = (s.length - 1) * p;
  const lo = Math.floor(i);
  const hi = Math.ceil(i);
  if (lo === hi) return s[lo];
  return s[lo] * (hi - i) + s[hi] * (i - lo);
}
function renderPlaces(rows) {
  const picks = rows.slice(0, 5);
  const p95 = percentile(rows.map(r => r.score), 0.95);
  const n95 = rows.filter(r => r.score >= p95 - 1e-9).length;
  document.getElementById("p95").textContent =
    `95th percentile score: ${p95.toFixed(1)}. ${n95} tiles on this map are at or above it, outlined in dark.`;
  document.getElementById("places").innerHTML = picks.map((p, i) => {
    const f = fmt(p);
    return `<button class="place" data-lat="${p.lat}" data-lon="${p.lon}">
      <span class="rank">${i + 1}</span><span class="name">${placeName(p)}</span><span></span>
      <span class="meta">${p.province}${p.center_on_land ? "" : " · coastal cell"} · ${p.lat.toFixed(1)}°N, ${Math.abs(p.lon).toFixed(1)}°${p.lon < 0 ? "W" : "E"}</span>
      <span class="nums">score ${Math.round(p.score)} · ${f.temp} · ${f.cloud} · ${f.rain}</span>
    </button>`;
  }).join("");
  document.querySelectorAll(".place").forEach(btn => {
    btn.onclick = () => {
      const lat = +btn.dataset.lat, lon = +btn.dataset.lon;
      state.selected = rows.find(r => r.lat === lat && r.lon === lon);
      map.setView([lat, lon], Math.max(map.getZoom(), 8));
      render();
    };
  });
}

function renderDetail() {
  const box = document.getElementById("detail");
  const p = state.selected;
  if (!p) { box.className = "note"; box.textContent = "Click a cell."; return; }
  box.className = "";
  const maxT = Math.max(...p.temp_c);
  const bars = p.temp_c.map((t, i) => {
    const h = Math.max(4, (t / maxT) * 64);
    const on = state.months.has(i) ? "" : "opacity:0.35";
    return `<i style="height:${h}px;${on}" title="${MONTHS[i]} ${t.toFixed(1)}°C"></i>`;
  }).join("");
  const labels = MONTHS.map(m => `<span>${m[0]}</span>`).join("");
  const f = fmt({ ...p, ...metrics(p) });
  const m = metrics(p);
  const parts = `Score ${Math.round(p.score)} out of 100 against the other cells on this map.`;
  box.innerHTML = `<strong>${placeName(p)}</strong>
    <p class="note" style="margin:4px 0 8px">${p.province}${p.center_on_land ? " · center on land" : " · center just offshore"}<br>
    For the months selected: ${m.temp.toFixed(1)}°C, ${Math.round(m.cloud)}% cloud, ${Math.round(m.rain)} mm rain.<br>${parts}</p>
    <div class="note">Mean temperature by month</div>
    <div class="bars">${bars}</div>
    <div class="mlabels">${labels}</div>`;
}

function renderLegend(rows) {
  const el = document.getElementById("legend");
  const titles = {
    score: ["Weaker match", "Warm, clear, dry"],
    temp: ["Colder", "Warmer"],
    cloud: ["Clearer", "Cloudier"],
    rain: ["Drier", "Wetter"]
  };
  let textLo = "", textHi = "";
  if (state.layer === "score") {
    textLo = "0"; textHi = "100";
  } else if (rows[0]) {
    const vals = DATA.points.filter(inView).map(p => metrics(p)[state.layer === "temp" ? "temp" : state.layer === "cloud" ? "cloud" : "rain"]);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    textLo = state.layer === "temp" ? lo.toFixed(1) + "°" : state.layer === "cloud" ? Math.round(lo) + "%" : Math.round(lo) + " mm";
    textHi = state.layer === "temp" ? hi.toFixed(1) + "°" : state.layer === "cloud" ? Math.round(hi) + "%" : Math.round(hi) + " mm";
  }
  const stops = RAMPS[state.layer].join(",");
  el.innerHTML = `<div>${titles[state.layer][0]} → ${titles[state.layer][1]}</div>
    <div class="swatch" style="background:linear-gradient(90deg,${stops})"></div>
    <div class="ends"><span>${textLo}</span><span>${textHi}</span></div>`;
}

function renderMap(rows) {
  layer.clearLayers();
  const dlat = (DATA.dlat || 0.5) / 2;
  const dlon = (DATA.dlon || 0.625) / 2;
  const p95 = percentile(rows.map(r => r.score), 0.95);
  const top = new Map(rows.slice(0, 5).map((row, i) => [row.lat + "," + row.lon, i + 1]));
  for (const row of rows) {
    const key = row.lat + "," + row.lon;
    const rank = top.get(key);
    const high = row.score >= p95 - 1e-9;
    const selected = state.selected && state.selected.lat === row.lat && state.selected.lon === row.lon;
    const rect = L.rectangle([[row.lat - dlat, row.lon - dlon], [row.lat + dlat, row.lon + dlon]], {
      color: rank ? "#1c1915" : high ? "#7c2d12" : selected ? "#1c1915" : "#f7f4ee",
      weight: rank ? 2.5 : high ? 1.6 : selected ? 2 : 0.4,
      fillColor: colorOf(row),
      fillOpacity: rank ? 0.9 : 0.78
    });
    const f = fmt(row);
    rect.bindTooltip(`<strong>${rank ? rank + " · " : ""}${placeName(row)}</strong><br>score ${Math.round(row.score)}<br>${f.temp} · ${f.cloud} · ${f.rain}`, { sticky: true });
    rect.on("click", () => { state.selected = row; render(); });
    rect.addTo(layer);
    if (rank) {
      L.marker([row.lat, row.lon], {
        interactive: false,
        keyboard: false,
        icon: L.divIcon({
          className: "rank-pin",
          html: String(rank),
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        })
      }).addTo(layer);
    }
  }
  if (state.fit) {
    const bounds = state.view === "canaries" ? [[27.3, -18.6], [29.6, -13.0]] : [[35.7, -9.9], [44.0, 4.6]];
    map.fitBounds(bounds, { padding: [16, 16] });
    state.fit = false;
  }
}

function render() {
  const rows = scored();
  if (state.selected) {
    state.selected = rows.find(r => r.lat === state.selected.lat && r.lon === state.selected.lon) || null;
  }
  renderAnswer(rows);
  renderPlaces(rows);
  renderDetail();
  renderLegend(rows);
  renderMap(rows);
}

function chip(label, on, click) {
  const b = document.createElement("button");
  b.textContent = label;
  b.className = on ? "on" : "";
  b.onclick = click;
  return b;
}
function buildControls() {
  const presets = [["Winter", [11, 0, 1]], ["Spring", [2, 3, 4]], ["Summer", [5, 6, 7]], ["Autumn", [8, 9, 10]], ["Full year", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]];
  const presetBox = document.getElementById("presets");
  const monthBox = document.getElementById("months");
  function paint() {
    presetBox.innerHTML = "";
    monthBox.innerHTML = "";
    for (const [label, idx] of presets) {
      const same = idx.length === state.months.size && idx.every(i => state.months.has(i));
      const b = chip(label, same, () => { state.months = new Set(idx); buildControls(); render(); });
      b.classList.add("preset");
      if (same) b.classList.add("on");
      presetBox.appendChild(b);
    }
    MONTHS.forEach((name, i) => {
      monthBox.appendChild(chip(name, state.months.has(i), () => {
        if (state.months.has(i)) { if (state.months.size > 1) state.months.delete(i); }
        else state.months.add(i);
        buildControls();
        render();
      }));
    });
    const layers = document.getElementById("layers");
    layers.innerHTML = "";
    for (const [id, label] of [["score", "Combined"], ["temp", "Temperature"], ["cloud", "Cloud"], ["rain", "Rain"]]) {
      layers.appendChild(chip(label, state.layer === id, () => { state.layer = id; buildControls(); render(); }));
    }
    const weights = document.getElementById("weights");
    weights.innerHTML = `<h3>Weights</h3>`;
    const { sum } = weightShares();
    for (const [key, label] of [["temp", "Warmth"], ["cloud", "Clear sky"], ["rain", "Dryness"]]) {
      const lab = document.createElement("label");
      lab.className = "slider";
      const share = Math.round(100 * state.weights[key] / sum);
      lab.innerHTML = `<span style="width:78px">${label}</span><input type="range" min="0" max="10" step="1" value="${state.weights[key]}"><span class="wval">${share}%</span>`;
      lab.querySelector("input").oninput = (e) => {
        state.weights[key] = +e.target.value;
        const next = weightShares();
        weights.querySelectorAll(".wval").forEach((el, i) => {
          const keys = ["temp", "cloud", "rain"];
          el.textContent = Math.round(100 * state.weights[keys[i]] / next.sum) + "%";
        });
        render();
      };
      weights.appendChild(lab);
    }
    const views = document.getElementById("views");
    views.innerHTML = "";
    for (const [id, label] of [["peninsula", "Mainland and Balearics"], ["canaries", "Canary Islands"]]) {
      views.appendChild(chip(label, state.view === id, () => {
        state.view = id;
        state.fit = true;
        state.selected = null;
        buildControls();
        render();
      }));
    }
  }
  paint();
}
document.getElementById("offshore").onchange = (e) => { state.offshore = e.target.checked; render(); };
buildControls();
render();
</script>
</body>
</html>
"""

html = html.replace("__DATA__", payload)
(ROOT / "index.html").write_text(html)
print(f"wrote index.html { (ROOT / 'index.html').stat().st_size } bytes")
