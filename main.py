"""
PowerMonitor Pro - Aplicação de monitoramento de consumo de energia
Versão: 1.0
"""

import sys
import os

# Verificar dependências
def check_dependencies():
    """Verificar se todas as dependências estão instaladas"""
    missing = []
    required = ['psutil', 'tkinter']
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
            
    if missing:
        print("⚠️ Dependências faltando:")
        for package in missing:
            print(f"  - {package}")
        print("\n📦 Instalando dependências...")
        os.system(f'{sys.executable} -m pip install {", ".join(missing)}')
        return False
    return True

def main():
    # Verificar dependências
    if not check_dependencies():
        print("❌ Erro: Verifique as dependências e tente novamente.")
        input("Pressione Enter para sair...")
        return 1
        
    # Importar interface
    try:
        from ui.main import main as ui_main
        ui_main()
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
