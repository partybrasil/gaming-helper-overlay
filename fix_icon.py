#!/usr/bin/env python3
"""
Fix Floating Icon Configuration
Reset the floating icon to correct size and position.
"""

import yaml
from pathlib import Path

def fix_icon_config():
    config_file = Path("config/config.yaml")
    
    if not config_file.exists():
        print("Config file not found!")
        return
    
    # Load config
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Fix floating icon settings
    if 'floating_icon' not in config:
        config['floating_icon'] = {}
    
    config['floating_icon']['size'] = {'width': 50, 'height': 50}
    config['floating_icon']['position'] = {'x': 100, 'y': 100}
    config['floating_icon']['opacity'] = 0.8
    config['floating_icon']['always_on_top'] = True
    
    # Save config
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("Floating icon configuration fixed!")
    print("- Size: 50x50")
    print("- Position: (100, 100)")
    print("- Opacity: 0.8")

if __name__ == "__main__":
    fix_icon_config()
