"""
PowerMonitor Pro - Servidor Web
Roda a aplicaçãocomo servidor web acessível remotamente
Coleta dados em tempo real via thread de background
"""

import http.server
import socketserver
import json
import os
import sys
import threading
import time

# Adicionar caminho do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.power_monitor import PowerMonitor


# Global monitor instance — single collector running in background
_monitor = None
_monitor_lock = threading.Lock()
_current_stats = {}
_current_processes = []


def _get_storage_file():
    """Retorna o caminho do arquivo de armazenamento."""
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data', 'consumption_history.json'
    )


def _monitor_thread(storage_file, interval=3):
    """Thread de coleta contínua que roda em background."""
    global _monitor, _current_stats, _current_processes
    _monitor = PowerMonitor({
        'sample_interval': interval,
        'storage_file': storage_file
    })
    _monitor.start()

    while _monitor.running:
        try:
            sample = _monitor.collect_sample()
            # Calcular stats a partir da amostra atual
            with _monitor_lock:
                stats = {
                    'total_samples': len(_monitor.history),
                    'current_power_watts': round(
                        sample['cpu_power']['cpu_power_watts'] + sample['gpu_power']['gpu_power'], 2
                    ),
                    'current_cpu_percent': sample['cpu_power']['cpu_percent'],
                    'current_gpu_percent': sample['gpu_power']['gpu_load'],
                    'current_ram_percent': sample['ram_usage']['ram_percent'],
                    'cpu_temp': sample['cpu_power']['cpu_temp'],
                    'max_power_watts': 0,
                    'avg_power_watts': 0,
                    'min_power_watts': 0,
                    'avg_cpu_percent': 0,
                    'avg_gpu_percent': 0,
                    'avg_ram_percent': 0,
                    'total_energy_kwh': 0,
                    'timestamp': sample['timestamp']
                }
                # Calcular stats acumulados
                if _monitor.history:
                    powers = [r['total_power_watts'] for r in _monitor.history]
                    cpus = [r['cpu_percent'] for r in _monitor.history]
                    gpus = [r['gpu_percent'] for r in _monitor.history]
                    rams = [r['ram_percent'] for r in _monitor.history]
                    stats['max_power_watts'] = max(powers)
                    stats['min_power_watts'] = min(powers)
                    stats['avg_power_watts'] = round(sum(powers) / len(powers), 2)
                    stats['avg_cpu_percent'] = round(sum(cpus) / len(cpus), 2)
                    stats['avg_gpu_percent'] = round(sum(gpus) / len(gpus), 2)
                    stats['avg_ram_percent'] = round(sum(rams) / len(rams), 2)
                    stats['total_energy_kwh'] = round(
                        (sum(powers) * _monitor.config['sample_interval']) / 3600000, 6
                    )
                _current_stats = stats
                _current_processes = _monitor.get_process_list(10)
            time.sleep(interval)
        except KeyboardInterrupt:
            _monitor.stop()


def get_monitor():
    """Retorna o monitor singleton, iniciando se necessário."""
    global _monitor
    if _monitor is None:
        storage_file = _get_storage_file()
        _monitor_thread(storage_file, interval=3)
    return _monitor


class PowerMonitorHandler(http.server.BaseHTTPRequestHandler):
    directory = os.path.dirname(os.path.abspath(__file__))

    def do_GET(self):
        if self.path == '/api/stats':
            return self.handle_stats()
        elif self.path == '/api/history':
            return self.handle_history()
        elif self.path == '/api/processes':
            return self.handle_processes()
        elif self.path == '/api/collect':
            return self.handle_collect()
        elif self.path == '/':
            return self.handle_index()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def handle_stats(self):
        """Retorna estatísticas em tempo real."""
        # Inicia o monitor se ainda não estiver rodando
        get_monitor()
        with _monitor_lock:
            stats = dict(_current_stats) if _current_stats else {}

        # Return defaults instead of empty
        if not stats:
            stats = {
                'total_samples': 0,
                'current_power_watts': 0,
                'current_cpu_percent': 0,
                'current_gpu_percent': 0,
                'current_ram_percent': 0,
                'cpu_temp': None,
                'max_power_watts': 0,
                'avg_power_watts': 0,
                'min_power_watts': 0,
                'avg_cpu_percent': 0,
                'avg_gpu_percent': 0,
                'avg_ram_percent': 0,
                'total_energy_kwh': 0
            }

        self._send_json(stats)

    def handle_history(self):
        """Retorna histórico de amostras."""
        monitor = get_monitor()
        with _monitor_lock:
            history = list(monitor.history) if monitor.history else []
        self._send_json(history)

    def handle_processes(self):
        """Retorna lista de processos mais intensivos."""
        get_monitor()
        with _monitor_lock:
            processes = list(_current_processes)
        self._send_json(processes)

    def handle_collect(self):
        """Endpoint para forçar coleta imediata."""
        monitor = get_monitor()
        try:
            sample = monitor.run_once()
            self._send_json({
                'status': 'collected',
                'timestamp': sample['timestamp'],
                'cpu_power': sample['cpu_power']['cpu_power_watts'],
                'gpu_power': sample['gpu_power']['gpu_power'],
                'total': round(sample['cpu_power']['cpu_power_watts'] + sample['gpu_power']['gpu_power'], 2)
            })
        except Exception as e:
            self._send_json({'status': 'error', 'message': str(e)})

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
        # Start the background collector thread only if not already started
        storage_file = _get_storage_file()
        if _monitor is None:
            collector_thread = threading.Thread(
                target=_monitor_thread,
                args=(storage_file, 3),
                daemon=True
            )
            collector_thread.start()
            time.sleep(1)  # Wait for monitor to initialize

        # Start HTTP server
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer((self.host, self.port), PowerMonitorHandler)
        print(f"PowerMonitor Pro is running on http://{self.host}:{self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        global _monitor
        if _monitor:
            _monitor.stop()
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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
