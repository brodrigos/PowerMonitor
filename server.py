"""
PowerMonitor Pro - Servidor Web
Roda a aplicaçãocomo servidor web acessível remotamente
"""

import http.server
import socketserver
import json
import os
import sys
import threading

# Adicionar caminho do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.power_monitor import PowerMonitor


class PowerMonitorHandler(http.server.BaseHTTPRequestHandler):
    directory = os.path.dirname(os.path.abspath(__file__))

    def do_GET(self):
        if self.path == '/api/stats':
            return self.handle_stats()
        elif self.path == '/api/history':
            return self.handle_history()
        elif self.path == '/api/processes':
            return self.handle_processes()
        elif self.path == '/':
            return self.handle_index()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def handle_stats(self):
        monitor = PowerMonitor({
            'sample_interval': 5,
            'storage_file': os.path.join(self.directory, 'data', 'consumption_history.json')
        })
        monitor._load_history()
        stats = monitor.get_statistics()

        # Return defaults instead of None if no history
        if stats is None:
            stats = {
                'total_samples': 0,
                'avg_power_watts': 0,
                'max_power_watts': 0,
                'min_power_watts': 0,
                'avg_cpu_percent': 0,
                'avg_gpu_percent': 0,
                'avg_ram_percent': 0,
                'current_power_watts': 0,
                'total_energy_kwh': 0
            }

        self._send_json(stats)

    def handle_history(self):
        monitor = PowerMonitor({
            'sample_interval': 5,
            'storage_file': os.path.join(self.directory, 'data', 'consumption_history.json')
        })
        monitor._load_history()
        # Return empty array instead of None
        self._send_json(monitor.history if monitor.history else [])

    def handle_processes(self):
        monitor = PowerMonitor({
            'sample_interval': 5,
            'storage_file': os.path.join(self.directory, 'data', 'consumption_history.json')
        })
        processes = monitor.get_process_list(10)
        self._send_json(processes)

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

    def handle_index(self):
        try:
            html_path = os.path.join(self.directory, 'index.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'index.html not found')

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


class PowerMonitorServer:
    def __init__(self, host='0.0.0.0', port=9090):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        # Allow port reuse
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer((self.host, self.port), PowerMonitorHandler)
        print(f"PowerMonitor Pro is running on http://{self.host}:{self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='PowerMonitor Pro Server')
    parser.add_argument('--port', type=int, default=9090, help='Server port')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host')
    args = parser.parse_args()

    server = PowerMonitorServer(args.host, args.port)
    server.start()
    print(f"Access the app at: http://{args.host}:{args.port}")

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
