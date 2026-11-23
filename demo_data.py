"""
PowerMonitor Pro - Gerador de dados de demonstração
Gera dados simulados para testar a interface
"""

import json
import os
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Gerar dados de demonstração"""
    data = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(288):  # 24 horas a cada 5 minutos
        timestamp = start_time + timedelta(minutes=i*5)
        hour = timestamp.hour
        
        # Simular padrões de uso
        base_cpu = 20 + 30 * (0.5 + 0.5 * ((hour % 12) / 12))
        base_gpu = 10 + 20 * (0.5 + 0.5 * ((hour % 8) / 8))
        base_ram = 30 + 20 * ((hour % 6) / 6)
        
        data.append({
            'timestamp': timestamp.isoformat(),
            'total_power_watts': round(random.uniform(base_cpu, base_cpu + 50), 2),
            'cpu_percent': round(random.uniform(base_cpu * 0.5, base_cpu), 2),
            'gpu_percent': round(random.uniform(base_gpu * 0.5, base_gpu), 2),
            'ram_percent': round(random.uniform(base_ram * 0.5, base_ram), 2)
        })
    
    # Salvar dados
    os.makedirs('data', exist_ok=True)
    with open('data/demo_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Demo data generated: {len(data) } records")
    return data

if __name__ == "__main__":
    generate_demo_data()
