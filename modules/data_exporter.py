"""
PowerMonitor - Módulo de exportação de dados
Exportar dados para CSV e Excel
"""

import csv
import json
import os
from datetime import datetime


class DataExporter:
    def __init__(self, data_source=None):
        """
        data_source: objeto com método get_history() ou similar
        """
        self.data_source = data_source
        
    def export_to_csv(self, filepath, data=None):
        """Exportar dados para CSV"""
        try:
            if data is None and self.data_source:
                data = self.data_source.get_history()
                
            if not data:
                raise ValueError("Nenhum dado para exportar")
                
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow(['Timestamp', 'Potência (W)', 'CPU %', 'GPU %', 'RAM %'])
                
                # Dados
                for record in data:
                    writer.writerow([
                        record.get('timestamp', ''),
                        record.get('total_power_watts', ''),
                        record.get('cpu_percent', ''),
                        record.get('gpu_percent', ''),
                        record.get('ram_percent', '')
                    ])
                    
            return True
            
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False
            
    def export_to_excel(self, filepath, data=None):
        """Exportar dados para Excel (requer openpyxl)"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            if data is None and self.data_source:
                data = self.data_source.get_history()
                
            if not data:
                raise ValueError("Nenhum dado para exportar")
                
            # Criar workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Consumo de Energia"
            
            # Estilos
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_align = Alignment(horizontal="center", vertical="center")
            
            # Cabeçalho
            headers = ['Timestamp', 'Potência (W)', 'CPU %', 'GPU %', 'RAM %']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_align
                
            # Dados
            for row, record in enumerate(data, 2):
                ws.cell(row=row, column=1, value=record.get('timestamp', ''))
                ws.cell(row=row, column=2, value=record.get('total_power_watts', 0))
                ws.cell(row=row, column=3, value=record.get('cpu_percent', 0))
                ws.cell(row=row, column=4, value=record.get('gpu_percent', 0))
                ws.cell(row=row, column=5, value=record.get('ram_percent', 0))
                
            # Ajustar largura das colunas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
                
            # Salvar workbook
            wb.save(filepath)
            return True
            
        except ImportError:
            print("openpyxl não está instalado. Instalando...")
            os.system("pip install openpyxl")
            return self.export_to_excel(filepath, data)
            
        except Exception as e:
            print(f"Erro ao exportar para Excel: {e}")
            return False
            
    def export_to_json(self, filepath, data=None):
        """Exportar dados para JSON"""
        try:
            if data is None and self.data_source:
                data = self.data_source.get_history()
                
            if not data:
                raise ValueError("Nenhum dado para exportar")
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Erro ao exportar para JSON: {e}")
            return False
            
    def generate_report(self, filepath, data=None, stats=None):
        """Gerar relatório completo em arquivo de texto"""
        try:
            if data is None and self.data_source:
                data = self.data_source.get_history()
                
            report = f"""
📊 RELATÓRIO DE CONSUMO DE ENERGIA
Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 ESTATÍSTICAS:
"""
            if stats:
                report += f"""
• Amolestras coletadas: {stats.get('total_samples', 0)}
• Potência média: {stats.get('avg_power_watts', 0)} W
• Potência máxima: {stats.get('max_power_watts', 0)} W
• Potência mínima: {stats.get('min_power_watts', 0)} W
• Potência atual: {stats.get('current_power_watts', 0)} W
• Energia total consumida: {stats.get('total_energy_kwh', 0)} kWh

🖥️ RECURSOS DO SISTEMA:
• CPU médio: {stats.get('avg_cpu_percent', 0)}%
• GPU médio: {stats.get('avg_gpu_percent', 0)}%
• RAM médio: {stats.get('avg_ram_percent', 0)}%
"""
            
            if data:
                report += f"\n📋 ÚLTIMOS REGISTROS:\n"
                for record in data[-10:]:  # Últimos 10 registros
                    report += f"""
[{record.get('timestamp', '')}] 
Potência: {record.get('total_power_watts', 0)} W | CPU: {record.get('cpu_percent', 0)}% | RAM: {record.get('ram_percent', 0)}%
"""
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
                
            return True
            
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return False

