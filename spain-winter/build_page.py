#!/usr/bin/env python3
"""Embed climate.json into the Goldilocks map page."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "climate.json").read_text())
areas = json.loads((ROOT / "areas.json").read_text())
payload = json.dumps(data, separators=(",", ":"))
area_payload = json.dumps(areas, separators=(",", ":"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Goldilocks</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='1' x2='1' y2='0'%3E%3Cstop offset='0' stop-color='%23e4b33c'/%3E%3Cstop offset='0.42' stop-color='%23e4b33c'/%3E%3Cstop offset='0.58' stop-color='%23c11212'/%3E%3Cstop offset='1' stop-color='%23c11212'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='16' cy='16' r='13' fill='url(%23g)' stroke='%23f7f3ea' stroke-width='2'/%3E%3C/svg%3E">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<style>
  :root {
    --paper: #f7f3ea;
    --panel: #fffcf7;
    --ink: #1c1914;
    --muted: #6d6558;
    --line: #e6dcc8;
    --hot: #c11212;
    --chip: #f3ecdf;
    --dock-h: 140px;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; }
  body {
    color: var(--ink);
    background: #e8e2d6;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    overflow: hidden;
  }
  button, input, select, summary { font: inherit; color: inherit; }
  button, summary { cursor: pointer; }
  #map { position: fixed; inset: 0; background: #e8e2d6; }
  #dock {
    position: fixed;
    z-index: 800;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: min(640px, calc(100vw - 24px));
    background: rgba(255, 252, 247, 0.96);
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 10px 28px rgba(28, 25, 20, 0.16);
    padding: 8px 10px 10px;
  }
  .dock-top {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 8px;
    align-items: center;
  }
  .mark { font-family: Palatino, Georgia, serif; font-size: 15px; letter-spacing: -0.03em; }
  .note, .src { color: var(--muted); font-size: 12px; line-height: 1.4; }
  .search-row { position: relative; min-width: 0; }
  #q {
    width: 100%;
    height: 32px;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0 10px;
    background: #fff;
    font-size: 16px;
  }
  #draw-area {
    height: 32px;
    border-radius: 8px;
    background: #fff;
    border: 1px solid var(--line);
    padding: 0 10px;
  }
  #hits {
    display: none;
    position: absolute;
    z-index: 5;
    top: 36px;
    left: 0;
    right: 0;
    max-height: 240px;
    overflow: auto;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 28px rgba(28, 25, 20, 0.18);
  }
  #hits.open { display: block; }
  #hits button {
    display: block;
    width: 100%;
    text-align: left;
    background: transparent;
    border: 0;
    border-bottom: 1px solid var(--line);
    border-radius: 0;
    padding: 10px 12px;
    min-height: 44px;
  }
  #hits button small { display: block; color: var(--muted); }
  .group {
    display: grid;
    grid-template-columns: 48px minmax(0, 1fr);
    gap: 8px;
    align-items: center;
    margin-top: 6px;
  }
  .group.score-group { align-items: start; }
  .group.score-group .glabel { line-height: 44px; }
  .score-block { min-width: 0; }
  .score-note {
    margin: 3px 0 0;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.25;
  }
  .glabel {
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
  }
  .seg, .tool-row { display: flex; min-width: 0; }
  .seg {
    background: var(--chip);
    border-radius: 8px;
    padding: 2px;
    gap: 2px;
  }
  .when-controls, .show-row { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
  .show-row { flex-direction: row; align-items: center; }
  #layers.seg { flex: 1; }
  #draw.seg { flex: none; min-width: max-content; }
  button.chip {
    flex: 1 1 auto;
    background: transparent;
    border: 0;
    border-radius: 6px;
    padding: 4px 6px;
    min-height: 26px;
    font-size: 12px;
    text-align: center;
  }
  #draw button.chip { flex: 0 0 auto; padding: 4px 10px; }
  #months button.chip { padding: 4px 0; font-size: 11px; letter-spacing: -0.02em; }
  button.chip.on, #draw-area.on { background: var(--ink); color: #fff; }
  #weights {
    position: relative;
    height: 44px;
    touch-action: none;
    user-select: none;
  }
  #weights .mix-track {
    position: relative;
    display: flex;
    height: 44px;
    border-radius: 10px;
    overflow: hidden;
    background: var(--chip);
  }
  #weights .part {
    min-width: 0;
    flex: 0 1 0px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1px;
    overflow: hidden;
    line-height: 1.05;
    padding: 0;
  }
  #weights .part .nm {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 10px;
    font-weight: 650;
  }
  #weights .part .pct { font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums; }
  #weights .part.tight .nm { display: none; }
  #weights .part.warm { background: #e4b33c; color: var(--ink); }
  #weights .part.sky { background: #24556f; color: #f7f3ea; }
  #weights .part.dry { background: #efe4cf; color: var(--ink); }
  #weights .grip {
    position: absolute;
    top: 0;
    width: 44px;
    height: 44px;
    padding: 0;
    border: 0;
    background: transparent;
    transform: translateX(-50%);
    cursor: ew-resize;
    touch-action: none;
    z-index: 2;
  }
  #weights .grip.dragging { z-index: 4; }
  #weights .knob {
    position: absolute;
    top: 50%;
    width: 16px;
    height: 26px;
    transform: translate(-50%, -50%);
    border-radius: 8px;
    background: #fff;
    border: 2px solid var(--ink);
    box-shadow: 0 1px 4px rgba(28, 25, 20, 0.28);
    pointer-events: none;
    z-index: 3;
  }
  #weights .mix-zeros {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 4;
  }
  #weights .zero-tag {
    position: absolute;
    top: 3px;
    font-size: 9px;
    line-height: 1.2;
    font-weight: 700;
    color: var(--ink);
    background: rgba(255, 252, 247, 0.96);
    border-radius: 4px;
    padding: 1px 4px;
    white-space: nowrap;
    pointer-events: none;
  }
  .check, summary.chip {
    background: transparent;
    border: 0;
    border-radius: 8px;
    padding: 4px 2px;
    min-height: 28px;
    font-size: 12px;
    color: var(--muted);
  }
  #active-filters { display: flex; flex-wrap: wrap; gap: 6px; }
  #active-filters:empty { display: none; }
  #active-filters button {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 4px 10px;
    min-height: 32px;
  }
  details { margin-top: 4px; }
  summary { list-style: none; display: inline-flex; align-items: center; }
  summary::-webkit-details-marker { display: none; }
  .fold { padding: 8px 2px 4px; }
  .check { display: flex; align-items: center; gap: 8px; margin: 8px 0; font-size: 13px; }
  select {
    height: 36px;
    border-radius: 8px;
    border: 1px solid var(--line);
    background: #fff;
    padding: 0 8px;
    max-width: 100%;
  }
  #card, #board {
    position: fixed;
    z-index: 820;
    background: var(--panel);
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(28, 25, 20, 0.22);
  }
  #card {
    display: none;
    top: calc(var(--dock-h) + 12px);
    right: 12px;
    width: min(360px, calc(100vw - 24px));
    max-height: calc(100dvh - var(--dock-h) - 250px);
    overflow: auto;
    padding: 12px 14px 14px;
  }
  body.card-open #board { max-height: 220px; }
  body.card-open #places { height: 130px; }
  body.card-open #card { display: block; }
  #card-close {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 36px;
    height: 36px;
    border: 0;
    border-radius: 50%;
    background: var(--chip);
  }
  #card h2 { margin: 0 28px 2px 0; font-family: Palatino, Georgia, serif; font-size: 22px; line-height: 1.15; }
  .stats { display: flex; flex-wrap: wrap; gap: 10px 14px; margin: 10px 0; }
  .stats > div { min-width: 64px; }
  .stats b { display: block; font-size: 18px; font-variant-numeric: tabular-nums; }
  .stats b.hot { color: var(--hot); }
  .stats span { color: var(--muted); font-size: 10px; letter-spacing: 0.05em; text-transform: uppercase; }
  .sunny-line { margin: 0 0 8px; font-size: 15px; line-height: 1.25; }
  .sunny-line b { font-size: 22px; font-variant-numeric: tabular-nums; }
  .sunny-line span { display: block; margin-top: 2px; color: var(--muted); font-size: 12px; letter-spacing: 0; text-transform: none; }
  table.months { width: 100%; border-collapse: collapse; font-size: 12px; font-variant-numeric: tabular-nums; }
  table.months th { text-align: right; color: var(--muted); font-weight: 600; font-size: 10px; letter-spacing: 0.04em; }
  table.months th:first-child, table.months td:first-child { text-align: left; }
  table.months td { padding: 3px 0; border-top: 1px solid var(--line); text-align: right; }
  table.months tr.on td { font-weight: 700; }
  #card-back { display: none; margin-top: 8px; background: var(--chip); border: 0; border-radius: 999px; padding: 8px 12px; min-height: 40px; }
  #board {
    z-index: 810;
    right: 12px;
    bottom: 12px;
    width: min(360px, calc(100vw - 24px));
    display: flex;
    flex-direction: column;
    max-height: min(460px, 52vh);
  }
  #board-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    text-align: left;
    background: transparent;
    border: 0;
    padding: 10px 12px;
    min-height: 48px;
  }
  #board-toggle strong { font-size: 14px; }
  #board-sub { color: var(--muted); font-size: 12px; line-height: 1.35; }
  .chev { width: 8px; height: 8px; border-right: 2px solid var(--ink); border-bottom: 2px solid var(--ink); transform: rotate(45deg); margin-left: auto; }
  #board.open .chev { transform: rotate(-135deg); }
  #board-body { display: none; min-height: 0; }
  #board.open #board-body { display: flex; flex-direction: column; min-height: 0; }
  .key { height: 8px; margin: 0 12px 8px; border-radius: 99px; }
  #places { overflow: auto; height: min(340px, 38vh); -webkit-overflow-scrolling: touch; }
  #places-inner { position: relative; }
  .place {
    position: absolute;
    left: 6px;
    right: 6px;
    height: 54px;
    display: grid;
    grid-template-columns: 32px 1fr;
    grid-template-rows: 1.2em 1.2em;
    column-gap: 6px;
    text-align: left;
    background: transparent;
    border: 0;
    border-radius: 10px;
    padding: 6px;
  }
  .place:hover, .place.hot { background: #f8efd6; }
  .place .rank { grid-row: 1 / span 2; align-self: center; font-weight: 700; color: var(--muted); font-variant-numeric: tabular-nums; }
  .place.top .rank { color: var(--hot); }
  .place .name { font-weight: 650; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .place .nums { color: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .legend {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 8px 10px;
    width: 190px;
    font-size: 12px;
    box-shadow: 0 6px 18px rgba(28, 25, 20, 0.12);
  }
  .swatch { height: 10px; margin: 6px 0; border-radius: 99px; }
  .legend .ends { display: flex; justify-content: space-between; color: var(--muted); }
  .src a { color: var(--hot); }
  body.selecting .leaflet-container { cursor: crosshair; touch-action: none; }
  .leaflet-marks-pane,
  .leaflet-marks-pane * { pointer-events: none !important; }
  @media (max-width: 720px) {
    #dock {
      top: 0;
      left: 0;
      right: 0;
      transform: none;
      width: auto;
      border-radius: 0 0 14px 14px;
      max-height: 46dvh;
      overflow: auto;
      padding: 6px 10px 8px;
      padding-top: max(6px, env(safe-area-inset-top));
    }
    .dock-top { grid-template-columns: minmax(0, 1fr) auto; }
    .mark { display: none; }
    #months { overflow-x: auto; }
    #months button.chip { flex: 0 0 auto; padding: 4px 7px; }
    #layers.seg { overflow-x: auto; }
    #board:not(.open) #board-sub { display: none; }
    #card {
      top: auto;
      right: 0;
      left: 0;
      bottom: 0;
      width: auto;
      max-height: min(68dvh, calc(100dvh - var(--dock-h) - 8px));
      border-radius: 16px 16px 0 0;
      padding-bottom: max(14px, env(safe-area-inset-bottom));
    }
    #card-back { display: inline-flex; }
    #board {
      left: 0;
      right: 0;
      bottom: 0;
      width: auto;
      border-radius: 16px 16px 0 0;
      max-height: 70dvh;
      padding-bottom: env(safe-area-inset-bottom);
    }
    #places { height: 48dvh; }
    .legend { display: none; }
    .leaflet-bottom { bottom: 64px !important; }
    body.board-open .leaflet-bottom { bottom: 46dvh !important; }
    body.card-open #board { visibility: hidden; }
    body.card-open .leaflet-bottom { bottom: 12px !important; }
  }
</style>
</head>
<body>
<header id="dock">
  <div class="dock-top">
    <div class="mark">Goldilocks</div>
    <div class="search-row">
      <input id="q" type="search" placeholder="Place or country" autocomplete="off" enterkeyhint="search">
      <div id="hits"></div>
    </div>
    <button id="draw-area" type="button">Draw</button>
  </div>
  <span id="brand-sub" hidden>World · 2016–2025</span>
  <div id="active-filters"></div>
  <div class="group">
    <span class="glabel">When</span>
    <div class="when-controls">
      <div class="seg" id="presets"></div>
      <div class="seg" id="months"></div>
    </div>
  </div>
  <div class="group score-group">
    <span class="glabel">Score</span>
    <div class="score-block">
      <div id="weights"></div>
      <p class="score-note" id="score-note">Numbers are monthly averages over 2016–2025. The bar is how much warmth, clear sky, and dryness count.</p>
    </div>
  </div>
  <div class="group">
    <span class="glabel">Show</span>
    <div class="show-row">
      <div class="seg" id="layers"></div>
      <div class="seg" id="draw"></div>
    </div>
  </div>
  <details>
    <summary class="chip">Place</summary>
    <div class="fold">
      <p class="note" id="scope-note">Cloud and sunny days are the 1° NASA grid for 2016–2025. The map is 2° until you search or draw a box, which loads 0.5° cells.</p>
      <p class="src">Temperature and rain: TerraClimate, 2016–2025. Cloud: NASA POWER CERES at 1°. A sunny day is cloud under 70%, so the day is not overcast. The map is 2°, and 0.5° inside a search or a drawn box.</p>
    </div>
  </details>
</header>
<aside id="card" aria-live="polite">
  <button id="card-close" type="button" aria-label="Close">×</button>
  <div id="card-body"></div>
  <button id="card-back" type="button">Rankings</button>
</aside>
<aside id="board">
  <button id="board-toggle" type="button">
    <span><strong id="board-title">Rankings</strong><br><span id="board-sub"></span></span>
    <i class="chev"></i>
  </button>
  <div id="board-body">
    <div class="key" id="key"></div>
    <div id="places"><div id="places-inner"></div></div>
  </div>
</aside>
<div id="map"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script id="climate-data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("climate-data").textContent);
const AREAS = __AREAS__;
const MONTHS = DATA.months;
const CITIES = [
  ["Seville", 37.389, -5.984], ["Córdoba", 37.889, -4.779], ["Granada", 37.178, -3.598],
  ["Málaga", 36.721, -4.421], ["Marbella", 36.510, -4.885], ["Almería", 36.834, -2.463],
  ["Cabo de Gata", 36.728, -2.191], ["Roquetas de Mar", 36.764, -2.615],
  ["Motril", 36.745, -3.518], ["Almuñécar", 36.734, -3.691], ["Nerja", 36.745, -3.875],
  ["Cádiz", 36.527, -6.289], ["Jerez", 36.685, -6.126], ["Tarifa", 36.014, -5.603],
  ["Algeciras", 36.140, -5.453], ["Huelva", 37.262, -6.945],
  ["Murcia", 37.992, -1.131], ["Cartagena", 37.606, -0.986], ["Águilas", 37.411, -1.582],
  ["Torrevieja", 37.978, -0.683], ["Guardamar", 38.090, -0.655], ["Elche", 38.266, -0.698],
  ["Santa Pola", 38.192, -0.556], ["Alicante", 38.346, -0.491], ["Benidorm", 38.541, -0.123],
  ["Valencia", 39.470, -0.377], ["Castellón", 39.986, -0.037], ["Tarragona", 41.119, 1.245],
  ["Barcelona", 41.388, 2.169], ["Girona", 41.979, 2.821], ["Palma", 39.569, 2.650],
  ["Ibiza", 38.909, 1.433], ["Mahón", 39.889, 4.266], ["Madrid", 40.417, -3.704],
  ["Toledo", 39.858, -4.024], ["Badajoz", 38.879, -6.971], ["Zaragoza", 41.649, -0.889],
  ["Bilbao", 43.263, -2.935], ["San Sebastián", 43.318, -1.981], ["Santander", 43.462, -3.810],
  ["Oviedo", 43.362, -5.849], ["A Coruña", 43.362, -8.411], ["Vigo", 42.241, -8.721],
  ["León", 42.598, -5.567], ["Burgos", 42.344, -3.697], ["Valladolid", 41.652, -4.724],
  ["Logroño", 42.466, -2.445], ["Pamplona", 42.812, -1.645], ["Albacete", 38.994, -1.858],
  ["Ciudad Real", 38.986, -3.930], ["Jaén", 37.779, -3.785], ["Las Palmas", 28.124, -15.430],
  ["Maspalomas", 27.760, -15.586], ["Santa Cruz de Tenerife", 28.464, -16.252],
  ["Los Cristianos", 28.050, -16.716], ["Arrecife", 28.963, -13.548],
  ["Puerto del Rosario", 28.500, -13.863], ["Santa Cruz de La Palma", 28.684, -17.765],
  ["Valverde", 27.810, -17.915]
];
const WORLD_CITIES = [
  ["Lisbon", 38.72, -9.14], ["Porto", 41.15, -8.61], ["Faro", 37.02, -7.93],
  ["Tangier", 35.76, -5.83], ["Marrakesh", 31.63, -8.01], ["Casablanca", 33.59, -7.62],
  ["Paris", 48.86, 2.35], ["Nice", 43.70, 7.27], ["Rome", 41.90, 12.50],
  ["Naples", 40.85, 14.27], ["Athens", 37.98, 23.73], ["Istanbul", 41.01, 28.98],
  ["Cairo", 30.04, 31.24], ["Tunis", 36.81, 10.18], ["Dubai", 25.20, 55.27],
  ["Riyadh", 24.71, 46.68], ["Jerusalem", 31.77, 35.21], ["Tokyo", 35.68, 139.65],
  ["Kyoto", 35.01, 135.77], ["Seoul", 37.57, 126.98], ["Beijing", 39.90, 116.41],
  ["Shanghai", 31.23, 121.47], ["Hong Kong", 22.32, 114.17], ["Bangkok", 13.76, 100.50],
  ["Singapore", 1.35, 103.82], ["Delhi", 28.61, 77.21], ["Mumbai", 19.08, 72.88],
  ["Sydney", -33.87, 151.21], ["Melbourne", -37.81, 144.96], ["Auckland", -36.85, 174.76],
  ["Cape Town", -33.93, 18.42], ["Johannesburg", -26.20, 28.05], ["Nairobi", -1.29, 36.82],
  ["Lagos", 6.52, 3.38], ["London", 51.51, -0.13], ["Dublin", 53.35, -6.26],
  ["Amsterdam", 52.37, 4.90], ["Berlin", 52.52, 13.41], ["Vienna", 48.21, 16.37],
  ["Prague", 50.08, 14.44], ["Warsaw", 52.23, 21.01], ["Stockholm", 59.33, 18.07],
  ["Oslo", 59.91, 10.75], ["Helsinki", 60.17, 24.94], ["Reykjavík", 64.15, -21.94],
  ["New York", 40.71, -74.01], ["Los Angeles", 34.05, -118.24], ["Miami", 25.76, -80.19],
  ["Mexico City", 19.43, -99.13], ["São Paulo", -23.55, -46.63], ["Buenos Aires", -34.60, -58.38],
  ["Santiago", -33.45, -70.67], ["Lima", -12.05, -77.04], ["Bogotá", 4.71, -74.07]
];
const ALIAS = {
  "united states": "united states of america",
  "usa": "united states of america",
  "us": "united states of america",
  "uk": "united kingdom",
  "britain": "united kingdom",
  "great britain": "united kingdom",
  "czechia": "czechia",
  "czech republic": "czechia"
};
const HEAT = ["#10243a", "#1b4468", "#3e6d8c", "#7f8c91", "#c4b49a", "#e4b33c", "#f07a16", "#e23b2b", "#c11212"];
const ITEM_H = 58;

const state = {
  months: new Set([11, 0, 1]),
  layer: "score",
  weights: { temp: 33, cloud: 33, rain: 34 },
  draw: "tiles",
  country: "",
  area: null,
  bbox: null,
  selecting: false,
  selected: null,
  cardOpen: false,
  boardOpen: window.matchMedia("(min-width: 721px)").matches,
  fit: true,
  rows: [],
  listSig: "",
  loading: ""
};

let overviewPts = null;
let job = 0;
let rendering = false;
let viewportSyncTimer = 0;
let viewportSyncQueued = false;
let hoverRow = null;
let areaRect = null;
let rubber = null;
let anchor = null;
let drawing = false;
const tileCache = new Map();

const map = L.map("map", { zoomControl: false, attributionControl: true, preferCanvas: true, minZoom: 2 });
L.control.zoom({ position: "bottomleft" }).addTo(map);
L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", {
  attribution: "Tiles &copy; Esri",
  maxZoom: 14
}).addTo(map);
map.createPane("cells");
map.getPane("cells").style.zIndex = 410;
map.createPane("marks");
map.getPane("marks").style.zIndex = 450;
map.getPane("marks").style.pointerEvents = "none";
const layer = L.layerGroup().addTo(map);
const markLayer = L.layerGroup().addTo(map);
const hoverLayer = L.layerGroup().addTo(map);
map.setView([8, 0], 2);

function heatBlur() {
  const z = map.getZoom() || 6;
  const d = state.drawStep || DATA.dlat || 0.125;
  const cellPx = d * 256 * Math.pow(2, z) / 360;
  const px = Math.min(28, Math.max(4, cellPx * 1.35));
  return "blur(" + px.toFixed(1) + "px)";
}
function syncCellPane() {
  const pane = map.getPane("cells");
  // Uniform veil, so city names and relief show through even where cells overlap.
  pane.style.opacity = "0.48";
  pane.style.filter = state.draw === "heat" ? heatBlur() : "";
}
function viewportTilesMissing(box) {
  return tilesForBounds(box).some(id => !tileCache.has(id));
}
function scheduleViewportSync() {
  if (!map || state.bbox || state.selecting || drawing) return;
  if (map.getZoom() < 5) return;
  clearTimeout(viewportSyncTimer);
  viewportSyncTimer = setTimeout(flushViewportSync, 50);
}
async function flushViewportSync() {
  if (!map || state.bbox || state.selecting || drawing) return;
  if (map.getZoom() < 5) return;
  if (rendering) {
    viewportSyncQueued = true;
    return;
  }
  viewportSyncQueued = false;
  const box = mapViewportBox(0.12);
  const missing = viewportTilesMissing(box);
  const track = job;
  if (missing) await ensureTiles(box);
  if (track !== job || state.bbox) return;
  if (!state.area && map.getZoom() >= 5) render();
}
map.on("zoomend", () => { syncCellPane(); scheduleViewportSync(); });

const legend = L.control({ position: "bottomleft" });
legend.onAdd = function () {
  const div = L.DomUtil.create("div", "legend");
  div.id = "legend";
  L.DomEvent.disableClickPropagation(div);
  return div;
};
legend.addTo(map);

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function km(a, b) {
  const x = (a.lon - b.lon) * 111.32 * Math.cos(((a.lat + b.lat) / 2) * Math.PI / 180);
  const y = (a.lat - b.lat) * 110.57;
  return Math.hypot(x, y);
}
function inside(p, box) {
  return p.lat >= box[0] && p.lat <= box[2] && p.lon >= box[1] && p.lon <= box[3];
}
// A 0.5° land cell can sit in the sea beside an island. If no polygon contains
// the center, it still belongs to the nearest country within one cell.
const NEAR_COUNTRY = 0.5;
function prepareArea(area) {
  if (!area.geometry || area.parts) return area;
  try {
    const g = area.geometry;
    const polys = g.type === "Polygon" ? [g.coordinates] : (g.type === "MultiPolygon" ? g.coordinates : null);
    if (!polys) throw new Error("geometry");
    area.parts = polys.map(rings => {
      let s = 90, w = 180, n = -90, e = -180;
      for (const ring of rings) {
        for (const pt of ring) {
          const x = pt[0], y = pt[1];
          if (y < s) s = y;
          if (y > n) n = y;
          if (x < w) w = x;
          if (x > e) e = x;
        }
      }
      return [s, w, n, e];
    });
  } catch (err) {
    // A bad ring must not stop the map from starting. Fall back to the box.
    area.geometry = null;
    area.parts = area.bbox ? [area.bbox] : [];
  }
  return area;
}
AREAS.forEach(prepareArea);
function boxArea(bbox) {
  return {
    kind: "box",
    name: "",
    bbox: [Math.min(bbox[0], bbox[2]), Math.min(bbox[1], bbox[3]), Math.max(bbox[0], bbox[2]), Math.max(bbox[1], bbox[3])],
    geometry: null
  };
}
function hitsParts(area, lat, lon, pad) {
  for (const b of area.parts || []) {
    if (lat < b[0] - pad || lat > b[2] + pad || lon < b[1] - pad || lon > b[3] + pad) continue;
    return true;
  }
  return false;
}
function pointInRing(x, y, ring) {
  let insideRing = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1];
    const xj = ring[j][0], yj = ring[j][1];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) insideRing = !insideRing;
  }
  return insideRing;
}
function pointInRings(x, y, rings) {
  let insidePoly = false;
  for (const ring of rings) {
    if (pointInRing(x, y, ring)) insidePoly = !insidePoly;
  }
  return insidePoly;
}
function ringArea(ring) {
  let a = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    a += ring[j][0] * ring[i][1] - ring[i][0] * ring[j][1];
  }
  return Math.abs(a) * 0.5;
}
function coverSize(area, lon, lat) {
  if (!area || !area.geometry) return null;
  const polys = area.geometry.type === "Polygon" ? [area.geometry.coordinates] : area.geometry.coordinates;
  let best = null;
  for (const rings of polys) {
    if (!pointInRings(lon, lat, rings)) continue;
    const sz = ringArea(rings[0]);
    if (best == null || sz < best) best = sz;
  }
  return best;
}
function distToArea(area, lon, lat) {
  let best = Infinity;
  const polys = area.geometry.type === "Polygon" ? [area.geometry.coordinates] : area.geometry.coordinates;
  for (let i = 0; i < polys.length; i++) {
    const b = area.parts[i];
    const dx = lon < b[1] ? b[1] - lon : lon > b[3] ? lon - b[3] : 0;
    const dy = lat < b[0] ? b[0] - lat : lat > b[2] ? lat - b[2] : 0;
    if (dx * dx + dy * dy >= best * best) continue;
    for (const ring of polys[i]) {
      for (let k = 1; k < ring.length; k++) {
        const ax = ring[k - 1][0], ay = ring[k - 1][1];
        const bx = ring[k][0], by = ring[k][1];
        const ex = bx - ax, ey = by - ay;
        const l2 = ex * ex + ey * ey;
        let d;
        if (l2 === 0) d = Math.hypot(lon - ax, lat - ay);
        else {
          const t = Math.max(0, Math.min(1, ((lon - ax) * ex + (lat - ay) * ey) / l2));
          d = Math.hypot(lon - (ax + t * ex), lat - (ay + t * ey));
        }
        if (d < best) best = d;
      }
    }
  }
  return best;
}
function countryAt(lat, lon) {
  let best = null;
  let bestA = Infinity;
  for (const area of AREAS) {
    if (!hitsParts(area, lat, lon, 0)) continue;
    const sz = coverSize(area, lon, lat);
    if (sz != null && sz < bestA) { bestA = sz; best = area; }
  }
  if (best) return best;
  let near = null;
  let nearD = NEAR_COUNTRY;
  for (const area of AREAS) {
    if (!hitsParts(area, lat, lon, nearD)) continue;
    const d = distToArea(area, lon, lat);
    if (d < nearD) { nearD = d; near = area; }
  }
  return near;
}
function findCountry(name) {
  const raw = String(name || "").toLowerCase().trim();
  if (!raw) return null;
  const q = ALIAS[raw] || raw;
  return AREAS.find(c => c.name.toLowerCase() === q)
    || AREAS.find(c => c.name.toLowerCase().includes(q));
}
function cellInArea(p, area) {
  if (!area) return true;
  if (!area.geometry) return inside(p, area.bbox);
  const mine = coverSize(area, p.lon, p.lat);
  if (mine != null) {
    for (const other of AREAS) {
      if (other === area) continue;
      if (!hitsParts(other, p.lat, p.lon, 0)) continue;
      const sz = coverSize(other, p.lon, p.lat);
      if (sz != null && sz < mine) return false;
    }
    return true;
  }
  return countryAt(p.lat, p.lon) === area;
}
function viewBounds(area) {
  if (!area) return [[-56, -168], [72, 178]];
  if (!area.geometry) return [[area.bbox[0], area.bbox[1]], [area.bbox[2], area.bbox[3]]];
  let main = area.parts[0];
  let mainA = -1;
  for (const b of area.parts) {
    const span = b[3] - b[1];
    const size = span > 180 ? 0 : (b[2] - b[0]) * span;
    if (size > mainA) { mainA = size; main = b; }
  }
  let s = main[0], w = main[1], n = main[2], e = main[3];
  if (e - w > 180) return [[main[0], main[1]], [main[2], main[3]]];
  for (const b of area.parts) {
    if (b[3] - b[1] > 180) continue;
    if (b[2] < main[0] - 12 || b[0] > main[2] + 12 || b[3] < main[1] - 12 || b[1] > main[3] + 12) continue;
    s = Math.min(s, b[0]);
    w = Math.min(w, b[1]);
    n = Math.max(n, b[2]);
    e = Math.max(e, b[3]);
  }
  return [[s, w], [n, e]];
}
function nearestNamed(p, list, limit) {
  let best = null;
  let bestD = limit;
  for (const [name, lat, lon] of list) {
    const d = km(p, { lat, lon });
    if (d < bestD) { bestD = d; best = name; }
  }
  return best;
}
function placeName(p) {
  const city = nearestNamed(p, CITIES, 45) || nearestNamed(p, WORLD_CITIES, 140);
  if (city) return city;
  const country = p.province || "Land";
  const ns = (p.lat >= 0 ? p.lat.toFixed(1) + "°N" : Math.abs(p.lat).toFixed(1) + "°S");
  const ew = (p.lon >= 0 ? p.lon.toFixed(1) + "°E" : Math.abs(p.lon).toFixed(1) + "°W");
  return country + " · " + ns + ", " + ew;
}
function metrics(p) {
  const idx = [...state.months];
  let t = 0, c = 0, r = 0, nc = 0;
  for (const i of idx) {
    t += p.temp_c[i];
    r += p.precip_mm[i];
    if (p.cloud_pct) { c += p.cloud_pct[i]; nc++; }
  }
  const n = idx.length || 1;
  return { temp: t / n, cloud: nc ? c / n : null, rain: r };
}
function weightShares() {
  const wT = state.weights.temp;
  const wC = state.weights.cloud;
  const wR = state.weights.rain;
  const sum = wT + wC + wR;
  return { wT, wC, wR, sum: sum || 1 };
}
function scoredSet(points, scale) {
  const rows = points.map(p => ({ ...p, ...metrics(p) }));
  if (!rows.length) {
    rows.scale = scale || null;
    rows.hasCloud = false;
    return rows;
  }
  const cloudVals = rows.map(r => r.cloud).filter(v => v != null);
  const hasCloud = cloudVals.length > 0;
  let t0, t1, c0, c1, r0, r1;
  if (scale) ({ t0, t1, c0, c1, r0, r1 } = scale);
  else {
    t0 = Math.min(...rows.map(r => r.temp)); t1 = Math.max(...rows.map(r => r.temp));
    r0 = Math.min(...rows.map(r => r.rain)); r1 = Math.max(...rows.map(r => r.rain));
    c0 = hasCloud ? Math.min(...cloudVals) : 0;
    c1 = hasCloud ? Math.max(...cloudVals) : 1;
  }
  const span = (v, a, b) => b === a ? 0.5 : (v - a) / (b - a);
  const { wT, wC, wR, sum } = weightShares();
  for (const row of rows) {
    row.tScore = span(row.temp, t0, t1);
    row.rScore = 1 - span(row.rain, r0, r1);
    if (row.cloud == null) {
      row.cScore = null;
      let a = wT, b = wR;
      if (a + b === 0) { a = 1; b = 1; }
      row.score = 100 * (a * row.tScore + b * row.rScore) / (a + b);
    } else {
      row.cScore = 1 - span(row.cloud, c0, c1);
      row.score = 100 * (wT * row.tScore + wC * row.cScore + wR * row.rScore) / sum;
    }
  }
  rows.sort((a, b) => b.score - a.score);
  rows.scale = { t0, t1, c0, c1, r0, r1 };
  rows.hasCloud = hasCloud;
  return rows;
}
function tilesForBounds(box) {
  const ids = [];
  const s = Math.floor(box[0] / 10) * 10;
  const w = Math.floor(box[1] / 10) * 10;
  for (let lat = s; lat < box[2]; lat += 10) {
    for (let lon = w; lon < box[3]; lon += 10) ids.push(lat + "_" + lon);
  }
  return ids;
}
function tilesForArea(area) {
  if (!area) return [];
  if (!area.geometry) return tilesForBounds(area.bbox);
  const ids = new Set();
  const pad = 0.6;
  for (const b of area.parts) {
    if (b[3] - b[1] > 180) continue;
    for (const id of tilesForBounds([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad])) ids.add(id);
  }
  return [...ids];
}
function cellsInTiles(box) {
  const out = [];
  for (const id of tilesForBounds(box)) {
    const pts = tileCache.get(id);
    if (pts) out.push(...pts);
  }
  return out;
}
function cellsForArea(area) {
  const ids = area && area.geometry ? tilesForArea(area) : tilesForBounds(area.bbox);
  const out = [];
  for (const id of ids) {
    const pts = tileCache.get(id);
    if (pts) out.push(...pts);
  }
  return out;
}
let spainCloudBuckets = null;
function spainCloudIndex() {
  if (spainCloudBuckets) return spainCloudBuckets;
  const step = 0.125;
  const map = new Map();
  for (const p of DATA.points) {
    if (!p.cloud_pct) continue;
    const key = Math.floor(p.lat / step) + "," + Math.floor(p.lon / step);
    const bucket = map.get(key);
    if (bucket) bucket.push(p);
    else map.set(key, [p]);
  }
  spainCloudBuckets = { map, step };
  return spainCloudBuckets;
}
function nearestSpainCloud(lat, lon) {
  const { map, step } = spainCloudIndex();
  const i0 = Math.floor(lat / step);
  const j0 = Math.floor(lon / step);
  let best = null;
  let bestD = 0.04;
  for (let di = -2; di <= 2; di++) {
    for (let dj = -2; dj <= 2; dj++) {
      const bucket = map.get((i0 + di) + "," + (j0 + dj));
      if (!bucket) continue;
      for (const p of bucket) {
        const d2 = (p.lat - lat) ** 2 + (p.lon - lon) ** 2;
        if (d2 <= bestD) { bestD = d2; best = p; }
      }
    }
  }
  return best;
}
function unpack(data) {
  const d = data.d;
  return data.p.map(row => {
    const lat = row[0], lon = row[1];
    const country = countryAt(lat, lon);
    let cloud = row.length > 38 && row[26] >= 0 ? row.slice(26, 38) : null;
    if (!cloud) {
      const near = nearestSpainCloud(lat, lon);
      if (near) cloud = near.cloud_pct;
    }
    return {
      lat, lon,
      temp_c: row.slice(2, 14).map(v => v / 10),
      precip_mm: row.slice(14, 26),
      cloud_pct: cloud,
      sunny_days: row.length > 38 && row[38] >= 0 ? row[38] : null,
      dlat: d,
      dlon: d,
      center_on_land: true,
      province: country ? country.name : ""
    };
  });
}
function inDrawnBox(p) {
  return !state.bbox || inside(p, state.bbox);
}
function mapViewportBox(padFrac) {
  if (!map) return null;
  const b = padFrac ? map.getBounds().pad(padFrac) : map.getBounds();
  return [b.getSouth(), b.getWest(), b.getNorth(), b.getEast()];
}
function fineViewportCells() {
  if (!map || map.getZoom() < 5) return null;
  const box = mapViewportBox(0.08);
  const cells = cellsInTiles(box).filter(p => inside(p, box));
  return cells.length ? cells : null;
}
function worldPoints() {
  if (!overviewPts) return [];
  if (state.area && state.area.geometry) {
    const fine = cellsForArea(state.area).filter(p => cellInArea(p, state.area) && inDrawnBox(p));
    if (fine.length) return fine;
    return overviewPts.filter(p => cellInArea(p, state.area) && inDrawnBox(p));
  }
  if (state.bbox) {
    const fine = cellsInTiles(state.bbox).filter(p => inside(p, state.bbox));
    if (fine.length) return fine;
    return overviewPts.filter(p => inside(p, state.bbox));
  }
  const fine = fineViewportCells();
  if (fine) return fine;
  return overviewPts;
}
function listRows() {
  return scoredSet(worldPoints());
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
  return mix(stops[i], stops[Math.min(stops.length - 1, i + 1)], x - i);
}
function colorOf(row) {
  if (state.layer === "cloud" && row.cloud == null) return "#cfc8ba";
  const t = state.layer === "score" ? row.score / 100
    : state.layer === "temp" ? row.tScore
    : state.layer === "cloud" ? row.cScore
    : row.rScore;
  return ramp(HEAT, t);
}
function fmt(row) {
  return {
    temp: row.temp.toFixed(1) + "°C",
    cloud: row.cloud == null ? "" : Math.round(row.cloud) + "% cloud",
    rain: Math.round(row.rain) + " mm"
  };
}
function percentile(values, p) {
  const s = values.slice().sort((a, b) => a - b);
  if (!s.length) return 0;
  const i = (s.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  if (lo === hi) return s[lo];
  return s[lo] * (hi - i) + s[hi] * (i - lo);
}
function halfOf(row) {
  return {
    lat: (row.dlat || DATA.dlat || 0.125) / 2,
    lon: (row.dlon || DATA.dlon || 0.125) / 2
  };
}
function addOutline(row, style) {
  const h = halfOf(row);
  L.rectangle([[row.lat - h.lat, row.lon - h.lon], [row.lat + h.lat, row.lon + h.lon]], {
    pane: "marks", interactive: false, fill: false, ...style
  }).addTo(markLayer);
}
function highlight(row) {
  hoverRow = row;
  hoverLayer.clearLayers();
  document.querySelectorAll(".place.hot").forEach(el => el.classList.remove("hot"));
  if (!row) return;
  const h = halfOf(row);
  const bounds = [[row.lat - h.lat, row.lon - h.lon], [row.lat + h.lat, row.lon + h.lon]];
  L.rectangle(bounds, { pane: "marks", interactive: false, fill: false, color: "#ffffff", weight: 5 }).addTo(hoverLayer);
  L.rectangle(bounds, { pane: "marks", interactive: false, fill: false, color: "#c11212", weight: 2 }).addTo(hoverLayer);
  const btn = document.querySelector('.place[data-i="' + state.rows.indexOf(row) + '"]');
  if (btn) btn.classList.add("hot");
}
function syncChrome() {
  document.body.classList.toggle("card-open", state.cardOpen && !!state.selected);
  document.body.classList.toggle("board-open", state.boardOpen);
  document.body.classList.toggle("selecting", state.selecting);
  const board = document.getElementById("board");
  board.classList.toggle("open", state.boardOpen);
  document.getElementById("draw-area").classList.toggle("on", state.selecting);
  const dockH = document.getElementById("dock").offsetHeight;
  document.documentElement.style.setProperty("--dock-h", dockH + "px");
  document.getElementById("brand-sub").textContent = "World · 2016–2025 · temperature, cloud, and rain";
}
function renderFilters() {
  const box = document.getElementById("active-filters");
  const bits = [];
  if (state.country) bits.push('<button type="button" data-clear="country">' + esc(state.country) + " ×</button>");
  if (state.bbox) bits.push('<button type="button" data-clear="bbox">Drawn area ×</button>');
  box.innerHTML = bits.join("");
  box.querySelectorAll("button").forEach(btn => {
    btn.onclick = () => {
      if (btn.dataset.clear === "country") {
        document.getElementById("q").value = "";
        state.country = "";
        state.area = null;
      } else {
        state.bbox = null;
      }
      state.fit = true;
      state.selected = null;
      state.cardOpen = false;
      reloadScope();
    };
  });
}
function renderBoard(rows) {
  const p95 = percentile(rows.map(r => r.score), 0.95);
  const n95 = rows.filter(r => r.score >= p95 - 1e-9).length;
  const best = rows[0];
  document.getElementById("board-title").textContent = best
    ? "Best · " + placeName(best) + " · " + Math.round(best.score)
    : (state.loading || "Rankings");
  let sub = state.loading || (rows.length ? rows.length.toLocaleString() + " places" : "Nothing in this area");
  if (rows.length) sub += " · 95th percentile " + p95.toFixed(1) + " (" + n95 + " places)";
  document.getElementById("board-sub").textContent = sub;
  document.getElementById("key").style.background = "linear-gradient(90deg," + HEAT.join(",") + ")";
  const sig = [state.country || "", state.bbox && state.bbox.join(","), rows.length, best && best.lat, best && Math.round(best.score)].join("|");
  if (sig !== state.listSig) {
    state.listSig = sig;
    document.getElementById("places").scrollTop = 0;
  }
  state.rows = rows;
  paintPlacesNow();
}
function paintPlacesNow() {
  const scroller = document.getElementById("places");
  const inner = document.getElementById("places-inner");
  const rows = state.rows;
  inner.style.height = (rows.length * ITEM_H) + "px";
  if (!state.boardOpen) { inner.innerHTML = ""; return; }
  const viewH = scroller.clientHeight || 320;
  const start = Math.max(0, Math.floor(scroller.scrollTop / ITEM_H) - 8);
  const end = Math.min(rows.length, start + Math.ceil(viewH / ITEM_H) + 16);
  inner.innerHTML = rows.slice(start, end).map((p, offset) => {
    const i = start + offset;
    const f = fmt(p);
    const cloud = f.cloud ? " · " + f.cloud : "";
    return '<button type="button" class="place' + (i < 10 ? " top" : "") + '" data-i="' + i + '" style="top:' + (i * ITEM_H) + 'px">'
      + '<span class="rank">' + (i + 1) + '</span>'
      + '<span class="name">' + esc(placeName(p)) + '</span>'
      + '<span class="nums">score ' + Math.round(p.score) + " · " + f.temp + cloud + " · " + f.rain + "</span>"
      + "</button>";
  }).join("");
}
function renderDetail(rows) {
  const body = document.getElementById("card-body");
  const p = state.selected;
  if (!state.cardOpen || !p) { body.innerHTML = ""; return; }
  const rankIndex = rows.findIndex(r => r.lat === p.lat && r.lon === p.lon);
  const rankLine = rankIndex >= 0
    ? "Rank " + (rankIndex + 1) + " of " + rows.length.toLocaleString() + " in this view. "
    : "This is a finer cell than the ranked list. ";
  const f = fmt(p);
  const where = [p.province, p.center_on_land ? "" : "center just offshore"].filter(Boolean).join(" · ");
  const coord = p.lat.toFixed(2) + "°, " + p.lon.toFixed(2) + "°";
  const cloudStat = p.cloud == null ? "" : '<div><b>' + Math.round(p.cloud) + '%</b><span>cloud</span></div>';
  const sunny = p.sunny_days == null ? ""
    : '<p class="sunny-line"><b>' + Math.round(p.sunny_days) + '</b> sunny days / year<span>Cloud under 70%, so the day is not overcast. Averaged 2016–2025, about 100 km.</span></p>';
  const head = "<tr><th>Month</th><th>°C</th>" + (p.cloud_pct ? "<th>Cloud</th>" : "") + "<th>Rain</th></tr>";
  const table = p.temp_c.map((t, i) => {
    const on = state.months.has(i) ? ' class="on"' : "";
    const cloud = p.cloud_pct ? "<td>" + Math.round(p.cloud_pct[i]) + "%</td>" : "";
    return "<tr" + on + "><td>" + MONTHS[i] + "</td><td>" + t.toFixed(1) + "</td>" + cloud + "<td>" + Math.round(p.precip_mm[i]) + " mm</td></tr>";
  }).join("");
  body.innerHTML = "<h2>" + esc(placeName(p)) + "</h2>"
    + '<p class="note" style="margin:0">' + esc(where) + "<br>" + coord + "</p>"
    + '<div class="stats"><div><b class="hot">' + Math.round(p.score) + '</b><span>score</span></div>'
    + "<div><b>" + f.temp + "</b><span>temperature</span></div>" + cloudStat
    + "<div><b>" + Math.round(p.rain) + " mm</b><span>rain</span></div></div>"
    + sunny
    + '<p class="note">' + rankLine
    + "Bold months are the ones in the score. Rain is the total; temperature"
    + (p.cloud == null ? " is the average." : " and cloud are averages.")
    + "</p>"
    + '<table class="months">' + head + table + "</table>";
}
function renderLegend(rows) {
  const el = document.getElementById("legend");
  if (!el) return;
  const titles = {
    score: ["Weaker match", "Best"],
    temp: ["Colder", "Warmer"],
    cloud: ["Cloudier", "Clearer"],
    rain: ["Wetter", "Drier"]
  };
  let textLo = "Low", textHi = "High";
  if (state.layer === "score") { textLo = "0"; textHi = "100"; }
  else if (rows.scale) {
    const s = rows.scale;
    const pack = (v, kind) => kind === "temp" ? v.toFixed(1) + "°" : kind === "cloud" ? Math.round(v) + "%" : Math.round(v) + " mm";
    if (state.layer === "temp") { textLo = pack(s.t0, "temp"); textHi = pack(s.t1, "temp"); }
    if (state.layer === "cloud") { textLo = pack(s.c1, "cloud"); textHi = pack(s.c0, "cloud"); }
    if (state.layer === "rain") { textLo = pack(s.r1, "rain"); textHi = pack(s.r0, "rain"); }
  }
  el.innerHTML = "<div>" + titles[state.layer][0] + " → " + titles[state.layer][1] + "</div>"
    + '<div class="swatch" style="background:linear-gradient(90deg,' + HEAT.join(",") + ')"></div>'
    + '<div class="ends"><span>' + textLo + "</span><span>" + textHi + "</span></div>";
}
function rowsToDraw(list) {
  if (!list.length) return [];
  if (state.area || state.bbox) return list;
  const fine = fineViewportCells();
  if (fine) return scoredSet(fine, list.scale);
  const b = map.getBounds().pad(0.15);
  return list.filter(p => inside(p, [b.getSouth(), b.getWest(), b.getNorth(), b.getEast()]));
}
function segmentsCross(a, b, c, d) {
  function side(p, q, r) {
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
  }
  const c1 = side(a, b, c), c2 = side(a, b, d), c3 = side(c, d, a), c4 = side(c, d, b);
  return (c1 > 0) !== (c2 > 0) && (c3 > 0) !== (c4 > 0);
}
// Island chains were simplified into one ring that crosses itself, which strokes
// as a scribble across the sea. A crossing of neighbors is a spike; a wide gap is not.
function ringDrawable(ring) {
  if (!ring || ring.length < 4) return false;
  const closed = ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1];
  const pts = closed ? ring.slice(0, -1) : ring;
  const m = pts.length;
  if (m < 4) return false;
  if (m > 700) return true;
  for (let i = 0; i < m; i++) {
    for (let j = i + 2; j < m; j++) {
      if (i === 0 && j === m - 1) continue;
      if (!segmentsCross(pts[i], pts[(i + 1) % m], pts[j], pts[(j + 1) % m])) continue;
      const gap = Math.min(j - i, m - (j - i));
      if (gap > 3) return false;
    }
  }
  return true;
}
function displayGeometry(area) {
  const g = area && area.geometry;
  if (!g || !g.coordinates) return null;
  const polys = g.type === "Polygon" ? [g.coordinates] : (g.type === "MultiPolygon" ? g.coordinates : []);
  const kept = [];
  for (const rings of polys) {
    if (!rings || !rings[0] || !ringDrawable(rings[0])) continue;
    kept.push([rings[0]]);
  }
  if (!kept.length) return null;
  return { type: "MultiPolygon", coordinates: kept };
}
function scopeBounds() {
  const countryB = state.area && state.area.geometry ? viewBounds(state.area) : null;
  const boxB = state.bbox ? [[state.bbox[0], state.bbox[1]], [state.bbox[2], state.bbox[3]]] : null;
  if (countryB && boxB) {
    const s = Math.max(countryB[0][0], boxB[0][0]);
    const w = Math.max(countryB[0][1], boxB[0][1]);
    const n = Math.min(countryB[1][0], boxB[1][0]);
    const e = Math.min(countryB[1][1], boxB[1][1]);
    if (s < n && w < e) return [[s, w], [n, e]];
    return boxB;
  }
  return countryB || boxB || [[-56, -168], [72, 178]];
}
function showAreaBox() {
  if (areaRect) { map.removeLayer(areaRect); areaRect = null; }
  if (!state.bbox) return;
  const [s, w, n, e] = state.bbox;
  areaRect = L.rectangle([[s, w], [n, e]], {
    pane: "marks", interactive: false, bubblingMouseEvents: false,
    color: "#1c1914", weight: 2, dashArray: "5 4", fill: false
  }).addTo(map);
  const el = areaRect.getElement && areaRect.getElement();
  if (el) el.style.pointerEvents = "none";
}
function renderMap(list) {
  layer.clearLayers();
  markLayer.clearLayers();
  const drawRows = rowsToDraw(list);
  state.drawStep = drawRows[0] ? (drawRows[0].dlat || DATA.dlat || 0.125) : (DATA.dlat || 0.125);
  syncCellPane();
  const heat = state.draw === "heat";
  const pad = heat ? 1.22 : 1.035;
  for (const row of drawRows) {
    const h = halfOf(row);
    const rect = L.rectangle(
      [[row.lat - h.lat * pad, row.lon - h.lon * pad], [row.lat + h.lat * pad, row.lon + h.lon * pad]],
      { pane: "cells", stroke: false, weight: 0, opacity: 0, fillColor: colorOf(row), fillOpacity: 1 }
    );
    const f = fmt(row);
    if (window.matchMedia("(hover: hover)").matches) {
      const sunnyTip = row.sunny_days == null ? "" : "<br>" + Math.round(row.sunny_days) + " sunny days / year";
      rect.bindTooltip("<strong>" + esc(placeName(row)) + "</strong><br>score " + Math.round(row.score) + "<br>" + f.temp + (f.cloud ? " · " + f.cloud : "") + " · " + f.rain + sunnyTip, { sticky: true });
    }
    rect.on("click", () => {
      if (state.suppressClick) return;
      openRow(row, list);
    });
    rect.addTo(layer);
  }
  for (const row of list.slice(0, 10)) {
    addOutline(row, { color: "#ffffff", weight: 3 });
    addOutline(row, { color: "#1c1914", weight: 1.5 });
  }
  if (state.selected) {
    const row = list.find(r => r.lat === state.selected.lat && r.lon === state.selected.lon) || state.selected;
    addOutline(row, { color: "#ffffff", weight: 4, dashArray: "7 4" });
  }
  showAreaBox();
  if (hoverRow) highlight(hoverRow);
  if (state.fit) {
    const padTop = document.getElementById("dock").offsetHeight + 12;
    const padBottom = window.innerWidth < 721 ? (state.boardOpen ? 180 : 72) : 24;
    let bounds = scopeBounds();
    map.fitBounds(bounds, { animate: false, paddingTopLeft: [16, padTop], paddingBottomRight: [16, padBottom] });
    state.fit = false;
  }
}
function render() {
  if (rendering) return;
  rendering = true;
  try {
    const rows = listRows();
    if (state.selected) {
      const still = rows.find(r => r.lat === state.selected.lat && r.lon === state.selected.lon);
      if (still) state.selected = still;
    }
    syncChrome();
    renderFilters();
    renderBoard(rows);
    renderDetail(rows);
    renderLegend(rows);
    renderMap(rows);
  } finally {
    rendering = false;
    flushUrl();
    if (viewportSyncQueued) scheduleViewportSync();
  }
}
function openRow(row, list) {
  state.selected = row;
  state.cardOpen = true;
  const dockH = document.getElementById("dock").offsetHeight + 8;
  const bot = window.innerWidth < 721 ? Math.round(window.innerHeight * 0.42) : 24;
  const d = row.dlat || 0.4;
  map.fitBounds([[row.lat - d, row.lon - d], [row.lat + d, row.lon + d]], {
    paddingTopLeft: [24, dockH],
    paddingBottomRight: [24, bot],
    maxZoom: (row.dlat || 0.125) > 1 ? 6 : 9,
    animate: true
  });
  render();
}
function chip(label, on, click) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "chip" + (on ? " on" : "");
  b.textContent = label;
  b.onclick = click;
  return b;
}
// Shareable query: c, box, m, w, ly, dr, ll, z, at.
// w is warmth, clear sky, dryness as shares that sum to 100.
// A triple whose values are all 0–10 is the old level slider and converts to shares.
// Omitted keys keep the defaults. pushState only when country or box changes.
const WINTER_MONTHS = "0,1,11";
let shareReady = false;
let urlIntent = "replace";
let geoStamp = "";
function roundTo(n, digits) {
  const f = 10 ** digits;
  return Math.round(n * f) / f;
}
function monthKey(set) {
  return [...set].sort((a, b) => a - b).join(",");
}
function geoToken() {
  const box = state.bbox ? state.bbox.map(n => roundTo(n, 3)).join(",") : "";
  return [state.country || "", box].join("|");
}
function noteGeo() { urlIntent = "push"; }
function nums(raw, count) {
  if (!raw) return null;
  const parts = String(raw).split(",").map(Number);
  if (parts.length !== count || parts.some(v => !Number.isFinite(v))) return null;
  return parts;
}
function parseMonths(raw) {
  if (!raw) return new Set([11, 0, 1]);
  const set = new Set();
  for (const n of String(raw).split(",").map(Number)) {
    if (Number.isInteger(n) && n >= 0 && n <= 11) set.add(n);
  }
  return set.size ? set : new Set([11, 0, 1]);
}
function equalShares() {
  return { temp: 33, cloud: 33, rain: 34 };
}
function sharesFromParts(vals) {
  const sum = vals[0] + vals[1] + vals[2];
  if (sum <= 0) return equalShares();
  const exact = vals.map(v => 100 * v / sum);
  const base = exact.map(v => Math.floor(v));
  let left = 100 - base.reduce((a, b) => a + b, 0);
  const order = exact.map((v, i) => ({ i, frac: v - base[i] })).sort((a, b) => b.frac - a.frac || b.i - a.i);
  for (let k = 0; k < left; k++) base[order[k].i] += 1;
  return { temp: base[0], cloud: base[1], rain: base[2] };
}
function parseWeights(raw) {
  const parts = nums(raw, 3);
  if (!parts) return equalShares();
  const vals = parts.map(v => Math.round(v));
  if (vals.some(v => v < 0)) return equalShares();
  if (vals.every(v => v <= 10)) return sharesFromParts(vals);
  const clamped = vals.map(v => Math.max(0, Math.min(100, v)));
  if (clamped[0] + clamped[1] + clamped[2] === 100) {
    return { temp: clamped[0], cloud: clamped[1], rain: clamped[2] };
  }
  return sharesFromParts(clamped);
}
function readShare() {
  const q = new URLSearchParams(location.search);
  const box = nums(q.get("box"), 4);
  const ll = nums(q.get("ll"), 2);
  const at = nums(q.get("at"), 2);
  const z = q.get("z") == null || q.get("z") === "" ? null : Number(q.get("z"));
  let country = "";
  let bbox = null;
  let area = null;
  if (q.get("c")) {
    const found = findCountry(q.get("c"));
    if (found) {
      country = found.name;
      area = found;
    }
  }
  if (box) {
    bbox = [Math.min(box[0], box[2]), Math.min(box[1], box[3]), Math.max(box[0], box[2]), Math.max(box[1], box[3])];
  }
  const layer = { t: "temp", c: "cloud", r: "rain" }[q.get("ly")] || "score";
  return {
    country, bbox, area,
    months: parseMonths(q.get("m")),
    weights: parseWeights(q.get("w")),
    layer,
    draw: q.get("dr") === "heat" ? "heat" : "tiles",
    ll: ll && ll[0] >= -90 && ll[0] <= 90 && ll[1] >= -180 && ll[1] <= 180 ? ll : null,
    z: Number.isFinite(z) && z >= 2 && z <= 14 ? z : null,
    at: at && at[0] >= -90 && at[0] <= 90 && at[1] >= -180 && at[1] <= 180 ? at : null
  };
}
function composeAddress() {
  const p = new URLSearchParams();
  if (state.country) p.set("c", state.country);
  if (state.bbox) p.set("box", state.bbox.map(n => roundTo(n, 3)).join(","));
  const mk = monthKey(state.months);
  if (mk && mk !== WINTER_MONTHS) p.set("m", mk);
  const wt = [state.weights.temp, state.weights.cloud, state.weights.rain];
  if (wt[0] !== 33 || wt[1] !== 33 || wt[2] !== 34) p.set("w", wt.join(","));
  const ly = { temp: "t", cloud: "c", rain: "r" }[state.layer];
  if (ly) p.set("ly", ly);
  if (state.draw === "heat") p.set("dr", "heat");
  const center = map.getCenter();
  const zoom = map.getZoom();
  if (center && Number.isFinite(center.lat) && Number.isFinite(center.lng) && Number.isFinite(zoom)) {
    p.set("ll", roundTo(center.lat, 3) + "," + roundTo(center.lng, 3));
    p.set("z", String(roundTo(zoom, 2)));
  }
  if (state.cardOpen && state.selected && Number.isFinite(state.selected.lat)) {
    p.set("at", roundTo(state.selected.lat, 4) + "," + roundTo(state.selected.lon, 4));
  }
  const qs = p.toString();
  return location.pathname + (qs ? "?" + qs : "") + location.hash;
}
function flushUrl() {
  if (!shareReady) return;
  const geo = geoToken();
  const push = urlIntent === "push" && geo !== geoStamp;
  urlIntent = "replace";
  const next = composeAddress();
  const here = location.pathname + location.search + location.hash;
  geoStamp = geo;
  if (next === here) return;
  if (push) history.pushState(null, "", next);
  else history.replaceState(null, "", next);
}
function applyShare(spec) {
  state.months = spec.months;
  state.layer = spec.layer;
  state.weights = spec.weights;
  state.draw = spec.draw;
  state.country = spec.country;
  state.area = spec.area || null;
  state.bbox = spec.bbox;
  state.selected = null;
  state.cardOpen = false;
  state.pendingAt = spec.at ? { lat: spec.at[0], lon: spec.at[1] } : null;
  state.fit = !(spec.ll && spec.z != null);
  state.loading = "";
  state.selecting = false;
  const search = document.getElementById("q");
  if (search) search.value = spec.country || "";
  if (spec.ll && spec.z != null) {
    map.invalidateSize({ animate: false });
    map.setView([spec.ll[0], spec.ll[1]], spec.z, { animate: false });
  }
}
function nearestRow(rows, at) {
  let best = null;
  let bestD = Infinity;
  for (const row of rows) {
    const d = (row.lat - at.lat) ** 2 + (row.lon - at.lon) ** 2;
    if (d < bestD) { bestD = d; best = row; }
  }
  if (!best) return null;
  const tol = Math.max(best.dlat || 0.125, best.dlon || 0.125);
  if (Math.abs(best.lat - at.lat) > tol || Math.abs(best.lon - at.lon) > tol) return null;
  return best;
}
function takePendingCell() {
  if (!state.pendingAt) return;
  const hit = nearestRow(listRows(), state.pendingAt);
  state.pendingAt = null;
  if (!hit) return;
  state.selected = hit;
  state.cardOpen = true;
}
async function restoreFromLocation() {
  const mine = ++job;
  urlIntent = "replace";
  const spec = readShare();
  applyShare(spec);
  state.loading = (state.area || state.bbox) ? "Loading this area…" : "Loading the world grid…";
  try {
    if (!overviewPts) {
      const res = await fetch("world/overview.json");
      if (!res.ok) throw new Error("overview");
      overviewPts = unpack(await res.json());
    }
    if (mine !== job) return;
    if (state.area && state.area.geometry) await ensureTiles(state.area.bbox);
    else if (state.bbox) await ensureTiles(state.bbox);
    if (mine !== job) return;
    state.loading = "";
  } catch (err) {
    if (mine !== job) return;
    state.loading = "Could not load that area.";
  }
  if (mine !== job) return;
  takePendingCell();
  buildControls();
  render();
  geoStamp = geoToken();
  urlIntent = "replace";
  shareReady = true;
}
function buildControls() {
  const presets = [["Winter", [11, 0, 1]], ["Spring", [2, 3, 4]], ["Summer", [5, 6, 7]], ["Autumn", [8, 9, 10]], ["Year", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]];
  const presetBox = document.getElementById("presets");
  const monthBox = document.getElementById("months");
  presetBox.innerHTML = "";
  monthBox.innerHTML = "";
  for (const [label, idx] of presets) {
    const same = idx.length === state.months.size && idx.every(i => state.months.has(i));
    presetBox.appendChild(chip(label, same, () => { state.months = new Set(idx); buildControls(); render(); }));
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
  const layerIds = [["score", "Combined"], ["temp", "Temp"], ["cloud", "Cloud"], ["rain", "Rain"]];
  for (const [id, label] of layerIds) {
    layers.appendChild(chip(label, state.layer === id, () => { state.layer = id; buildControls(); render(); }));
  }
  const draw = document.getElementById("draw");
  draw.innerHTML = "";
  for (const [id, label] of [["tiles", "Tiles"], ["heat", "Heatmap"]]) {
    draw.appendChild(chip(label, state.draw === id, () => { state.draw = id; buildControls(); render(); }));
  }
  buildMix();
  syncChrome();
}
const MIX_NAMES = { temp: "Warmth", cloud: "Clear sky", rain: "Dryness" };
const MIX_SHORT = { temp: "Warm", cloud: "Sky", rain: "Dry" };
let mixDrag = null;
let mixFrame = 0;
function applyDivider(index, pct) {
  const t = state.weights.temp;
  const c = state.weights.cloud;
  const next = Math.max(0, Math.min(100, pct));
  if (index === 0) {
    const edge = t + c;
    if (next <= edge) {
      state.weights.temp = next;
      state.weights.cloud = edge - next;
    } else {
      state.weights.temp = next;
      state.weights.cloud = 0;
      state.weights.rain = 100 - next;
    }
  } else if (next >= t) {
    state.weights.cloud = next - t;
    state.weights.rain = 100 - next;
  } else {
    state.weights.temp = next;
    state.weights.cloud = 0;
    state.weights.rain = 100 - next;
  }
}
function dividerIndexAt(clientX) {
  const track = document.querySelector("#weights .mix-track");
  const rect = track.getBoundingClientRect();
  const x = clientX - rect.left;
  const a = rect.width * state.weights.temp / 100;
  const b = rect.width * (state.weights.temp + state.weights.cloud) / 100;
  return Math.abs(x - a) <= Math.abs(x - b) ? 0 : 1;
}
function mixClientPct(clientX) {
  const track = document.querySelector("#weights .mix-track");
  const rect = track.getBoundingClientRect();
  if (!rect.width) return 0;
  const x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
  return Math.round(100 * x / rect.width);
}
function paintMix() {
  const bar = document.getElementById("weights");
  if (!bar) return;
  const track = bar.querySelector(".mix-track");
  const grips = bar.querySelectorAll(".grip");
  if (!track || grips.length < 2) return;
  const width = track.getBoundingClientRect().width || 0;
  for (const key of ["temp", "cloud", "rain"]) {
    const pct = state.weights[key];
    const part = bar.querySelector('.part[data-key="' + key + '"]');
    const px = width * pct / 100;
    part.style.flexGrow = String(pct);
    part.classList.toggle("zero", pct === 0);
    part.classList.toggle("tight", pct > 0 && px < 34);
    part.querySelector(".nm").textContent = pct === 0 ? "" : (px >= 78 ? MIX_NAMES[key] : MIX_SHORT[key]);
    part.querySelector(".pct").textContent = pct + "%";
    const label = MIX_NAMES[key] + " " + pct + "%";
    part.title = label;
    part.setAttribute("aria-label", label);
  }
  const lefts = [state.weights.temp, state.weights.temp + state.weights.cloud];
  grips[0].style.left = lefts[0] + "%";
  grips[1].style.left = lefts[1] + "%";
  const knobs = track.querySelectorAll(".knob");
  if (knobs[0]) knobs[0].style.left = lefts[0] + "%";
  if (knobs[1]) knobs[1].style.left = lefts[1] + "%";
  const zeros = track.querySelector(".mix-zeros");
  if (zeros) {
    zeros.innerHTML = "";
    const spots = [["temp", 0, "left"], ["cloud", lefts[0], "left"], ["rain", lefts[1], "right"]];
    let stackLeft = 0;
    let stackRight = 0;
    for (const [key, at, side] of spots) {
      if (state.weights[key] !== 0) continue;
      const tag = document.createElement("span");
      tag.className = "zero-tag";
      tag.textContent = MIX_NAMES[key] + " 0%";
      if (side === "right") {
        tag.style.right = "20px";
        tag.style.top = (3 + stackRight * 13) + "px";
        stackRight += 1;
      } else {
        tag.style.left = "calc(" + at + "% + 20px)";
        tag.style.top = (3 + stackLeft * 13) + "px";
        stackLeft += 1;
      }
      zeros.appendChild(tag);
    }
  }
}
function queueMixScore() {
  if (mixFrame) return;
  mixFrame = requestAnimationFrame(() => {
    mixFrame = 0;
    render();
  });
}
function buildMix() {
  const bar = document.getElementById("weights");
  bar.innerHTML = "";
  const track = document.createElement("div");
  track.className = "mix-track";
  const bits = [["temp", "warm"], ["cloud", "sky"], ["rain", "dry"]];
  for (const [key, tone] of bits) {
    const part = document.createElement("div");
    part.className = "part " + tone;
    part.dataset.key = key;
    part.innerHTML = '<span class="nm"></span><span class="pct"></span>';
    track.appendChild(part);
  }
  const zeros = document.createElement("div");
  zeros.className = "mix-zeros";
  track.appendChild(zeros);
  for (let n = 0; n < 2; n++) {
    const knob = document.createElement("i");
    knob.className = "knob";
    track.appendChild(knob);
  }
  bar.appendChild(track);
  for (const i of [0, 1]) {
    const grip = document.createElement("button");
    grip.type = "button";
    grip.className = "grip";
    grip.dataset.i = String(i);
    grip.setAttribute("aria-label", i === 0 ? "Divider between warmth and clear sky" : "Divider between clear sky and dryness");
    grip.addEventListener("pointerdown", (e) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      e.preventDefault();
      grip.setPointerCapture(e.pointerId);
      mixDrag = { i: dividerIndexAt(e.clientX), id: e.pointerId, moved: false };
      grip.classList.add("dragging");
    });
    grip.addEventListener("pointermove", (e) => {
      if (!mixDrag || e.pointerId !== mixDrag.id) return;
      mixDrag.moved = true;
      applyDivider(mixDrag.i, mixClientPct(e.clientX));
      paintMix();
      queueMixScore();
    });
    const finishMix = (e, usePoint) => {
      if (!mixDrag || e.pointerId !== mixDrag.id) return;
      const which = mixDrag.i;
      const moved = mixDrag.moved;
      mixDrag = null;
      grip.classList.remove("dragging");
      if (mixFrame) { cancelAnimationFrame(mixFrame); mixFrame = 0; }
      if (!moved) return;
      if (usePoint) {
        applyDivider(which, mixClientPct(e.clientX));
        paintMix();
      }
      render();
    };
    grip.addEventListener("pointerup", (e) => finishMix(e, true));
    grip.addEventListener("pointercancel", (e) => finishMix(e, false));
    grip.addEventListener("click", (e) => e.preventDefault());
    bar.appendChild(grip);
  }
  paintMix();
}
let searchTimer = 0;
let searchGen = 0;
function hideHits() {
  searchGen++;
  clearTimeout(searchTimer);
  const box = document.getElementById("hits");
  if (!box) return;
  box.classList.remove("open");
}
function showHits(items) {
  const box = document.getElementById("hits");
  if (!items.length) { box.classList.remove("open"); box.innerHTML = ""; return; }
  box.innerHTML = items.map((hit, i) => '<button type="button" data-i="' + i + '">' + esc(hit.name) + "<small>" + esc(hit.hint) + "</small></button>").join("");
  box.classList.add("open");
  box.querySelectorAll("button").forEach(btn => { btn.onclick = () => goToHit(items[+btn.dataset.i]); });
}
function localHits(q) {
  const s = q.trim().toLowerCase();
  if (!s) return [];
  const hits = [];
  for (const area of AREAS) {
    if (area.name.toLowerCase().includes(s)) hits.push({ kind: "area", name: area.name, hint: "Country", country: area });
  }
  for (const [name, lat, lon] of CITIES) {
    if (name.toLowerCase().includes(s)) hits.push({ kind: "place", name, hint: "Place", lat, lon });
  }
  for (const [name, lat, lon] of WORLD_CITIES) {
    if (name.toLowerCase().includes(s)) hits.push({ kind: "place", name, hint: "Place", lat, lon });
  }
  return hits.slice(0, 8);
}
async function remoteHits(q, items) {
  const res = await fetch("https://geocoding-api.open-meteo.com/v1/search?language=en&count=5&name=" + encodeURIComponent(q));
  if (!res.ok) return items;
  const data = await res.json();
  const extra = [];
  for (const r of data.results || []) {
    const country = findCountry(r.country || r.name);
    if (r.feature_code === "PCLI" && country) {
      extra.push({ kind: "area", name: r.name, hint: "Country", country });
    } else if (r.latitude != null) {
      extra.push({
        kind: "place",
        name: r.name,
        hint: [r.admin1, r.country].filter(Boolean).join(", "),
        lat: r.latitude,
        lon: r.longitude,
        countryCode: r.country_code
      });
    }
  }
  const names = new Set(items.map(h => h.name.toLowerCase()));
  return items.concat(extra.filter(h => !names.has(h.name.toLowerCase()))).slice(0, 8);
}
function goToHit(hit) {
  hideHits();
  document.getElementById("q").value = hit.name;
  if (hit.kind === "area") {
    const b = hit.country.bbox || [hit.country.s, hit.country.w, hit.country.n, hit.country.e];
    return enterWorld([b[0], b[1], b[2], b[3]], hit.country.name);
  }
  return focusWorldCity(hit.lat, hit.lon);
}
async function ensureTiles(box) {
  const ids = (state.area && state.area.geometry) ? tilesForArea(state.area) : tilesForBounds(box);
  await Promise.all(ids.map(async id => {
    if (tileCache.has(id)) return;
    const res = await fetch("world/t/" + id + ".json");
    tileCache.set(id, res.ok ? unpack(await res.json()) : []);
  }));
}
function normBox(bbox) {
  return [Math.min(bbox[0], bbox[2]), Math.min(bbox[1], bbox[3]), Math.max(bbox[0], bbox[2]), Math.max(bbox[1], bbox[3])];
}
async function loadWorld(bbox, mine) {
  const focused = !!(bbox || (state.area && state.area.geometry));
  state.loading = focused ? "Loading this area…" : "Loading the world grid…";
  syncChrome();
  document.getElementById("board-title").textContent = state.loading;
  try {
    if (!overviewPts) {
      const res = await fetch("world/overview.json");
      if (!res.ok) throw new Error("overview");
      overviewPts = unpack(await res.json());
    }
    if (mine !== job) return;
    if (state.area && state.area.geometry) await ensureTiles(state.area.bbox);
    else if (bbox) await ensureTiles(bbox);
    if (mine !== job) return;
    state.loading = "";
  } catch (err) {
    if (mine !== job) return;
    state.loading = "Could not load that area.";
  }
}
async function reloadScope() {
  const mine = ++job;
  state.fit = true;
  state.selected = null;
  state.cardOpen = false;
  noteGeo();
  const tileBox = state.bbox || (state.area && state.area.bbox) || null;
  await loadWorld(tileBox, mine);
  if (mine !== job) return;
  buildControls();
  render();
}
async function enterWorld(bbox, countryName) {
  const mine = ++job;
  if (countryName) {
    const area = findCountry(countryName);
    state.area = area || null;
    state.country = area ? area.name : "";
  } else if (bbox) {
    state.area = null;
    state.country = "";
    state.bbox = normBox(bbox);
  } else {
    state.area = null;
    state.country = "";
    state.bbox = null;
  }
  state.fit = true;
  state.selected = null;
  state.cardOpen = false;
  noteGeo();
  const tileBox = state.bbox || (state.area && state.area.bbox) || null;
  await loadWorld(tileBox, mine);
  if (mine !== job) return;
  buildControls();
  render();
}
async function focusWorldCity(lat, lon) {
  const pad = 3;
  await enterWorld([lat - pad, lon - pad, lat + pad, lon + pad]);
  const rows = listRows();
  const nearest = rows.slice().sort((a, b) => km(a, { lat, lon }) - km(b, { lat, lon }))[0];
  if (!nearest) return;
  state.selected = nearest;
  state.cardOpen = true;
  state.fit = false;
  render();
}
function finishDraw(bbox) {
  state.selecting = false;
  drawing = false;
  anchor = null;
  state.suppressClick = true;
  setTimeout(() => { state.suppressClick = false; }, 400);
  map.dragging.enable();
  if (rubber) { map.removeLayer(rubber); rubber = null; }
  state.bbox = normBox(bbox);
  if (!state.country) {
    state.area = null;
    const q = document.getElementById("q");
    if (q) q.value = "";
  }
  state.fit = true;
  state.selected = null;
  state.cardOpen = false;
  noteGeo();
  const mine = ++job;
  loadWorld(state.bbox, mine).then(() => {
    if (mine !== job) return;
    buildControls();
    render();
  });
}
function beginDraw(latlng) {
  if (!state.selecting || drawing || !latlng) return;
  drawing = true;
  anchor = latlng;
  map.dragging.disable();
  if (rubber) map.removeLayer(rubber);
  rubber = L.rectangle([[latlng.lat, latlng.lng], [latlng.lat, latlng.lng]], {
    pane: "marks", color: "#c11212", weight: 2, fillOpacity: 0.08, interactive: false
  }).addTo(map);
}
function moveDraw(latlng) {
  if (!drawing || !anchor || !rubber || !latlng) return;
  rubber.setBounds(L.latLngBounds(anchor, latlng));
}
function endDraw(latlng) {
  if (!drawing) return;
  drawing = false;
  const start = anchor;
  let end = latlng;
  if (!end && rubber) end = rubber.getBounds().getNorthEast();
  anchor = null;
  if (rubber) { map.removeLayer(rubber); rubber = null; }
  map.dragging.enable();
  state.selecting = false;
  if (!start || !end) { syncChrome(); return; }
  const b = L.latLngBounds(start, end);
  if (b.getNorth() - b.getSouth() < 0.25 && b.getEast() - b.getWest() < 0.25) {
    syncChrome();
    return;
  }
  finishDraw([b.getSouth(), b.getWest(), b.getNorth(), b.getEast()]);
}
map.on("mousedown", (e) => { if (state.selecting) beginDraw(e.latlng); });
map.on("mousemove", (e) => moveDraw(e.latlng));
map.on("mouseup", (e) => endDraw(e.latlng));
window.addEventListener("mouseup", () => { if (drawing) endDraw(null); });
const surface = map.getContainer();
surface.addEventListener("touchstart", (ev) => {
  if (!state.selecting || !ev.touches[0]) return;
  ev.preventDefault();
  beginDraw(map.mouseEventToLatLng(ev.touches[0]));
}, { passive: false });
surface.addEventListener("touchmove", (ev) => {
  if (!drawing || !ev.touches[0]) return;
  ev.preventDefault();
  moveDraw(map.mouseEventToLatLng(ev.touches[0]));
}, { passive: false });
surface.addEventListener("touchend", (ev) => {
  const t = ev.changedTouches && ev.changedTouches[0];
  endDraw(t ? map.mouseEventToLatLng(t) : anchor);
});
map.on("moveend", () => {
  if (shareReady && !rendering) flushUrl();
  scheduleViewportSync();
});

document.getElementById("board-toggle").onclick = () => {
  state.boardOpen = !state.boardOpen;
  syncChrome();
  paintPlacesNow();
};
document.getElementById("card-close").onclick = () => {
  state.cardOpen = false;
  state.selected = null;
  render();
};
document.getElementById("card-back").onclick = () => {
  state.cardOpen = false;
  state.boardOpen = true;
  render();
};
document.getElementById("draw-area").onclick = () => {
  state.selecting = !state.selecting;
  if (!state.selecting) {
    drawing = false;
    anchor = null;
    if (rubber) { map.removeLayer(rubber); rubber = null; }
    map.dragging.enable();
  }
  syncChrome();
};
document.getElementById("q").addEventListener("input", (e) => {
  const q = e.target.value;
  const items = localHits(q);
  const gen = ++searchGen;
  showHits(items);
  clearTimeout(searchTimer);
  if (q.trim().length < 2) return;
  searchTimer = setTimeout(async () => {
    try {
      const next = await remoteHits(q, items);
      if (gen !== searchGen) return;
      showHits(next);
    } catch (err) { /* local hits stay */ }
  }, 280);
});
document.addEventListener("pointerdown", (e) => {
  const row = document.querySelector(".search-row");
  if (row && !row.contains(e.target)) hideHits();
});
document.getElementById("q").addEventListener("keydown", (e) => {
  if (e.key === "Escape") hideHits();
  if (e.key === "Enter") {
    const first = document.querySelector("#hits button");
    if (first) first.click();
  }
});
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (state.selecting || drawing) {
    state.selecting = false;
    drawing = false;
    anchor = null;
    if (rubber) { map.removeLayer(rubber); rubber = null; }
    map.dragging.enable();
    syncChrome();
    return;
  }
  if (state.cardOpen) {
    state.cardOpen = false;
    state.selected = null;
    render();
  }
});
const places = document.getElementById("places");
places.addEventListener("scroll", () => {
  if (places._queued) return;
  places._queued = true;
  requestAnimationFrame(() => { places._queued = false; paintPlacesNow(); });
}, { passive: true });
places.addEventListener("mouseover", (e) => {
  const btn = e.target.closest(".place");
  if (!btn) return;
  highlight(state.rows[+btn.dataset.i]);
});
places.addEventListener("mouseout", (e) => {
  const next = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".place");
  if (next && places.contains(next)) return;
  highlight(null);
});
places.addEventListener("click", (e) => {
  const btn = e.target.closest(".place");
  if (!btn) return;
  const row = state.rows[+btn.dataset.i];
  if (row) openRow(row, state.rows);
});
window.addEventListener("resize", () => { map.invalidateSize(); syncChrome(); paintMix(); });
window.addEventListener("popstate", () => {
  shareReady = false;
  restoreFromLocation();
});
restoreFromLocation();
</script>
</body>
</html>
"""

html = html.replace("__DATA__", payload).replace("__AREAS__", area_payload)
(ROOT / "index.html").write_text(html)
print(f"wrote index.html {(ROOT / 'index.html').stat().st_size} bytes")
