"""Small dependency-free local web dashboard."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from config import DATABASE_FILE
from database.database import NoiseDatabase

PAGE = """<!doctype html><meta charset=utf-8><title>Noise Monitor</title>
<style>body{font:16px system-ui;max-width:960px;margin:3rem auto;background:#111;color:#eee}canvas{width:100%;height:260px;background:#191919}table{width:100%;border-collapse:collapse}td,th{padding:.5rem;text-align:left;border-bottom:1px solid #333}</style>
<h1>Noise Monitor</h1><p id=latest>Waiting for measurements…</p><canvas id=chart width=960 height=260></canvas><h2>Recent frames</h2><table><thead><tr><th>Time (UTC)</th><th>RMS</th><th>Peak</th><th>Dominant Hz</th><th>Centroid Hz</th></tr></thead><tbody></tbody></table>
<script>const c=document.querySelector('canvas'),x=c.getContext('2d'),b=document.querySelector('tbody'),l=document.querySelector('#latest');
async function refresh(){let d=await (await fetch('/api/frames')).json(), last=d.at(-1);l.textContent=last?`Latest RMS ${last.rms.toFixed(4)} — peak ${last.peak.toFixed(4)}`:'No data yet';b.innerHTML=d.slice().reverse().map(f=>`<tr><td>${f.recorded_at}</td><td>${f.rms.toFixed(4)}</td><td>${f.peak.toFixed(4)}</td><td>${f.dominant_frequency.toFixed(0)}</td><td>${f.spectral_centroid.toFixed(0)}</td></tr>`).join('');x.clearRect(0,0,c.width,c.height);if(!d.length)return;let m=Math.max(...d.map(f=>f.rms),.01);x.strokeStyle='#58d68d';x.beginPath();d.forEach((f,i)=>{let px=i*c.width/Math.max(d.length-1,1),py=c.height-(f.rms/m)*(c.height-12)-6;i?x.lineTo(px,py):x.moveTo(px,py)});x.stroke()}refresh();setInterval(refresh,5000)</script>"""


def serve(host: str = "0.0.0.0", port: int = 8080) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/api/frames":
                with NoiseDatabase(DATABASE_FILE) as database:
                    body = json.dumps(database.recent_frames()).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body)
            elif self.path == "/":
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(PAGE.encode())
            else:
                self.send_error(404)
        def log_message(self, format, *args):
            return
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Dashboard listening at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
