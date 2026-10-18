from __future__ import annotations

import argparse
import io
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

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
  <title>Mejiro Express</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {
      --bg: #f4f6fa;
      --surface: #ffffff;
      --border: #d5dbe6;
      --primary: #0033a0;
      --text: #0a1f44;
      --muted: #5f6b7e;
      --good: #1b7f4b;
      --bad: #c8102e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      font-size: 14px;
    }
    header {
      background: var(--primary);
      color: #fff;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    header h1 { font-size: 1.1rem; font-weight: 600; white-space: nowrap; }
    header label { margin-left: auto; font-size: 0.85rem; }
    header button {
      padding: 6px 12px;
      border: 1px solid rgba(255, 255, 255, 0.6);
      border-radius: 4px;
      background: transparent;
      color: #fff;
      font: inherit;
      cursor: pointer;
      white-space: nowrap;
    }
    header button:disabled { opacity: 0.4; cursor: default; }
    select {
      width: min(560px, 55vw);
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 4px;
      font: inherit;
      color: var(--text);
      background: #fff;
    }
    main {
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    h2 { font-size: 0.95rem; font-weight: 600; }
    .run-title { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
    .run-title h2 { font-size: 1.2rem; }
    .run-title span { color: var(--muted); font-size: 0.85rem; }
    .run-title span.error { color: var(--bad); }
    main.loading > .summary, main.loading > .views, main.loading > .plot { opacity: 0.45; }
    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
    }
    .metric {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 8px 12px;
    }
    .metric span { display: block; font-size: 0.75rem; color: var(--muted); }
    .metric strong { font-size: 1rem; font-weight: 600; word-break: break-word; }
    .metric.bad strong { color: var(--bad); }
    .metric.good strong { color: var(--good); }
    .tabs { display: flex; gap: 6px; align-items: center; }
    .tabs:empty { display: none; }
    .tabs button {
      padding: 5px 12px;
      border: 1px solid var(--border);
      border-radius: 4px;
      background: var(--surface);
      color: var(--text);
      font: inherit;
      cursor: pointer;
    }
    .tabs button.active { background: var(--primary); border-color: var(--primary); color: #fff; }
    .views { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 1000px) { .views { grid-template-columns: 1fr; } }
    .view {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      overflow: hidden;
    }
    .view-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-bottom: 1px solid var(--border);
    }
    .badge { font-size: 0.8rem; color: var(--muted); }
    .badge.good { color: var(--good); }
    .badge.bad { color: var(--bad); }
    .canvas { position: relative; height: 440px; background: #eef2f8; }
    .tooltip {
      position: absolute;
      display: none;
      pointer-events: none;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 6px 10px;
      font-size: 0.8rem;
      z-index: 5;
      white-space: nowrap;
    }
    .view-foot { padding: 8px 12px; border-top: 1px solid var(--border); font-size: 0.85rem; }
    .view-foot p { color: var(--muted); }
    .outside { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; max-height: 84px; overflow-y: auto; }
    .outside b { font-weight: 600; margin-right: 4px; }
    .chip {
      padding: 1px 7px;
      border: 1px solid var(--border);
      border-radius: 3px;
      font-size: 0.78rem;
      background: var(--bg);
    }
    .chip.fragile { border-color: var(--bad); color: var(--bad); }
    .plot {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: center;
    }
    .plot h2 { align-self: flex-start; }
    .plot img { max-width: 100%; height: auto; }
    .legend { color: var(--muted); font-size: 0.8rem; }
  </style>
</head>
<body>
  <header>
    <h1>Mejiro Express</h1>
    <label for="runSelect">Run</label>
    <button type="button" id="prevRun">Sebelumnya</button>
    <select id="runSelect"></select>
    <button type="button" id="nextRun">Berikutnya</button>
  </header>

  <main>
    <section class="run-title"><h2 id="runTitle"></h2><span id="runMeta"></span></section>
    <section class="summary" id="summary"></section>
    <div class="tabs" id="truckTabs"></div>

    <section class="views">
      <div class="view">
        <div class="view-head"><h2>State awal</h2><span class="badge" id="badgeInit"></span></div>
        <div class="canvas" id="canvasInit"><div class="tooltip" id="tipInit"></div></div>
        <div class="view-foot"><p id="infoInit"></p><div class="outside" id="outsideInit"></div></div>
      </div>
      <div class="view">
        <div class="view-head"><h2>State akhir</h2><span class="badge" id="badgeFinal"></span></div>
        <div class="canvas" id="canvasFinal"><div class="tooltip" id="tipFinal"></div></div>
        <div class="view-foot"><p id="infoFinal"></p><div class="outside" id="outsideFinal"></div></div>
      </div>
    </section>

    <section class="plot">
      <h2>Grafik hasil pencarian</h2>
      <img id="plotImage" alt="Grafik hasil pencarian">
    </section>

    <p class="legend">Merah: paket fragile. Drag kiri untuk memutar, scroll untuk zoom, drag kanan untuk menggeser.</p>
  </main>

  <script>
    const PALETTE = [0x0033a0, 0xf2b01e, 0x4da6e8, 0x0a1f44, 0xe8702a, 0x8a97a8, 0x1b998b, 0x6c8ebf];
    const FRAGILE_COLOR = 0xc8102e;
    let currentRun = null;
    let selectedTruck = 0;
    let runs = [];
    let requestId = 0;
    let plotTimer = null;
    const PLOT_DELAY_MS = 150;
    const viewInit = createViewer('canvasInit', 'tipInit');
    const viewFinal = createViewer('canvasFinal', 'tipFinal');

    function el(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function createViewer(containerId, tooltipId) {
      const container = document.getElementById(containerId);
      const tooltip = document.getElementById(tooltipId);
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      container.appendChild(renderer.domElement);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      scene.add(new THREE.AmbientLight(0xffffff, 0.8));
      const light = new THREE.DirectionalLight(0xffffff, 0.6);
      light.position.set(20, 40, 30);
      scene.add(light);

      const group = new THREE.Group();
      scene.add(group);
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      container.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const hit = raycaster.intersectObjects(group.children, true).find(h => h.object.userData.pkg);
        if (!hit) {
          tooltip.style.display = 'none';
          return;
        }
        const p = hit.object.userData.pkg;
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
        tooltip.style.top = (e.clientY - rect.top + 14) + 'px';
        tooltip.replaceChildren(
          el('strong', '', p.id + (p.is_fragile ? ' (fragile)' : '')),
          el('div', '', `Value ${p.value}, berat ${p.weight}, ETA ${p.eta}`),
          el('div', '', `Dimensi ${p.dims.join(' x ')}`),
          el('div', '', `Posisi (${p.x}, ${p.y}, ${p.z})`)
        );
      });
      container.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });

      window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      });

      (function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
      })();

      return { camera, controls, group };
    }

    function renderTruck(view, truck, packages) {
      const group = view.group;
      while (group.children.length > 0) group.remove(group.children[0]);
      if (!truck) return;
      const { w, l, h } = truck.dimensions;

      const frame = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)),
        new THREE.LineBasicMaterial({ color: 0x334155 })
      );
      frame.position.set(w / 2, h / 2, l / 2);
      group.add(frame);

      const grid = new THREE.GridHelper(Math.max(w, l), Math.max(w, l), 0xb6c0d0, 0xd5dbe6);
      grid.position.set(w / 2, 0, l / 2);
      group.add(grid);

      packages.forEach((p, i) => {
        const [dx, dy, dz] = p.dims;
        const geo = new THREE.BoxGeometry(dx, dz, dy);
        const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
          color: p.is_fragile ? FRAGILE_COLOR : PALETTE[i % PALETTE.length],
          roughness: 0.5,
          transparent: true,
          opacity: 0.92
        }));
        mesh.position.set(p.x + dx / 2, p.z + dz / 2, p.y + dy / 2);
        mesh.userData.pkg = p;
        mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x0a1f44 })));
        group.add(mesh);
      });

      view.camera.position.set(w * 1.6, h * 2.2, l * 2.4);
      view.controls.target.set(w / 2, h / 2, l / 2);
      view.camera.lookAt(w / 2, h / 2, l / 2);
    }

    function extraRows(meta) {
      const e = meta.extra || {};
      const rows = [];
      if (e.max_sideways !== undefined) rows.push(['Sideways move terpakai', `${e.sideways_used} / ${e.max_sideways}`]);
      if (e.restarts !== undefined) {
        rows.push(['Restart', `${e.restarts} / ${e.max_restart}`]);
        rows.push(['Iterasi per restart', (e.iterations_per_restart || []).join(', ')]);
      }
      if (e.stuck_count !== undefined) rows.push(['Stuck di local optima', e.stuck_count]);
      if (e.population_size !== undefined) {
        rows.push(['Populasi', e.population_size]);
        rows.push(['Generasi', e.generations]);
      }
      return rows;
    }

    function renderSummary(meta) {
      const violations = Object.entries(meta.final_violations || {})
        .filter(([, v]) => v > 0).map(([k, v]) => `${k} ${v}`).join(', ');
      const rows = [
        ['Algoritma', meta.label || meta.algorithm, ''],
        ['Objective awal', meta.initial_objective.toFixed(1), ''],
        ['Objective akhir', meta.final_objective.toFixed(1), ''],
        ['Value akhir', meta.final_value.toFixed(0), ''],
        ['Status', meta.feasible ? 'Feasible' : `Tidak feasible: ${violations}`, meta.feasible ? 'good' : 'bad'],
        ['Durasi', `${meta.duration_sec.toFixed(2)} detik`, ''],
        ['Iterasi', meta.iterations, ''],
        ...extraRows(meta).map(([k, v]) => [k, v, ''])
      ];
      document.getElementById('summary').replaceChildren(...rows.map(([label, value, cls]) => {
        const card = el('div', 'metric ' + cls);
        card.append(el('span', '', label), el('strong', '', String(value)));
        return card;
      }));
    }

    function renderState(summary, suffix, view) {
      const badge = document.getElementById('badge' + suffix);
      badge.className = 'badge ' + (summary.feasible ? 'good' : 'bad');
      badge.textContent = `Value ${summary.total_value.toFixed(0)} | ${summary.feasible ? 'Feasible' : 'Tidak feasible'}`;

      const truck = summary.trucks[selectedTruck];
      document.getElementById('info' + suffix).textContent =
        `Truk ${truck.id}: ${truck.package_count} paket, berat ${truck.current_weight} / ${truck.max_capacity}, value ${truck.value.toFixed(0)}`;

      const outside = summary.outside_packages;
      document.getElementById('outside' + suffix).replaceChildren(
        el('b', '', `Di luar truk (${outside.length}):`),
        ...outside.map(p => {
          const chip = el('span', 'chip' + (p.is_fragile ? ' fragile' : ''), p.id);
          chip.title = `Value ${p.value}, berat ${p.weight}, dimensi ${p.dims.join(' x ')}, ETA ${p.eta}`;
          return chip;
        })
      );

      renderTruck(view, truck, summary.inside_packages.filter(p => p.truck === selectedTruck));
    }

    function renderTabs(trucks) {
      const tabs = document.getElementById('truckTabs');
      tabs.replaceChildren();
      if (trucks.length < 2) return;
      trucks.forEach((t, i) => {
        const btn = el('button', i === selectedTruck ? 'active' : '', `Truk ${t.id}`);
        btn.onclick = () => { selectedTruck = i; updateUI(); };
        tabs.appendChild(btn);
      });
    }

    function updateUI() {
      if (!currentRun) return;
      const { metadata, initial_summary, final_summary } = currentRun;
      if (selectedTruck >= final_summary.trucks.length) selectedTruck = 0;
      renderSummary(metadata);
      renderTabs(final_summary.trucks);
      renderState(initial_summary, 'Init', viewInit);
      renderState(final_summary, 'Final', viewFinal);
    }

    function setLoading(on) {
      document.querySelector('main').classList.toggle('loading', on);
    }

    function showRunHeader() {
      const select = document.getElementById('runSelect');
      const run = runs[select.selectedIndex];
      document.getElementById('runTitle').textContent = `${run.label}, seed ${run.seed}`;
      const meta = document.getElementById('runMeta');
      meta.className = '';
      meta.textContent = `Folder ${run.folder} | run ${select.selectedIndex + 1} dari ${runs.length}`;
      document.getElementById('prevRun').disabled = select.selectedIndex === 0;
      document.getElementById('nextRun').disabled = select.selectedIndex === runs.length - 1;
    }

    async function loadRun(path) {
      const id = ++requestId;
      clearTimeout(plotTimer);
      showRunHeader();
      setLoading(true);
      try {
        const res = await fetch(`/api/run?path=${encodeURIComponent(path)}`);
        const data = await res.json();
        if (id !== requestId) return;
        if (data.error) throw new Error(data.error);
        currentRun = data;
        updateUI();
        const img = document.getElementById('plotImage');
        img.onload = img.onerror = () => { if (id === requestId) setLoading(false); };
        plotTimer = setTimeout(() => {
          img.src = `/api/plot?path=${encodeURIComponent(path)}&t=${Date.now()}`;
        }, PLOT_DELAY_MS);
      } catch (err) {
        if (id !== requestId) return;
        setLoading(false);
        const meta = document.getElementById('runMeta');
        meta.className = 'error';
        meta.textContent = `Gagal memuat run: ${err.message}`;
      }
    }

    async function loadRuns() {
      runs = await (await fetch('/api/runs')).json();
      const select = document.getElementById('runSelect');
      runs.forEach(r => {
        const opt = el('option', '', `[${r.folder}] ${r.label}, seed ${r.seed}`);
        opt.value = r.path;
        select.appendChild(opt);
      });
      const open = (index) => {
        select.selectedIndex = index;
        loadRun(runs[index].path);
      };
      select.addEventListener('change', () => loadRun(select.value));
      document.getElementById('prevRun').addEventListener('click', () => open(select.selectedIndex - 1));
      document.getElementById('nextRun').addEventListener('click', () => open(select.selectedIndex + 1));
      if (runs.length > 0) {
        open(0);
      } else {
        document.getElementById('runTitle').textContent = 'Tidak ada hasil run';
      }
    }

    window.addEventListener('DOMContentLoaded', loadRuns);
  </script>
</body>
</html>
"""


class VisualizerHandler(BaseHTTPRequestHandler):
    output_dirs: list[Path] = [REPO_ROOT / "output", REPO_ROOT / "src/tests/fixtures"]

    def log_message(self, format, *args):
        pass  # Suppress default request logging to keep console clean

    def do_GET(self):
        try:
            self._route()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _route(self):
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
            except (BrokenPipeError, ConnectionResetError):
                raise
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
            except (BrokenPipeError, ConnectionResetError):
                raise
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
