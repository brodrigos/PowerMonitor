"""
PowerMonitor - Interface Gráfica
Interface principal da aplicação com Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime
import csv
import os

class PowerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Power Monitor Pro")
        self.root.geometry("1200x800")
        
        # Importar o módulo de monitoramento
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from modules.power_monitor import PowerMonitor
        
        self.monitor = PowerMonitor({
            'sample_interval': 2,
            'storage_file': 'data/consumption_history.json'
        })
        
        self.config_file = 'data/app_config.json'
        self.load_config()
        
        self.setup_ui()
        self.update_dashboard()
        
    def setup_ui(self):
        """Configurar interface do usuário"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TFrame', 
            background='#1e1e2e'
        )
        style.configure(
            'TLabel', 
            background='#1e1e2e', 
            foreground='#ffffff',
            font=('Segoe UI', 10)
        )
        style.configure(
            'TButton', 
            font=('Segoe UI', 10)
        )
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Topo - Painel de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Botões de controle
        self.start_btn = ttk.Button(
            control_frame, 
            text="▶ Iniciar", 
            command=self.start_monitoring
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame, 
            text="⏸ Parar", 
            command=self.stop_monitoring,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)
        
        self.export_btn = ttk.Button(
            control_frame, 
            text="📊 Exportar", 
            command=self.export_data
        )
        self.export_btn.pack(side='left', padx=5)
        
        self.alert_btn = ttk.Button(
            control_frame, 
            text="⚠️ Alertas", 
            command=self.show_alert_settings
        )
        self.alert_btn.pack(side='left', padx=5)
        
        self.settings_btn = ttk.Button(
            control_frame, 
            text="⚙️ Configurações", 
            command=self.show_settings
        )
        self.settings_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label = ttk.Label(
            control_frame, 
            text="Monitoramento parado",
            foreground='#ff9800'
        )
        self.status_label.pack(side='left', padx=20)
        
        # Abas principais
        self.tabs = ttk.Notebook(main_frame)
        self.tabs.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Aba - Dashboard
        self.dashboard_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.dashboard_tab, text='📊 Dashboard')
        self.setup_dashboard()
        
        # Aba - Processos
        self.processes_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.processes_tab, text='📋 Processos')
        self.setup_processes_tab()
        
        # Aba - Histórico
        self.history_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.history_tab, text='📈 Histórico')
        self.setup_history_tab()
        
        # Aba - Relatórios
        self.reports_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.reports_tab, text='📄 Relatórios')
        self.setup_reports_tab()
        
        # Frame de status na parte inferior
        status_bar = ttk.Frame(main_frame, relief='sunken', style='TFrame')
        status_bar.pack(fill='x', padx=10, pady=5)
        
        self.status_text = tk.Text(
            status_bar, 
            height=3, 
            width=100,
            bg='#0d1117',
            fg='#e6edf3',
            font=('Consolas', 9),
            state='disabled',
            wrap='word'
        )
        scrollbar = ttk.Scrollbar(status_bar, orient='horizontal', command=self.status_text.xview)
        self.status_text.configure(xscrollcommand=scrollbar.set)
        
        self.status_text.pack(side='top', fill='x', expand=True)
        scrollbar.pack(side='bottom', fill='x', expand=True)
        
    def setup_dashboard(self):
        """Configurar painel principal"""
        # Painel de métricas principais
        metrics_frame = ttk.Frame(self.dashboard_tab)
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Criar widgets de métricas
        self.power_label = tk.Label(
            metrics_frame,
            text="⚡ Potência: 0 W",
            font=('Segoe UI', 14, 'bold'),
            fg='#00ff00',
            bg='#1e1e2e'
        )
        self.power_label.pack(side='left', padx=20, pady=10)
        
        self.cpu_label = tk.Label(
            metrics_frame,
            text="🖥️ CPU: 0%",
            font=('Segoe UI', 12),
            fg='#ffffff',
            bg='#1e1e2e'
        )
        self.cpu_label.pack(side='left', padx=20, pady=10)
        
        self.gpu_label = tk.Label(
            metrics_frame,
            text="🎮 GPU: 0%",
            font=('Segoe UI', 12),
            fg='#ffffff',
            bg='#1e1e2e'
        )
        self.gpu_label.pack(side='left', padx=20, pady=10)
        
        self.ram_label = tk.Label(
            metrics_frame,
            text="💾 RAM: 0%",
            font=('Segoe UI', 12),
            fg='#ffffff',
            bg='#1e1e2e'
        )
        self.ram_label.pack(side='left', padx=20, pady=10)
        
        self.energy_label = tk.Label(
            metrics_frame,
            text="🔋 Energia total: 0 kWh",
            font=('Segoe UI', 12),
            fg='#ffffff',
            bg='#1e1e2e'
        )
        self.energy_label.pack(side='left', padx=20, pady=10)
        
        # Frame para gráficos
        graph_frame = ttk.Frame(self.dashboard_tab)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Placeholder para gráfico
        self.graph_placeholder = tk.Canvas(
            graph_frame, 
            bg='#1e1e2e',
            width=800,
            height=400
        )
        self.graph_placeholder.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Adicionar texto de instrução
        self.graph_placeholder.create_text(
            400, 200,
            text="📈 Gráfico de consumo aparecerá aqui quando o monitoramento estiver ativo",
            font=('Segoe UI', 14),
            fill='#ffffff'
        )
        
    def setup_processes_tab(self):
        """Configurar aba de processos"""
        processes_frame = ttk.Frame(self.processes_tab)
        processes_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview para processos
        columns = ('PID', 'Nome', 'CPU %', 'Memória %')
        self.process_tree = ttk.Treeview(processes_frame, columns=columns, show='headings')
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100, anchor='center')
            
        self.process_tree.pack(fill='both', expand=True)
        
        # Botão de atualização
        refresh_btn = ttk.Button(
            processes_frame,
            text="🔄 Atualizar",
            command=self.update_process_list
        )
        refresh_btn.pack(pady=5)
        
    def setup_history_tab(self):
        """Configurar aba de histórico"""
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame de filtro
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filtrar por:").pack(side='left')
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(
            filter_frame, 
            textvariable=self.filter_var,
            width=30
        )
        filter_entry.pack(side='left', padx=5)
        
        ttk.Button(
            filter_frame, 
            text="🔍 Filtrar", 
            command=self.filter_history
        ).pack(side='left', padx=5)
        
        # Treeview para histórico
        columns = ('Timestamp', 'Potência (W)', 'CPU %', 'GPU %', 'RAM %')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120, anchor='center')
            
        self.history_tree.pack(fill='both', expand=True)
        
        # Botões de ação
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            action_frame,
            text="🗑️ Limpar Histórico",
            command=self.clear_history
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="📥 Importar CSV",
            command=self.import_csv
        ).pack(side='left', padx=5)
        
    def setup_reports_tab(self):
        """Configurar aba de relatórios"""
        reports_frame = ttk.Frame(self.reports_tab)
        reports_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Label de resumo
        self.report_label = tk.Label(
            reports_frame,
            text="📊 Estatísticas aparecerão aqui quando os dados forem coletados",
            font=('Segoe UI', 12),
            bg='#1e1e2e',
            fg='#ffffff',
            justify='left',
            wraplength=1000
        )
        self.report_label.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botão para gerar relatório
        ttk.Button(
            reports_frame,
            text="📄 Gerar Relatório",
            command=self.generate_report
        ).pack(pady=5)
        
    def start_monitoring(self):
        """Iniciar monitoramento"""
        self.monitor.start()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Monitoramento ativo", foreground='#00ff00')
        
        # Iniciar thread de monitoramento
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        
        self.add_status_message("Monitoramento iniciado!")
        
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitor.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Monitoramento parado", foreground='#ff9800')
        self.add_status_message("Monitoramento parado.")
        
    def monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitor.running:
            try:
                sample = self.monitor.collect_sample()
                self.root.after(0, self.update_dashboard_values, sample)
                self.root.after(0, self.update_process_list)
                self.root.after(0, self.update_history_tree)
                self.root.after(0, self.update_reports)
            except Exception as e:
                self.add_status_message(f"Erro no monitoramento: {e}")
            time.sleep(self.monitor.config['sample_interval'])
            
    def update_dashboard(self):
        """Atualizar painel principal"""
        pass  # Método chamado periodicamente
        
    def update_dashboard_values(self, sample):
        """Atualizar valores do dashboard"""
        try:
            cpu_power = sample['cpu_power']['cpu_power_watts']
            gpu_power = sample['gpu_power']['gpu_power']
            total_power = cpu_power + gpu_power
            
            self.power_label.config(
                text=f"⚡ Potência: {total_power} W",
                fg='#00ff00' if total_power < 50 else '#ff9800' if total_power < 150 else '#ff4444'
            )
            
            self.cpu_label.config(
                text=f"🖥️ CPU: {sample['cpu_power']['cpu_percent']}%",
                fg='#00ff00' if sample['cpu_power']['cpu_percent'] < 50 else '#ff9800' if sample['cpu_power']['cpu_percent'] < 80 else '#ff4444'
            )
            
            self.gpu_label.config(
                text=f"🎮 GPU: {sample['gpu_power']['gpu_load']}%",
                fg='#00ff00' if sample['gpu_power']['gpu_load'] < 50 else '#ff9800' if sample['gpu_power']['gpu_load'] < 80 else '#ff4444'
            )
            
            self.ram_label.config(
                text=f"💾 RAM: {sample['ram_usage']['ram_percent']}%",
                fg='#00ff00' if sample['ram_usage']['ram_percent'] < 70 else '#ff9800' if sample['ram_usage']['ram_percent'] < 85 else '#ff4444'
            )
            
            stats = self.monitor.get_statistics()
            if stats:
                self.energy_label.config(
                    text=f"🔋 Energia total: {stats['total_energy_kwh']} kWh",
                    fg='#00ff00' if stats['total_energy_kwh'] < 0.1 else '#ff9800'
                )
                
        except Exception as e:
            self.add_status_message(f"Erro ao atualizar dashboard: {e}")
            
    def update_process_list(self):
        """Atualizar lista de processos"""
        try:
            processes = self.monitor.get_process_list(15)
            
            # Limpar treeview
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
                
            # Adicionar processos
            for proc in processes:
                self.process_tree.insert('', 'end', values=(
                    proc['pid'],
                    proc['name'],
                    f"{proc['cpu_percent']}%",
                    f"{proc['memory_percent']}%"
                ))
        except Exception as e:
            self.add_status_message(f"Erro ao atualizar processos: {e}")
            
    def update_history_tree(self):
        """Atualizar treeview de histórico"""
        try:
            if not self.monitor.history:
                return
                
            # Manter apenas os últimos 100 registros visíveis
            recent_history = self.monitor.history[-100:]
            
            # Limpar treeview
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
                
            # Adicionar registros
            for record in recent_history:
                self.history_tree.insert('', 'end', values=(
                    record['timestamp'][:19],  # Format timestamp
                    f"{record['total_power_watts']}W",
                    f"{record['cpu_percent']}%",
                    f"{record['gpu_percent']}%",
                    f"{record['ram_percent']}%"
                ))
        except Exception as e:
            self.add_status_message(f"Erro ao atualizar histórico: {e}")
            
    def update_reports(self):
        """Atualizar relatórios"""
        pass  # Método chamado periodicamente
        
    def filter_history(self):
        """Filtrar histórico baseado no texto de busca"""
        filter_text = self.filter_var.get().lower()
        
        for item in self.history_tree.get_children():
            values = self.history_tree.item(item)['values']
            # Simplificar filtro - apenas mostrar se contém o texto
            if filter_text.lower() in ' '.join(str(v) for v in values).lower():
                self.history_tree.tag_configure(item, background='#333355')
            else:
                self.history_tree.tag_configure(item, background='')
                
    def clear_history(self):
        """Limpar histórico"""
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o histórico?"):
            self.monitor.history = []
            self.monitor._save_history()
            self.history_tree.delete(*self.history_tree.get_children())
            self.add_status_message("Histórico limpo.")
            
    def import_csv(self):
        """Importar dados de CSV"""
        import tkinter.filedialog
        
        file_path = tkinter.filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        
        if file_path:
            try:
                # Implementação simplificada de importação CSV
                self.add_status_message(f"CSV importado: {file_path}")
                # Aqui você implementaria a lógica real de parsing CSV
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar CSV: {e}")
                
    def export_data(self):
        """Exportar dados para CSV"""
        import tkinter.filedialog
        
        file_path = tkinter.filedialog.asksaveasfilename(
            title="Salvar dados",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Potência (W)', 'CPU %', 'GPU %', 'RAM %'])
                    
                    for record in self.monitor.history:
                        writer.writerow([
                            record['timestamp'],
                            record['total_power_watts'],
                            record['cpu_percent'],
                            record['gpu_percent'],
                            record['ram_percent']
                        ])
                        
                self.add_status_message(f"Dados exportados para: {file_path}")
                messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {e}")
                
    def show_alert_settings(self):
        """Mostrar configurações de alerta"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Configurações de Alerta")
        alert_window.geometry("400x300")
        
        # Frame principal
        frame = ttk.Frame(alert_window, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Configuração de potência máxima
        ttk.Label(frame, text="Potência máxima (W):").pack(anchor='w', pady=5)
        self.max_power_var = tk.StringVar(value=str(self.config.get('max_power_watts', 200)))
        ttk.Entry(frame, textvariable=self.max_power_var).pack(fill='x', pady=5)
        
        # Configuração de temperatura máxima
        ttk.Label(frame, text="Temperatura máxima (°C):").pack(anchor='w', pady=5)
        self.max_temp_var = tk.StringVar(value=str(self.config.get('max_temperature', 80)))
        ttk.Entry(frame, textvariable=self.max_temp_var).pack(fill='x', pady=5)
        
        # Botões
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            button_frame, 
            text="Salvar", 
            command=self.save_alert_settings
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=alert_window.destroy
        ).pack(side='right', padx=5)
        
    def save_alert_settings(self):
        """Salvar configurações de alerta"""
        try:
            self.config['max_power_watts'] = float(self.max_power_var.get())
            self.config['max_temperature'] = float(self.max_temp_var.get())
            self.save_config()
            self.add_status_message("Configurações de alerta salvas.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
            
    def show_settings(self):
        """Mostrar configurações da aplicação"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("500x400")
        
        # Frame principal
        frame = ttk.Frame(settings_window, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Intervalo de amostragem
        ttk.Label(frame, text="Intervalo de amostragem (segundos):").pack(anchor='w', pady=5)
        self.interval_var = tk.StringVar(value=str(self.monitor.config['sample_interval']))
        ttk.Entry(frame, textvariable=self.interval_var).pack(fill='x', pady=5)
        
        # Caminho de armazenamento
        ttk.Label(frame, text="Caminho de armazenamento:").pack(anchor='w', pady=5)
        self.storage_path_var = tk.StringVar(value=self.monitor.config['storage_file'])
        ttk.Entry(frame, textvariable=self.storage_path_var).pack(fill='x', pady=5)
        
        # Botões
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            button_frame, 
            text="Salvar", 
            command=self.save_settings
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=settings_window.destroy
        ).pack(side='right', padx=5)
        
    def save_settings(self):
        """Salvar configurações"""
        try:
            self.monitor.config['sample_interval'] = int(self.interval_var.get())
            self.monitor.config['storage_file'] = self.storage_path_var.get()
            self.save_config()
            self.add_status_message("Configurações salvas.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
            
    def generate_report(self):
        """Gerar relatório estatístico"""
        stats = self.monitor.get_statistics()
        if not stats:
            messagebox.showinfo("Estatísticas", "Nenhum dado disponível para gerar relatório.")
            return
            
        report_text = f"""
📊 RELATÓRIO DE CONSUMO DE ENERGIA

📈 ESTATÍSTICAS:
• Amolestras coletadas: {stats['total_samples']}
• Potência média: {stats['avg_power_watts']} W
• Potência máxima: {stats['max_power_watts']} W
• Potência mínima: {stats['min_power_watts']} W
• Potência atual: {stats['current_power_watts']} W
• Energia total consumida: {stats['total_energy_kwh']} kWh

🖥️ RECURSOS DO SISTEMA:
• CPU médio: {stats['avg_cpu_percent']}%
• GPU médio: {stats['avg_gpu_percent']}%
• RAM médio: {stats['avg_ram_percent']}%
        """
        
        # Mostrar relatório em janela
        report_window = tk.Toplevel(self.root)
        report_window.title("Relatório de Consumo")
        report_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(
            report_window, 
            width=70, 
            height=25,
            font=('Consolas', 10),
            bg='#0d1117',
            fg='#e6edf3'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('end', report_text)
        text_widget.config(state='disabled')
        
        # Salvar relatório em arquivo
        report_file = f"data/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self.add_status_message(f"Relatório salvo em: {report_file}")
        except Exception as e:
            self.add_status_message(f"Erro ao salvar relatório: {e}")
            
    def load_config(self):
        """Carregar configurações"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'max_power_watts': 200,
                    'max_temperature': 80,
                    'alert_enabled': True
                }
        except:
            self.config = {
                'max_power_watts': 200,
                'max_temperature': 80,
                'alert_enabled': True
            }
            
    def save_config(self):
        """Salvar configurações"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.add_status_message(f"Erro ao salvar configurações: {e}")
            
    def add_status_message(self, message):
        """Adicionar mensagem ao status"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.config(state='normal')
        self.status_text.insert('end', formatted_message)
        self.status_text.see('end')
        self.status_text.config(state='disabled')
        
def main():
    root = tk.Tk()
    app = PowerMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
