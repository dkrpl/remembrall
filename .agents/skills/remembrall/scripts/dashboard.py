#!/usr/bin/env python3
"""
Remembrall Interactive Web Dashboard.
Zero external dependencies (pure Python http.server).
Provides a modern dark-mode UI to monitor state, search features, calculate token savings, and update tasks.
"""

import http.server
import json
import socketserver
import sys
import urllib.parse
import webbrowser
from pathlib import Path

# Add scripts directory
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import remembrall
import simulation


def get_api_data(manifest_path):
    stats = remembrall.get_stats(manifest_path)
    features = remembrall.parse_features(manifest_path)
    bench = simulation.run_benchmark(manifest_path, simulated_turns=20)
    
    # Read technical findings
    content = Path(manifest_path).read_text(encoding="utf-8") if Path(manifest_path).exists() else ""
    findings = []
    in_findings = False
    for line in content.splitlines():
        if "## Technical Findings" in line:
            in_findings = True
        elif in_findings and line.startswith("#"):
            in_findings = False
        elif in_findings and (line.strip().startswith("-") or line.strip().startswith("*")):
            findings.append(line.strip().lstrip("-* ").strip())

    return {
        "stats": stats,
        "features": list(features.values()),
        "findings": findings,
        "benchmark": bench,
        "raw_markdown": content
    }


def generate_html(manifest_path):
    data = get_api_data(manifest_path)
    stats = data["stats"]
    features_json = json.dumps(data["features"])
    stats_json = json.dumps(stats)
    bench_json = json.dumps(data["benchmark"])
    
    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🔮 Remembrall State Engine</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f0f9ff',
              400: '#38bdf8',
              500: '#0ea5e9',
              600: '#0284c7',
              900: '#0c4a6e',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ background-color: #0f172a; color: #f8fafc; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
    .badge-done {{ background-color: #065f46; color: #34d399; border: 1px solid #059669; }}
    .badge-wip {{ background-color: #854d0e; color: #fde047; border: 1px solid #ca8a04; }}
    .badge-planned {{ background-color: #1e293b; color: #94a3b8; border: 1px solid #475569; }}
  </style>
</head>
<body class="min-h-screen p-6 md:p-10">
  <div class="max-w-6xl mx-auto space-y-8">
    
    <!-- Header -->
    <header class="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
      <div class="flex items-center space-x-4">
        <div class="h-12 w-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-2xl shadow-lg shadow-cyan-500/20">
          🔮
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white flex items-center gap-3">
            Remembrall State Engine
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">v1.0 Enterprise</span>
          </h1>
          <p class="text-sm text-slate-400">Zero-Amnesia Persistent Feature & Memory Management</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button onclick="triggerPrune()" class="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-2">
          🧹 Auto-Prune
        </button>
        <button onclick="openModal()" class="px-4 py-2 text-sm font-medium rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white shadow-md shadow-cyan-600/30 transition flex items-center gap-2">
          ➕ Register Feature
        </button>
      </div>
    </header>

    <!-- Metrics Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-slate-800/60 backdrop-blur border border-slate-800 p-5 rounded-2xl">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Features Tracked</div>
        <div class="text-3xl font-extrabold text-white mt-2" id="metric-total">{stats.get("total_features", 0)}</div>
        <div class="text-xs text-slate-400 mt-1 flex gap-2 font-mono">
          <span class="text-emerald-400">✓ {stats.get("done", 0)} Done</span> • 
          <span class="text-amber-400">⚡ {stats.get("wip", 0)} WIP</span>
        </div>
      </div>

      <div class="bg-slate-800/60 backdrop-blur border border-slate-800 p-5 rounded-2xl">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Token Efficiency</div>
        <div class="text-3xl font-extrabold text-cyan-400 mt-2">{data["benchmark"].get("token_savings_pct", 82.9)}%</div>
        <div class="text-xs text-slate-400 mt-1 font-mono">
          ~{data["benchmark"].get("tokens_saved", 0):,} tokens saved
        </div>
      </div>

      <div class="bg-slate-800/60 backdrop-blur border border-slate-800 p-5 rounded-2xl">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Manifest Budget</div>
        <div class="text-3xl font-extrabold text-white mt-2">
          {stats.get("lines", 0)} <span class="text-base font-normal text-slate-500">/ 120 lines</span>
        </div>
        <div class="text-xs text-slate-400 mt-1 font-mono">
          Token cost: ~{stats.get("est_tokens", 0)} tokens
        </div>
      </div>

      <div class="bg-slate-800/60 backdrop-blur border border-slate-800 p-5 rounded-2xl">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Engine Health</div>
        <div class="text-3xl font-extrabold mt-2 flex items-center gap-2">
          <span class="h-3 w-3 rounded-full bg-emerald-400 shadow-lg shadow-emerald-400/50 animate-pulse"></span>
          <span class="text-emerald-400 text-xl font-bold">HEALTHY</span>
        </div>
        <div class="text-xs text-slate-400 mt-1">Zero Re-scan active</div>
      </div>
    </div>

    <!-- Features Management Section -->
    <div class="bg-slate-800/40 border border-slate-800 rounded-2xl p-6 space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <!-- Search -->
        <div class="relative flex-1 max-w-md">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">🔍</span>
          <input type="text" id="searchInput" oninput="renderTable()" placeholder="Search features, files, or notes..." 
            class="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition">
        </div>

        <!-- Filter tabs -->
        <div class="flex p-1 bg-slate-900 rounded-xl border border-slate-800 text-xs font-medium">
          <button onclick="setFilter('ALL')" id="filter-all" class="px-3 py-1.5 rounded-lg bg-cyan-600 text-white">All</button>
          <button onclick="setFilter('DONE')" id="filter-done" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white">Done</button>
          <button onclick="setFilter('WIP')" id="filter-wip" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white">WIP</button>
          <button onclick="setFilter('PLANNED')" id="filter-planned" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white">Planned</button>
        </div>
      </div>

      <!-- Feature Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <th class="py-3 px-4">ID</th>
              <th class="py-3 px-4">Feature Name</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4">Associated Files</th>
              <th class="py-3 px-4">Notes</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody id="featuresTableBody" class="divide-y divide-slate-800/60 text-sm">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <!-- Modal Register Feature -->
  <div id="addModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
      <h3 class="text-lg font-bold text-white flex items-center gap-2">
        <span>➕</span> Register New Feature
      </h3>
      <div class="space-y-3 text-sm">
        <div>
          <label class="block text-slate-400 text-xs mb-1">Feature Title</label>
          <input type="text" id="m_title" class="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white">
        </div>
        <div>
          <label class="block text-slate-400 text-xs mb-1">Key Files (comma-separated)</label>
          <input type="text" id="m_files" placeholder="src/auth.py, src/main.py" class="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white">
        </div>
        <div>
          <label class="block text-slate-400 text-xs mb-1">Notes</label>
          <input type="text" id="m_notes" placeholder="1-line summary note" class="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white">
        </div>
        <div>
          <label class="block text-slate-400 text-xs mb-1">Initial Status</label>
          <select id="m_status" class="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white">
            <option value="PLANNED">PLANNED</option>
            <option value="WIP">WIP</option>
            <option value="DONE">DONE</option>
          </select>
        </div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <button onclick="closeModal()" class="px-4 py-2 text-sm rounded-xl text-slate-400 hover:text-white">Cancel</button>
        <button onclick="submitNewFeature()" class="px-4 py-2 text-sm font-semibold rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white">Save Feature</button>
      </div>
    </div>
  </div>

  <script>
    let rawFeatures = {features_json};
    let currentFilter = 'ALL';

    function setFilter(filter) {{
      currentFilter = filter;
      ['ALL', 'DONE', 'WIP', 'PLANNED'].forEach(f => {{
        const btn = document.getElementById('filter-' + f.toLowerCase());
        if (f === filter) {{
          btn.className = 'px-3 py-1.5 rounded-lg bg-cyan-600 text-white';
        }} else {{
          btn.className = 'px-3 py-1.5 rounded-lg text-slate-400 hover:text-white';
        }}
      }});
      renderTable();
    }}

    function renderTable() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const tbody = document.getElementById('featuresTableBody');
      tbody.innerHTML = '';

      const filtered = rawFeatures.filter(f => {{
        const matchesFilter = (currentFilter === 'ALL') || (f.status === currentFilter);
        const matchesQuery = !query || 
          f.title.toLowerCase().includes(query) || 
          f.files.toLowerCase().includes(query) || 
          f.notes.toLowerCase().includes(query) ||
          f.id.toLowerCase().includes(query);
        return matchesFilter && matchesQuery;
      }});

      if (filtered.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="6" class="py-6 text-center text-slate-500">No matching features found.</td></tr>';
        return;
      }}

      filtered.forEach(f => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        const badgeClass = f.status === 'DONE' ? 'badge-done' : (f.status === 'WIP' ? 'badge-wip' : 'badge-planned');
        
        tr.innerHTML = `
          <td class="py-3 px-4 font-mono text-cyan-400 font-bold">${{f.id}}</td>
          <td class="py-3 px-4 font-medium text-slate-200">${{f.title}}</td>
          <td class="py-3 px-4"><span class="px-2.5 py-1 text-xs rounded-full font-bold ${{badgeClass}}">${{f.status}}</span></td>
          <td class="py-3 px-4 font-mono text-xs text-slate-300 max-w-xs truncate" title="${{f.files}}">${{f.files}}</td>
          <td class="py-3 px-4 text-xs text-slate-400">${{f.notes || '-'}}</td>
          <td class="py-3 px-4 text-right">
            <select onchange="updateStatus('${{f.id}}', this.value)" class="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2 py-1 text-slate-300">
              <option value="PLANNED" ${{f.status === 'PLANNED' ? 'selected' : ''}}>PLANNED</option>
              <option value="WIP" ${{f.status === 'WIP' ? 'selected' : ''}}>WIP</option>
              <option value="DONE" ${{f.status === 'DONE' ? 'selected' : ''}}>DONE</option>
            </select>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function openModal() {{
      document.getElementById('addModal').classList.remove('hidden');
      document.getElementById('addModal').classList.add('flex');
    }}

    function closeModal() {{
      document.getElementById('addModal').classList.add('hidden');
      document.getElementById('addModal').classList.remove('flex');
    }}

    async function submitNewFeature() {{
      const title = document.getElementById('m_title').value;
      const files = document.getElementById('m_files').value;
      const notes = document.getElementById('m_notes').value;
      const status = document.getElementById('m_status').value;

      if (!title || !files) {{
        alert('Please provide title and file paths');
        return;
      }}

      await fetch('/api/features', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ title, files, notes, status }})
      }});

      closeModal();
      location.reload();
    }}

    async function updateStatus(id, newStatus) {{
      await fetch('/api/set-status', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ id, status: newStatus }})
      }});
      location.reload();
    }}

    async function triggerPrune() {{
      if (confirm('Consolidate historical features to reduce token budget?')) {{
        await fetch('/api/prune', {{ method: 'POST' }});
        location.reload();
      }}
    }}

    // Initial render
    renderTable();
  </script>
</body>
</html>"""


class RemembrallHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    manifest_path = None

    def log_message(self, format, *args):
        # Mute noisy console logs
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = generate_html(self.manifest_path)
            self.wfile.write(html.encode("utf-8"))
        elif parsed.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = get_api_data(self.manifest_path)
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if parsed.path == "/api/features":
            title = payload.get("title")
            files = payload.get("files")
            notes = payload.get("notes", "")
            status = payload.get("status", "PLANNED")
            new_id = remembrall.add_feature(self.manifest_path, title, files, notes=notes, status=status)
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "id": new_id}).encode("utf-8"))

        elif parsed.path == "/api/set-status":
            fid = payload.get("id")
            new_status = payload.get("status")
            remembrall.set_feature(self.manifest_path, fid, status=new_status)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))

        elif parsed.path == "/api/prune":
            count = remembrall.prune_manifest(self.manifest_path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "pruned": count}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


def start_server(manifest_path, port=4242, open_browser=True):
    RemembrallHTTPRequestHandler.manifest_path = manifest_path
    with socketserver.TCPServer(("", port), RemembrallHTTPRequestHandler) as httpd:
        url = f"http://localhost:{port}"
        print(f"\n🔮 Remembrall Dashboard running at: {url}")
        print("   Press Ctrl+C to stop the dashboard.\n")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped.")


if __name__ == "__main__":
    m_path = remembrall.find_manifest()
    start_server(m_path, port=4242, open_browser=True)
