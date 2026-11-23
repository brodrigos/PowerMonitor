"""
PowerMonitor Pro - Script de empacotamento para Windows
Cria um executável (.exe) da aplicação usando PyInstaller
"""

import os
import subprocess
import sys

def check_pyinstaller():
    """Verificar se PyInstaller está instalado"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("PyInstaller não está instalado. Instalando...")
        os.system(f'{sys.executable} -m pip install pyinstaller')
        return True

def create_spec_file():
    """Criar arquivo de spec para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('modules', 'modules'),
        ('ui', 'ui'),
    ],
    hiddenimports=[
        'psutil',
        'tkinter',
        'openpyxl',
        'matplotlib',
    ],
    hookspath=[],
    hooks=None,
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirect=False,
    noquery_reuse=False,
    lint=None,
    newline=None,
    kernel=None,
)

pyz = PYZ(a.pure, a.zipped_desc, kernel=None)

exe = EXE(
    pyz,
    ['main.py'],
    name='PowerMonitor Pro',
    icon=None,  # Você pode adicionar um ícone aqui
    version=None,
    windowed=True,
    disable_console=False,
    privileges_required=False,
    elevate=False,
    auto_install_ref=False,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('PowerMonitor Pro.spec', 'w') as f:
        f.write(spec_content)
        
    print("Arquivo de spec criado com sucesso!")

def build_executable():
    """Compilar o executável"""
    print("Compilando executável...")
    result = subprocess.run([
        'pyinstaller', 
        '--noconfirm',
        '--clean', 
        'PowerMonitor Pro.spec'
    ])
    
    if result.returncode == 0:
        print("Executável criado com sucesso!")
    else:
        print("Erro ao criar executável.")
        
def create_installer():
    """Criar instalador usando NSIS (opcional)"""
    print("Para criar um instalador completo, use NSIS:")
    print("https://www.nsis.org/Download")

def main():
    print("PowerMonitor Pro - Empacotamento")
    print("=" * 40)
    
    if not check_pyinstaller():
        return 1
        
    create_spec_file()
    build_executable()
    create_installer()
    
    return 0

if __name__ == "__main__":
    main()
