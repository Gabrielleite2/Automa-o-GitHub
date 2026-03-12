import json
import os
from datetime import datetime

LOG_FILE = os.path.join('.tmp', 'automation_logs.jsonl')
OUTPUT_HTML = 'log_viewer.html'

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation Logs</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-color: #f8fafc;
            --border-color: rgba(255, 255, 255, 0.1);
            
            --success: #10b981;
            --info: #3b82f6;
            --warning: #f59e0b;
            --error: #ef4444;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            min-height: 100vh;
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.2) 0, transparent 50%), 
                radial-gradient(at 100% 0%, hsla(339,49%,30%,0.2) 0, transparent 50%);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            background: linear-gradient(to right, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .glass-panel {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }

        .toolbar {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        input, select, button {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            outline: none;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            border-color: #60a5fa;
            box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
        }

        input { flex-grow: 1; }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-bottom: 1rem;
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        th {
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }

        tr {
            transition: background-color 0.2s;
        }

        tr:hover {
            background-color: rgba(255, 255, 255, 0.03);
        }

        .level-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .level-INFO { background: rgba(59, 130, 246, 0.1); color: var(--info); border: 1px solid rgba(59, 130, 246, 0.2); }
        .level-SUCCESS { background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }
        .level-WARNING { background: rgba(245, 158, 11, 0.1); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }
        .level-ERROR { background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }

        .time { color: #94a3b8; font-family: monospace; }
        .script-name { color: #cbd5e1; font-weight: 500; }
        .message { color: #f1f5f9; }

        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #94a3b8;
        }

    </style>
</head>
<body>
    <div class="container">
        <h1>Central Automation Logs</h1>
        
        <div class="glass-panel">
            <div class="toolbar">
                <input type="text" id="searchInput" placeholder="Search logs..." onkeyup="filterLogs()">
                <select id="levelFilter" onchange="filterLogs()">
                    <option value="">All Levels</option>
                    <option value="INFO">Info</option>
                    <option value="SUCCESS">Success</option>
                    <option value="WARNING">Warning</option>
                    <option value="ERROR">Error</option>
                </select>
            </div>

            <div style="overflow-x: auto;">
                <table id="logsTable">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Level</th>
                            <th>Script</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody id="logsBody">
                        <!-- LOGS_INJECTED_HERE -->
                    </tbody>
                </table>
            </div>
            
            <div id="emptyState" class="empty-state" style="display: none;">
                No logs found matching your criteria.
            </div>
        </div>
    </div>

    <script>
        // Log data injected via Python
        const logs = LOG_DATA_INJECTED_HERE;

        function renderLogs(data) {
            const tbody = document.getElementById('logsBody');
            const emptyState = document.getElementById('emptyState');
            const table = document.getElementById('logsTable');
            
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                emptyState.style.display = 'block';
                table.style.display = 'none';
                return;
            }

            emptyState.style.display = 'none';
            table.style.display = 'table';

            data.forEach(log => {
                const tr = document.createElement('tr');
                
                const d = new Date(log.timestamp);
                const timeStr = d.toLocaleString();

                tr.innerHTML = `
                    <td class="time">${timeStr}</td>
                    <td><span class="level-badge level-${log.level}">${log.level}</span></td>
                    <td class="script-name">${log.script}</td>
                    <td class="message">${log.message}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function filterLogs() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const levelFilter = document.getElementById('levelFilter').value;

            const filtered = logs.filter(log => {
                const matchesSearch = (log.message || '').toLowerCase().includes(searchTerm) || 
                                     (log.script || '').toLowerCase().includes(searchTerm);
                const matchesLevel = levelFilter === '' || log.level === levelFilter;
                
                return matchesSearch && matchesLevel;
            });

            renderLogs(filtered);
        }

        // Initial render (reverse to show newest first)
        renderLogs(logs.reverse());
    </script>
</body>
</html>
"""

def generate_viewer():
    print(f"Reading logs from {LOG_FILE}...")
    logs = []
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    else:
        print("No logs found yet. Creating an empty viewer.")

    # Inject JSON representation of logs into the HTML template
    html_content = HTML_TEMPLATE.replace(
        'LOG_DATA_INJECTED_HERE',
        json.dumps(logs)
    )

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSuccess! Log viewer generated at: {os.path.abspath(OUTPUT_HTML)}")
    print(f"Open this file in your browser to view the automation logs.")

if __name__ == "__main__":
    generate_viewer()
