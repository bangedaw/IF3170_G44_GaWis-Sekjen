"""Mejiro Express — 3D Packing & Experiment Results Visualizer Web Application.

Provides an interactive 3D Web UI (Three.js orbit controls), side-by-side initial vs
final state comparison, multi-truck inspection, outside package tracking, metrics display,
and integration with Edo's plots.py.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

SRC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from visualization import plots
from visualization.state_view import state_summary


def find_all_runs(base_dirs: list[Path]) -> list[dict[str, Any]]:
    runs = []
    seen = set()
    for base in base_dirs:
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.json")):
            if "plots" in p.parts or "configs" in p.parts:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(data, dict) and "algorithm" in data and "final_state" in data:
                rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                if rel in seen:
                    continue
                seen.add(rel)
                runs.append({
                    "path": rel,
                    "filename": p.name,
                    "folder": p.parent.name,
                    "algorithm": data.get("algorithm", "unknown"),
                    "label": data.get("label") or p.stem,
                    "seed": data.get("seed"),
                    "final_objective": data.get("final_objective", 0.0),
                    "final_value": data.get("final_value", 0.0),
                    "feasible": data.get("feasible", False),
                    "duration_sec": data.get("duration_sec", 0.0),
                    "iterations": data.get("iterations", 0),
                })
    return runs


def load_run_details(rel_path: str) -> dict[str, Any]:
    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {rel_path}")
    data = json.loads(full_path.read_text(encoding="utf-8"))

    problem = data["problem"]
    init_state = data.get("initial_state", {})
    final_state = data.get("final_state", {})

    init_summary = state_summary(problem, init_state) if init_state else None
    final_summary = state_summary(problem, final_state) if final_state else None

    return {
        "metadata": data,
        "initial_summary": init_summary,
        "final_summary": final_summary,
    }


def render_plot_image_bytes(rel_path: str, plot_type: str = "auto") -> bytes:
    full_path = REPO_ROOT / rel_path
    run = json.loads(full_path.read_text(encoding="utf-8"))
    history = run.get("history", {})

    if plot_type == "ga" or (plot_type == "auto" and "max" in history and "avg" in history):
        fig = plots.plot_ga(run)
    elif plot_type == "acceptance" or (plot_type == "auto" and "acceptance_prob" in history):
        fig = plots.plot_acceptance_prob(run)
    else:
        fig = plots.plot_objective(run)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mejiro Express — 3D Container Packing Visualizer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {
      --bg: #0b0f19;
      --surface: #111827;
      --surface-border: #1f2937;
      --surface-hover: #1e293b;
      --primary: #3b82f6;
      --primary-glow: rgba(59, 130, 246, 0.25);
      --accent: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      overflow-x: hidden;
    }
    header {
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--surface-border);
      padding: 14px 28px;
      position: sticky;
      top: 0;
      z-index: 50;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #2563eb, #10b981);
      border-radius: 10px;
      display: grid;
      place-items: center;
      font-size: 20px;
      box-shadow: 0 4px 12px var(--primary-glow);
    }
    .brand h1 {
      font-size: 1.15rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #ffffff, #93c5fd);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .brand p { font-size: 0.75rem; color: var(--text-muted); }

    .selector-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      max-width: 650px;
    }
    select {
      flex: 1;
      background: #0f172a;
      color: #fff;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 0.85rem;
      font-family: inherit;
      outline: none;
      cursor: pointer;
      transition: all 0.2s;
    }
    select:focus { border-color: var(--primary); box-shadow: 0 0 0 2px var(--primary-glow); }

    .main-container {
      padding: 24px 28px;
      max-width: 1600px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }
    .metric-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      position: relative;
      overflow: hidden;
    }
    .metric-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: var(--primary);
      opacity: 0.7;
    }
    .metric-card.success::before { background: var(--accent); }
    .metric-card.warning::before { background: var(--warning); }
    .metric-card.danger::before { background: var(--danger); }
    .metric-label { font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.05em; }
    .metric-val { font-size: 1.35rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
    .metric-sub { font-size: 0.75rem; color: var(--text-muted); }

    .truck-tabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--surface-border);
      padding-bottom: 10px;
      align-items: center;
    }
    .tab-btn {
      background: #1e293b;
      color: var(--text-muted);
      border: 1px solid transparent;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .tab-btn.active {
      background: var(--primary);
      color: #fff;
      box-shadow: 0 2px 8px var(--primary-glow);
    }

    .viewers-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    @media (max-width: 1024px) {
      .viewers-row { grid-template-columns: 1fr; }
    }
    .viewport-box {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .viewport-header {
      padding: 12px 18px;
      background: #0f172a;
      border-bottom: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .viewport-title {
      font-size: 0.88rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      font-size: 0.7rem;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 600;
    }
    .badge-feasible { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-infeasible { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .viewport-canvas {
      width: 100%;
      height: 480px;
      position: relative;
      background: radial-gradient(circle at center, #1e293b 0%, #0b0f19 100%);
    }
    .viewport-tooltip {
      position: absolute;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid #3b82f6;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 0.75rem;
      color: #fff;
      display: none;
      z-index: 10;
      box-shadow: 0 4px 14px rgba(0,0,0,0.5);
      font-family: 'JetBrains Mono', monospace;
    }
    .controls-hint {
      position: absolute;
      bottom: 10px;
      left: 12px;
      font-size: 0.7rem;
      color: var(--text-muted);
      background: rgba(0,0,0,0.5);
      padding: 4px 8px;
      border-radius: 4px;
      pointer-events: none;
    }

    .bottom-section {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    @media (max-width: 1024px) {
      .bottom-section { grid-template-columns: 1fr; }
    }
    .panel-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .panel-title {
      font-size: 0.95rem;
      font-weight: 700;
      border-bottom: 1px solid var(--surface-border);
      padding-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .package-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 10px;
      max-height: 280px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .pkg-chip {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 3px;
      font-size: 0.74rem;
    }
    .pkg-chip.fragile {
      border-color: #ef4444;
      background: rgba(239, 68, 68, 0.08);
    }
    .pkg-chip-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 700;
    }

    .plot-container {
      display: flex;
      align-items: center;
      justify-content: center;
      background: #0f172a;
      border-radius: 8px;
      overflow: hidden;
      padding: 10px;
      min-height: 280px;
    }
    .plot-container img {
      max-width: 100%;
      height: auto;
      border-radius: 6px;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-logo">🚚</div>
      <div>
        <h1>Mejiro Express — Visualizer</h1>
        <p>3D Container Packing & Local Search Results</p>
      </div>
    </div>
    <div class="selector-bar">
      <label for="runSelect" style="font-size: 0.8rem; font-weight:600; color:var(--text-muted);">Pilih Run:</label>
      <select id="runSelect"></select>
    </div>
  </header>

  <div class="main-container">
    <div class="metrics-grid" id="metricsGrid">
      <div class="metric-card"><div class="metric-label">Algoritma</div><div class="metric-val" id="mAlgo">-</div></div>
      <div class="metric-card success"><div class="metric-label">Final Objective</div><div class="metric-val" id="mFinalObj">-</div><div class="metric-sub" id="mInitObj">Awal: -</div></div>
      <div class="metric-card"><div class="metric-label">Total Nilai Paket</div><div class="metric-val" id="mFinalVal">-</div><div class="metric-sub" id="mInsideCount">-</div></div>
      <div class="metric-card" id="mFeasibleCard"><div class="metric-label">Status Solusi</div><div class="metric-val" id="mFeasible">-</div><div class="metric-sub" id="mViolations">-</div></div>
      <div class="metric-card"><div class="metric-label">Waktu Eksekusi</div><div class="metric-val" id="mDuration">-</div><div class="metric-sub" id="mIterations">-</div></div>
    </div>

    <div class="truck-tabs" id="truckTabs">
      <span style="font-size:0.8rem; font-weight:700; color:var(--text-muted); margin-right:6px;">Truk:</span>
    </div>

    <div class="viewers-row">
      <div class="viewport-box">
        <div class="viewport-header">
          <div class="viewport-title">🏁 State Awal (Initial)</div>
          <span class="badge" id="badgeInit">-</span>
        </div>
        <div class="viewport-canvas" id="canvasInit">
          <div class="viewport-tooltip" id="tipInit"></div>
          <div class="controls-hint">Orbit: Drag kiri | Zoom: Scroll | Pan: Drag kanan</div>
        </div>
      </div>

      <div class="viewport-box">
        <div class="viewport-header">
          <div class="viewport-title">🏆 State Akhir (Final Solusi)</div>
          <span class="badge" id="badgeFinal">-</span>
        </div>
        <div class="viewport-canvas" id="canvasFinal">
          <div class="viewport-tooltip" id="tipFinal"></div>
          <div class="controls-hint">Orbit: Drag kiri | Zoom: Scroll | Pan: Drag kanan</div>
        </div>
      </div>
    </div>

    <div class="bottom-section">
      <div class="panel-card">
        <div class="panel-title">
          <span>📦 Paket di Luar Peti Kemas (Unassigned)</span>
          <span style="font-size:0.75rem; font-weight:600; color:var(--text-muted);" id="outsideCountLabel">0 paket</span>
        </div>
        <div class="package-grid" id="outsideGrid"></div>
      </div>

      <div class="panel-card">
        <div class="panel-title">
          <span>📈 Grafik Riwayat Optimasi (plots.py)</span>
          <span style="font-size:0.75rem; font-weight:600; color:var(--primary);" id="plotTitle">Convergence</span>
        </div>
        <div class="plot-container">
          <img id="plotImage" src="" alt="Plot pencarian">
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentRunData = null;
    let selectedTruckIdx = 0;
    const sceneInit = create3DViewer('canvasInit', 'tipInit');
    const sceneFinal = create3DViewer('canvasFinal', 'tipFinal');

    function create3DViewer(containerId, tooltipId) {
      const container = document.getElementById(containerId);
      const tooltip = document.getElementById(tooltipId);
      const width = container.clientWidth;
      const height = container.clientHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      container.appendChild(renderer.domElement);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
      scene.add(ambientLight);
      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
      dirLight.position.set(20, 40, 30);
      scene.add(dirLight);

      const truckGroup = new THREE.Group();
      scene.add(truckGroup);

      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      container.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(truckGroup.children, true);
        if (intersects.length > 0 && intersects[0].object.userData.pkg) {
          const p = intersects[0].object.userData.pkg;
          tooltip.style.display = 'block';
          tooltip.style.left = (e.clientX - rect.left + 15) + 'px';
          tooltip.style.top = (e.clientY - rect.top + 15) + 'px';
          tooltip.innerHTML = `<strong>${p.id}</strong> ${p.is_fragile ? '⚠️ FRAGILE' : ''}<br>` +
                              `Nilai: ${p.value} | Berat: ${p.weight}<br>` +
                              `Dimensi: ${p.dims.join('x')} | ETA: ${p.eta} hari<br>` +
                              `Posisi: (${p.x}, ${p.y}, ${p.z}) Orientasi: ${p.orientation}`;
        } else {
          tooltip.style.display = 'none';
        }
      });

      container.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });

      window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      });

      function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
      }
      animate();

      return { scene, camera, controls, truckGroup };
    }

    function renderTruckToViewer(viewer, truck, packages) {
      const group = viewer.truckGroup;
      while (group.children.length > 0) {
        group.remove(group.children[0]);
      }

      if (!truck) return;
      const w = truck.dimensions.w;
      const l = truck.dimensions.l;
      const h = truck.dimensions.h;

      // Container bounding box wireframe
      const boxGeo = new THREE.BoxGeometry(w, h, l);
      const wireMat = new THREE.LineBasicMaterial({ color: 0x64748b, linewidth: 2 });
      const wire = new THREE.LineSegments(new THREE.EdgesGeometry(boxGeo), wireMat);
      wire.position.set(w / 2, h / 2, l / 2);
      group.add(wire);

      // Bottom grid floor
      const grid = new THREE.GridHelper(Math.max(w, l), Math.max(w, l), 0x334155, 0x1e293b);
      grid.position.set(w / 2, 0, l / 2);
      group.add(grid);

      // Packages
      const palette = [0x0033a0, 0xf2b01e, 0x0a8754, 0x7b2cbf, 0xe8702a, 0x0096c7, 0x588157, 0x3a0ca3];

      packages.forEach((p, idx) => {
        const dx = p.dims[0];
        const dy = p.dims[1];
        const dz = p.dims[2];

        const geo = new THREE.BoxGeometry(dx, dz, dy);
        const col = p.is_fragile ? 0xd90429 : palette[idx % palette.length];
        const mat = new THREE.MeshStandardMaterial({
          color: col,
          roughness: 0.35,
          metalness: 0.1,
          transparent: true,
          opacity: 0.88,
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(p.x + dx / 2, p.z + dz / 2, p.y + dy / 2);
        mesh.userData.pkg = p;

        const edgeGeo = new THREE.EdgesGeometry(geo);
        const edgeMat = new THREE.LineBasicMaterial({
          color: p.is_fragile ? 0xfef08a : 0x0f172a,
          linewidth: p.is_fragile ? 2 : 1
        });
        const edgeMesh = new THREE.LineSegments(edgeGeo, edgeMat);
        mesh.add(edgeMesh);

        group.add(mesh);
      });

      // Fit camera
      const maxDim = Math.max(w, l, h);
      viewer.camera.position.set(w * 1.6, h * 2.2, l * 2.4);
      viewer.controls.target.set(w / 2, h / 2, l / 2);
      viewer.camera.lookAt(w / 2, h / 2, l / 2);
    }

    async function loadRunsList() {
      const res = await fetch('/api/runs');
      const runs = await res.json();
      const sel = document.getElementById('runSelect');
      sel.innerHTML = '';
      runs.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.path;
        opt.textContent = `[${r.folder}] ${r.label} (seed ${r.seed}, obj: ${r.final_objective.toFixed(1)})`;
        sel.appendChild(opt);
      });

      if (runs.length > 0) {
        sel.value = runs[0].path;
        loadRun(runs[0].path);
      }

      sel.addEventListener('change', () => loadRun(sel.value));
    }

    async function loadRun(path) {
      const res = await fetch(`/api/run?path=${encodeURIComponent(path)}`);
      currentRunData = await res.json();
      updateUI();
    }

    function updateUI() {
      if (!currentRunData) return;
      const meta = currentRunData.metadata;
      const fin = currentRunData.final_summary;
      const init = currentRunData.initial_summary;

      document.getElementById('mAlgo').textContent = meta.algorithm;
      document.getElementById('mFinalObj').textContent = meta.final_objective.toFixed(1);
      document.getElementById('mInitObj').textContent = `Awal: ${meta.initial_objective.toFixed(1)}`;
      document.getElementById('mFinalVal').textContent = meta.final_value.toFixed(0);
      document.getElementById('mInsideCount').textContent = `Paket masuk: ${fin.inside_count}/${fin.total_packages}`;

      const feasCard = document.getElementById('mFeasibleCard');
      const mFeas = document.getElementById('mFeasible');
      const mViol = document.getElementById('mViolations');
      if (meta.feasible) {
        feasCard.className = 'metric-card success';
        mFeas.textContent = '✅ FEASIBLE';
        mViol.textContent = 'Semua constraint terpenuhi';
      } else {
        feasCard.className = 'metric-card danger';
        mFeas.textContent = '⚠️ TIDAK VALID';
        const v = meta.final_violations || {};
        mViol.textContent = Object.entries(v).filter(([k, val]) => val > 0).map(([k, val]) => `${k}:${val}`).join(' ') || 'Pelanggaran';
      }

      document.getElementById('mDuration').textContent = `${meta.duration_sec.toFixed(2)}s`;
      document.getElementById('mIterations').textContent = `${meta.iterations} iterasi | ${meta.extra.evaluations || '-'} eval`;

      const bInit = document.getElementById('badgeInit');
      bInit.className = 'badge ' + (init.feasible ? 'badge-feasible' : 'badge-infeasible');
      bInit.textContent = `Obj: ${init.objective.toFixed(1)} | ${init.feasible ? 'Feasible' : 'Infeasible'}`;

      const bFin = document.getElementById('badgeFinal');
      bFin.className = 'badge ' + (fin.feasible ? 'badge-feasible' : 'badge-infeasible');
      bFin.textContent = `Obj: ${fin.objective.toFixed(1)} | ${fin.feasible ? 'Feasible' : 'Infeasible'}`;

      // Truck Tabs
      const tabs = document.getElementById('truckTabs');
      tabs.innerHTML = '<span style="font-size:0.8rem; font-weight:700; color:var(--text-muted); margin-right:6px;">Pilih Truk:</span>';
      fin.trucks.forEach((t, idx) => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn' + (idx === selectedTruckIdx ? ' active' : '');
        btn.textContent = `Truk ${t.id} (${t.value.toFixed(0)} pts, ${t.current_weight}/${t.max_capacity} kg)`;
        btn.onclick = () => {
          selectedTruckIdx = idx;
          updateUI();
        };
        tabs.appendChild(btn);
      });

      if (selectedTruckIdx >= fin.trucks.length) selectedTruckIdx = 0;
      const curTruck = fin.trucks[selectedTruckIdx];

      // Render 3D
      const initPkgs = (init.inside_packages || []).filter(p => p.truck === selectedTruckIdx);
      const finPkgs = (fin.inside_packages || []).filter(p => p.truck === selectedTruckIdx);
      renderTruckToViewer(sceneInit, curTruck, initPkgs);
      renderTruckToViewer(sceneFinal, curTruck, finPkgs);

      // Outside Packages
      const outGrid = document.getElementById('outsideGrid');
      outGrid.innerHTML = '';
      document.getElementById('outsideCountLabel').textContent = `${fin.outside_packages.length} paket`;
      fin.outside_packages.forEach(p => {
        const chip = document.createElement('div');
        chip.className = 'pkg-chip' + (p.is_fragile ? ' fragile' : '');
        chip.innerHTML = `
          <div class="pkg-chip-head">
            <span>${p.id}</span>
            <span>${p.is_fragile ? '⚠️' : ''}</span>
          </div>
          <div style="color:var(--text-muted); font-size:0.7rem;">Nilai: ${p.value} | Berat: ${p.weight}</div>
          <div style="color:var(--text-muted); font-size:0.7rem;">Dims: ${p.dims.join('x')} | ETA: ${p.eta}h</div>
        `;
        outGrid.appendChild(chip);
      });

      // Update plot image
      const plotImg = document.getElementById('plotImage');
      plotImg.src = `/api/plot?path=${encodeURIComponent(document.getElementById('runSelect').value)}&t=${Date.now()}`;
    }

    window.addEventListener('DOMContentLoaded', loadRunsList);
  </script>
</body>
</html>
"""


class VisualizerHandler(BaseHTTPRequestHandler):
    output_dirs: list[Path] = [REPO_ROOT / "output", REPO_ROOT / "src/tests/fixtures"]

    def log_message(self, format, *args):
        pass  # Suppress default request logging to keep console clean

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        if parsed.path == "/api/runs":
            runs = find_all_runs(self.output_dirs)
            self._send_json(runs)
            return

        if parsed.path == "/api/run":
            rel_path = qs.get("path", [""])[0]
            try:
                data = load_run_details(rel_path)
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if parsed.path == "/api/plot":
            rel_path = qs.get("path", [""])[0]
            ptype = qs.get("type", ["auto"])[0]
            try:
                img_bytes = render_plot_image_bytes(rel_path, ptype)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(img_bytes)))
                self.end_headers()
                self.wfile.write(img_bytes)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mejiro Express — Visualizer Web Application")
    parser.add_argument("path", nargs="?", default="output", help="Folder output atau file JSON spesifik")
    parser.add_argument("--port", type=int, default=8501, help="Port server HTTP (default: 8501)")
    parser.add_argument("--no-browser", action="store_true", help="Jangan buka browser otomatis")
    parser.add_argument("--export-html", help="Simpan standalone dashboard ke file HTML")
    args = parser.parse_args(argv)

    target_path = Path(args.path)
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path

    if args.export_html:
        out_p = Path(args.export_html)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(HTML_TEMPLATE, encoding="utf-8")
        print(f"HTML viewer exported to: {out_p}")
        return

    dirs = [target_path] if target_path.is_dir() else [target_path.parent]
    dirs.append(REPO_ROOT / "src/tests/fixtures")
    VisualizerHandler.output_dirs = dirs

    server = ThreadingHTTPServer(("127.0.0.1", args.port), VisualizerHandler)
    url = f"http://127.0.0.1:{args.port}"
    print(f"=== Mejiro Express Visualizer ===")
    print(f"Server berjalan di: {url}")
    print("Tekan Ctrl+C untuk menghentikan server.")

    if not args.no_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
