#!/usr/bin/env python3
"""
Test Configuration Script
Script para verificar y reparar configuraciones antes de ejecutar tests
"""

import os
import sys
import yaml
from pathlib import Path

def create_minimal_config():
    """Crear configuración mínima para pruebas"""
    
    # Crear directorio de configuración si no existe
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    plugins_dir = config_dir / "plugins"
    plugins_dir.mkdir(exist_ok=True)
    
    # Configuración principal mínima
    main_config = {
        'app': {
            'name': 'Gaming Helper Overlay',
            'version': '1.0.0',
            'debug': False
        },
        'ui': {
            'theme': 'dark',
            'opacity': 0.9,
            'always_on_top': True
        },
        'floating_icon': {
            'enabled': True,
            'size': {'width': 50, 'height': 50},
            'position': {'x': 100, 'y': 100},
            'opacity': 0.8,
            'always_on_top': True
        },
        'plugins': {
            'enabled': True,
            'auto_load': True
        }
    }
    
    config_file = config_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(main_config, f, default_flow_style=False, indent=2)
    
    print(f"✓ Configuración principal creada: {config_file}")
    
    # Configuraciones de plugins
    plugin_configs = {
        'crosshair.yaml': {
            'enabled': False,
            'type': 'cross',
            'color': '#00FF00',
            'size': 20,
            'thickness': 2,
            'opacity': 0.8
        },
        'fps_counter.yaml': {
            'enabled': False,
            'position': 'top-left',
            'font_size': 12,
            'color': '#FFFFFF',
            'update_interval': 1.0
        },
        'cpu_gpu_monitor.yaml': {
            'enabled': False,
            'update_interval': 2.0,
            'show_cpu': True,
            'show_gpu': True,
            'show_memory': True
        },
        'anti_afk.yaml': {
            'enabled': False,
            'interval_min': 60,
            'interval_max': 120,
            'mouse_enabled': True,
            'keyboard_enabled': True,
            'safe_mode': True
        }
    }
    
    for config_name, config_data in plugin_configs.items():
        plugin_config_file = plugins_dir / config_name
        with open(plugin_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        print(f"✓ Configuración de plugin creada: {plugin_config_file}")

def create_missing_directories():
    """Crear directorios faltantes"""
    
    required_dirs = [
        "logs",
        "data", 
        "assets/icons",
        "config/plugins"
    ]
    
    for dir_path in required_dirs:
        dir_path_obj = Path(dir_path)
        dir_path_obj.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio asegurado: {dir_path}")

def create_placeholder_files():
    """Crear archivos placeholder necesarios"""
    
    # Crear icono placeholder si no existe
    icon_path = Path("assets/icons/app_icon.png")
    if not icon_path.exists():
        # Crear un archivo PNG mínimo (1x1 pixel transparente)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(icon_path, 'wb') as f:
            f.write(png_data)
        print(f"✓ Icono placeholder creado: {icon_path}")
    
    # Crear archivo de log placeholder
    log_path = Path("logs/gaming_helper.log")
    if not log_path.exists():
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("# Gaming Helper Overlay Log\n")
        print(f"✓ Log placeholder creado: {log_path}")

def main():
    """Función principal"""
    print("🔧 Configurando entorno de pruebas...")
    print("=" * 40)
    
    try:
        create_missing_directories()
        create_minimal_config()
        create_placeholder_files()
        
        print("\n✅ Entorno de pruebas configurado correctamente")
        print("Ahora puedes ejecutar: python test_suite.py")
        
    except Exception as e:
        print(f"\n❌ Error configurando entorno: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
