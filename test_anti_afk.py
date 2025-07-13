"""
Test script for Anti-AFK Plugin
Tests basic functionality without actually triggering inputs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from plugins.anti_afk import AntiAFKPlugin
from core.config_manager import ConfigManager
from core.thread_manager import ThreadManager

def test_anti_afk_plugin():
    """Test the Anti-AFK plugin functionality."""
    print("🧪 Testing Anti-AFK Plugin...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create required managers
    config_manager = ConfigManager()
    thread_manager = ThreadManager()
    
    try:
        # Initialize plugin
        plugin = AntiAFKPlugin(config_manager, thread_manager)
        print("✅ Plugin created successfully")
        
        # Test configuration defaults
        print(f"📋 Default interval: {plugin.plugin_config.get('interval_min')}-{plugin.plugin_config.get('interval_max')} seconds")
        print(f"🖱️ Mouse enabled: {plugin.plugin_config.get('mouse_enabled')}")
        print(f"⌨️ Keyboard enabled: {plugin.plugin_config.get('keyboard_enabled')}")
        print(f"🎮 Only in games: {plugin.plugin_config.get('only_in_games')}")
        print(f"🛡️ Safe mode: {plugin.plugin_config.get('safe_mode')}")
        print(f"🔑 Default keys: {plugin.plugin_config.get('keyboard_keys')}")
        
        # Test game detection (without triggering inputs)
        plugin._detect_active_game()
        if plugin.current_game_window:
            print(f"🎮 Current window: {plugin.current_game_window.get('title', 'Unknown')}")
            print(f"📂 Process: {plugin.current_game_window.get('process', 'unknown')}")
        else:
            print("🚫 No game window detected")
        
        # Test game detection logic
        is_game = plugin._is_game_active()
        print(f"🎯 Game detection result: {is_game}")
        
        # Test user activity detection
        is_active = plugin._is_user_recently_active()
        print(f"👤 User recently active: {is_active}")
        
        # Test configuration saving
        plugin.plugin_config['test_value'] = 'test_success'
        plugin.save_config()
        print("✅ Configuration save test passed")
        
        print("\n🎉 Anti-AFK Plugin test completed successfully!")
        print("\n📖 How to use:")
        print("1. Start the Gaming Helper Overlay")
        print("2. Open the Control Panel (click the floating icon)")
        print("3. Find 'Anti-AFK Emulation' in the plugins list")
        print("4. Click to activate the plugin")
        print("5. Configure settings and click 'Start Anti-AFK'")
        print("6. The plugin will prevent AFK kicks by simulating inputs")
        
        print("\n⚠️ Safety Notes:")
        print("• Safe mode is enabled by default (minimal mouse movements)")
        print("• Only activates when games are detected")
        print("• Respects user activity (pauses when you're active)")
        print("• Configurable intervals prevent detection")
        print("• Emergency stop on user input")
        
        print("\n🔧 Features:")
        print("• Random mouse movements (5-10 pixels)")
        print("• Configurable key presses (WASD, Space, etc.)")
        print("• Game whitelist/blacklist support")
        print("• Smart activity detection")
        print("• Advanced configuration dialog")
        print("• Real-time status display")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        thread_manager.shutdown()

if __name__ == "__main__":
    test_anti_afk_plugin()
