# -*- coding: utf-8 -*-
"""
PowerMonitor Pro - Teste em modo console
Valida as funcionalidades básicas sem interface gráfica
"""

import sys
import os
import codecs

# Forçar UTF-8 no stdout
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_power_monitor():
    """Testar módulo de monitoramento"""
    print("[TESTE] Módulo de monitoramento de energia")
    
    try:
        from modules.power_monitor import PowerMonitor
        
        monitor = PowerMonitor({
            'sample_interval': 1,
            'storage_file': 'data/test_history.json'
        })
        
        sample = monitor.run_once()
        
        print(f"[OK] CPU Power: {sample['cpu_power']['cpu_power_watts']} W")
        print(f"[OK] GPU Power: {sample['gpu_power']['gpu_power']} W")
        print(f"[OK] RAM Usage: {sample['ram_usage']['ram_percent']}%")
        cpu_temp = sample['cpu_power']['cpu_temp']
        print(f"[OK] CPU Temp: {cpu_temp} C" if cpu_temp else "[OK] CPU Temp: N/A")
        
        stats = monitor.get_statistics()
        print(f"[OK] Estatísticas: {stats['total_samples']} amostras coletadas")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Monitoramento: {e}")
        return False

def test_export():
    """Testar módulo de exportação"""
    print("\n[TESTE] Módulo de exportação")
    
    try:
        from modules.data_exporter import DataExporter
        
        import json
        with open('data/demo_data.json', 'r') as f:
            demo_data = json.load(f)
        
        exporter = DataExporter()
        
        success_csv = exporter.export_to_csv('data/test_export.csv', demo_data)
        if success_csv:
            print("[OK] Exportação CSV")
        
        success_excel = exporter.export_to_excel('data/test_export.xlsx', demo_data)
        if success_excel:
            print("[OK] Exportação Excel")
            
        success_json = exporter.export_to_json('data/test_export.json', demo_data)
        if success_json:
            print("[OK] Exportação JSON")
            
        return True
        
    except Exception as e:
        print(f"[ERRO] Exportação: {e}")
        return False

def test_alerts():
    """Testar sistema de alertas"""
    print("\n[TESTE] Sistema de alertas")
    
    try:
        from modules.alert_system import AlertSystem
        
        alert_system = AlertSystem({
            'max_power_watts': 50,
            'max_temperature': 30,
            'max_cpu_percent': 5,
            'max_ram_percent': 5,
            'alert_cooldown': 10
        })
        
        alert_system.start()
        
        import time
        time.sleep(15)
        
        alerts = alert_system.get_alerts()
        print(f"[OK] {len(alerts)} alertas gerados")
        
        alert_system.stop()
        return True
        
    except Exception as e:
        print(f"[ERRO] Alertas: {e}")
        return False

def main():
    print("PowerMonitor Pro - Teste Console")
    print("=" * 40)
    
    tests = [test_power_monitor, test_export, test_alerts]
    results = []
    
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[ERRO] Teste {test.__name__}: {e}")
            results.append(False)
            
    print("\n" + "=" * 40)
    print("RESUMO:")
    for i, result in enumerate(results):
        status = "[APROVADO]" if result else "[FALHOU]"
        print(f"{i+1}. {status}")
        
    if all(results):
        print("\n[SUCESSO] Todos os testes passaram!")
    else:
        print("\n[AVISO] Alguns testes falharam.")
        
    return 0

if __name__ == "__main__":
    main()
