# PowerMonitor Pro - Script de Instalação Rápida

"""
Script para instalar e configurar o PowerMonitor Pro automaticamente
"""

import os
import sys
import subprocess

def install_dependencies():
    """Instalar dependências"""
    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
    ])
    
def create_directories():
    """Criar diretórios necessários"""
    dirs = ['data', 'logs', 'ui', 'modules', 'utils']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        
def create_config():
    """Criar arquivo de configuração padrão"""
    config = {
        'version': '1.0',
        'sample_interval': 2,
        'max_power_watts': 200,
        'max_temperature': 80,
        'alert_enabled': True,
        'export_format': 'csv'
    }
    
    if not os.path.exists('data'):
        os.makedirs('data')
        
    with open('data/config.json', 'w') as f:
        import json
        json.dump(config, f, indent=2)
        
def main():
    print("PowerMonitor Pro - Instalador")
    print("=" * 40)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Python 3.8+ is required")
        return 1
        
    # Criar diretórios
    create_directories()
    
    # Instalar dependências
    install_dependencies()
    
    # Criar configuração
    create_config()
    
    print("\nInstallation completed!")
    print("\nExecute: python main.py")
    print("\nSee README.md for more information")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
