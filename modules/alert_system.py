"""
PowerMonitor - Sistema de Alertas
Sistema de alertas para monitoramento de consumo energético
"""

import time
import threading
from datetime import datetime


class AlertSystem:
    def __init__(self, config=None):
        self.config = config or {
            'max_power_watts': 200,
            'max_temperature': 80,
            'max_cpu_percent': 90,
            'max_ram_percent': 85,
            'alert_cooldown': 30  # segundos entre alertas do mesmo tipo
        }
        self.alerts = []
        self.running = False
        self.alert_thread = None
        
    def start(self):
        """Iniciar sistema de alertas"""
        self.running = True
        self.alert_thread = threading.Thread(target=self.alert_loop, daemon=True)
        self.alert_thread.start()
        
    def stop(self):
        """Parar sistema de alertas"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join()
            
    def alert_loop(self):
        """Loop principal de verificação de alertas"""
        while self.running:
            self.check_alerts()
            time.sleep(5)  # Verificar a cada 5 segundos
            
    def check_alerts(self):
        """Verificar condições de alerta"""
        import psutil
        
        # Verificar CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > self.config['max_cpu_percent']:
            self.trigger_alert(
                'cpu_high',
                f"CPU em {cpu_percent}% (limite: {self.config['max_cpu_percent']}%)",
                'warning'
            )
            
        # Verificar RAM
        ram = psutil.virtual_memory()
        if ram.percent > self.config['max_ram_percent']:
            self.trigger_alert(
                'ram_high',
                f"RAM em {ram.percent}% (limite: {self.config['max_ram_percent']}%)",
                'warning'
            )
            
        # Verificar temperatura
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for cpu_name, cpu_temps in temps.items():
                    if cpu_temps:
                        temp = cpu_temps[0].current
                        if temp > self.config['max_temperature']:
                            self.trigger_alert(
                                'temp_high',
                                f"Temperatura de {cpu_name} em {temp}°C (limite: {self.config['max_temperature']}°C)",
                                'critical'
                            )
        except:
            pass
            
    def trigger_alert(self, alert_type, message, severity='warning'):
        """Disparar alerta"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        # Verificar cooldown
        if self.is_alert_active(alert_type):
            return
            
        self.alerts.append(alert)
        self.send_notification(alert)
        
    def is_alert_active(self, alert_type):
        """Verificar se alerta do mesmo tipo está ativo recentemente"""
        for alert in self.alerts[-5:]:  # Verificar últimos 5 alerts
            if alert['type'] == alert_type:
                time_diff = (datetime.now() - datetime.fromisoformat(alert['timestamp'])).total_seconds()
                if time_diff < self.config['alert_cooldown']:
                    return True
        return False
        
    def send_notification(self, alert):
        """Enviar notificação de alerta"""
        # Aqui você implementaria o sistema de notificação
        # Por enquanto, apenas logar
        print(f"🚨 ALERTA [{alert['severity'].upper()}]: {alert['message']}")
        
        # Em uma implementação real, você poderia usar:
        # - Notificações do sistema operacional
        # - Emails
        # - Webhooks
        # - Sons
        
    def get_alerts(self, limit=50):
        """Retornar lista de alertas"""
        return self.alerts[-limit:]
        
    def clear_alerts(self):
        """Limpar alertas"""
        self.alerts = []
        
    def get_alert_summary(self):
        """Retornar resumo de alertas"""
        if not self.alerts:
            return "Nenhum alerta nos últimos 24 horas."
            
        summary = f"📊 RESUMO DE ALERTAS:\n"
        summary += f"Total de alertas: {len(self.alerts)}\n\n"
        
        # Contar por tipo
        alert_types = {}
        for alert in self.alerts:
            alert_type = alert['type']
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
        for alert_type, count in alert_types.items():
            summary += f"• {alert_type}: {count}\n"
            
        return summary
        
    def update_config(self, new_config):
        """Atualizar configurações de alerta"""
        self.config.update(new_config)

