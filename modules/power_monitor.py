"""
PowerMonitor - Módulo de Monitoramento de Energia
Coleção informações de consumo energético do sistema
"""

import psutil
import time
from datetime import datetime
import json
import os


class PowerMonitor:
    def __init__(self, config=None):
        defaults = {
            'sample_interval': 2,  # segundos entre amostras
            'storage_file': 'data/consumption_history.json',
            'max_records': 10000
        }
        if config:
            defaults.update(config)
        self.config = defaults
        self.history = []
        self.start_time = datetime.now()
        self.running = False
        self._last_cpu_percent = None
        self._ensure_storage_dir()
        
    def _ensure_storage_dir(self):
        """Garantir que o diretório de armazenamento existe"""
        dir_path = os.path.dirname(self.config['storage_file'])
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
    def _load_history(self):
        """Carregar histórico existente"""
        try:
            if os.path.exists(self.config['storage_file']):
                with open(self.config['storage_file'], 'r') as f:
                    self.history = json.load(f)
                # Manter apenas os registros mais recentes
                if len(self.history) > self.config['max_records']:
                    self.history = self.history[-self.config['max_records']:]
        except (json.JSONDecodeError, FileNotFoundError):
            self.history = []
            
    def _save_history(self):
        """Salvar histórico no disco"""
        try:
            with open(self.config['storage_file'], 'w') as f:
                json.dump(self.history[-self.config['max_records']:], f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            
    def get_cpu_power(self):
        """Estimar consumo de energia da CPU"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self._last_cpu_percent = cpu_percent
        # Estimativa baseada na carga da CPU (simplificada)
        # Em um sistema real, você precisaria de calibração específica
        cpu_power = (cpu_percent / 100) * 100  # Watts estimados
        return {
            'cpu_percent': cpu_percent,
            'cpu_power_watts': round(cpu_power, 2),
            'cpu_temp': self.get_cpu_temperature()
        }
    
    def get_cpu_temperature(self):
        """Obter temperatura da CPU"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Pega a primeira temperatura encontrada
                for cpu_name, cpu_temps in temps.items():
                    if cpu_temps:
                        return round(cpu_temps[0].current, 1)
        except:
            pass
        return None
    
    def get_gpu_info(self):
        """Obter informações sobre GPU (se disponível)"""
        # Usar o percent de CPU apenas como proxy (psutil não tem acesso direto a GPU sem nvidia-ml)
        # Reutilizar _last_cpu_percent para evitar segunda chamada de psutil.cpu_percent()
        gpu_percent = self._last_cpu_percent if self._last_cpu_percent is not None else 0
        return {
            'gpu_load': gpu_percent,
            'gpu_power': round((gpu_percent / 100) * 75, 2)
        }
    
    def get_ram_usage(self):
        """Obter uso de memória RAM"""
        ram = psutil.virtual_memory()
        return {
            'ram_percent': ram.percent,
            'ram_used_gb': round(ram.used / (1024**3), 2),
            'ram_total_gb': round(ram.total / (1024**3), 2)
        }
    
    def get_battery_info(self):
        """Obter informações da bateria (se disponível)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'plugged': battery.power_plugged,
                    'percent': battery.percent,
                    'time_remaining': str(battery.secsleft)
                }
            return None
        except:
            return None
            
    def get_disk_io(self):
        """Obter informações de uso do disco"""
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                return {
                    'read_mb': round(disk_io.read_bytes / (1024**2), 2),
                    'write_mb': round(disk_io.write_bytes / (1024**2), 2)
                }
        except:
            pass
        return {'read_mb': 0, 'write_mb': 0}
        
    def get_network_io(self):
        """Obter informações de rede"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'recv_mb': round(net_io.bytes_recv / (1024**2), 2)
            }
        except:
            return {'sent_mb': 0, 'recv_mb': 0}
    
    def get_system_uptime(self):
        """Obter tempo de atividade do sistema"""
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': uptime.total_seconds()
        }
    
    def get_process_list(self, top_n=10):
        """Obter lista de processos mais intensivos em recursos"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cpu_percent': proc_info['cpu_percent'] or 0,
                    'memory_percent': proc_info['memory_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Ordenar por consumo de CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:top_n]
    
    def collect_sample(self):
        """Coletar uma amostra completa de consumo"""
        sample = {
            'timestamp': datetime.now().isoformat(),
            'cpu_power': self.get_cpu_power(),
            'gpu_power': self.get_gpu_info(),
            'ram_usage': self.get_ram_usage(),
            'battery': self.get_battery_info(),
            'disk_io': self.get_disk_io(),
            'network_io': self.get_network_io(),
            'system_uptime': self.get_system_uptime(),
            'top_processes': self.get_process_list(5)
        }
        
        # Adicionar ao histórico
        self.history.append({
            'timestamp': sample['timestamp'],
            'total_power_watts': sample['cpu_power']['cpu_power_watts'] + sample['gpu_power']['gpu_power'],
            'cpu_percent': sample['cpu_power']['cpu_percent'],
            'gpu_percent': sample['gpu_power']['gpu_load'],
            'ram_percent': sample['ram_usage']['ram_percent'],
            'cpu_temp': sample['cpu_power']['cpu_temp']
        })
        
        return sample
    
    def start(self):
        """Iniciar monitoramento contínuo"""
        self.running = True
        self._load_history()
        print("Monitoramento iniciado...")
        
    def stop(self):
        """Parar monitoramento e salvar dados"""
        self.running = False
        self._save_history()
        print("Monitoramento parado. Dados salvos.")
        
    def run_once(self):
        """Executar uma única coleta de dados"""
        return self.collect_sample()
        
    def run_periodic(self, callback=None):
        """Executar monitoramento periódico"""
        self.start()
        while self.running:
            try:
                sample = self.collect_sample()
                if callback:
                    callback(sample)
                time.sleep(self.config['sample_interval'])
            except KeyboardInterrupt:
                self.stop()
                
    def get_statistics(self):
        """Calcular estatísticas do histórico"""
        if not self.history:
            return None
            
        powers = [record['total_power_watts'] for record in self.history]
        cpu_percents = [record['cpu_percent'] for record in self.history]
        gpu_percents = [record['gpu_percent'] for record in self.history]
        ram_percents = [record['ram_percent'] for record in self.history]
        
        return {
            'total_samples': len(self.history),
            'avg_power_watts': round(sum(powers) / len(powers), 2),
            'max_power_watts': max(powers),
            'min_power_watts': min(powers),
            'avg_cpu_percent': round(sum(cpu_percents) / len(cpu_percents), 2),
            'avg_gpu_percent': round(sum(gpu_percents) / len(gpu_percents), 2),
            'avg_ram_percent': round(sum(ram_percents) / len(ram_percents), 2),
            'current_power_watts': round(powers[-1], 2) if powers else 0,
            'total_energy_kwh': round((sum(powers) * self.config['sample_interval']) / 3600000, 6)
        }
