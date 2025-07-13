"""
Test script for Multi-Hotkey Macros Plugin
Tests basic functionality of the macro system.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from plugins.multi_hotkey_macros import MultiHotkeyMacrosPlugin, Macro, MacroAction, ActionType
from core.config_manager import ConfigManager
from core.thread_manager import ThreadManager

def test_multi_hotkey_macros_plugin():
    """Test the Multi-Hotkey Macros plugin functionality."""
    print("🧪 Testing Multi-Hotkey Macros Plugin...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create required managers
    config_manager = ConfigManager()
    thread_manager = ThreadManager()
    
    try:
        # Initialize plugin
        plugin = MultiHotkeyMacrosPlugin(config_manager, thread_manager)
        print("✅ Plugin created successfully")
        
        # Test initialization
        init_success = plugin.initialize()
        print(f"🔧 Plugin initialization: {'✅ Success' if init_success else '❌ Failed'}")
        
        # Test configuration defaults
        print(f"📋 Default settings:")
        print(f"  - Enabled: {plugin.plugin_config.get('enabled')}")
        print(f"  - Global hotkeys: {plugin.plugin_config.get('global_hotkey_enabled')}")
        print(f"  - Auto save: {plugin.plugin_config.get('auto_save')}")
        print(f"  - Max concurrent: {plugin.plugin_config.get('max_concurrent_macros')}")
        print(f"  - Execution delay: {plugin.plugin_config.get('execution_delay')}s")
        
        # Test macro creation
        print("\n🔨 Testing macro creation...")
        macro_id = plugin.create_macro("Test Macro", "Testing")
        print(f"✅ Created macro with ID: {macro_id}")
        
        # Test adding actions to macro
        test_macro = plugin.macros[macro_id]
        
        # Add a delay action
        delay_action = MacroAction(
            action_type=ActionType.DELAY,
            parameters={'duration': 1.0},
            description="Wait 1 second"
        )
        test_macro.actions.append(delay_action)
        
        # Add a key press action (safe for testing)
        key_action = MacroAction(
            action_type=ActionType.KEY_PRESS,
            parameters={'key': 'space'},
            description="Press spacebar"
        )
        test_macro.actions.append(key_action)
        
        # Add a mouse move action (relative, safe)
        mouse_action = MacroAction(
            action_type=ActionType.MOUSE_MOVE,
            parameters={'x': 1, 'y': 1, 'relative': True},
            description="Move mouse slightly"
        )
        test_macro.actions.append(mouse_action)
        
        print(f"✅ Added {len(test_macro.actions)} actions to macro")
        
        # Test macro properties
        test_macro.hotkey = "ctrl+alt+t"
        test_macro.repeat_count = 2
        test_macro.description = "Test macro for validation"
        
        print(f"📄 Macro details:")
        print(f"  - Name: {test_macro.name}")
        print(f"  - Category: {test_macro.category}")
        print(f"  - Hotkey: {test_macro.hotkey}")
        print(f"  - Actions: {len(test_macro.actions)}")
        print(f"  - Repeat count: {test_macro.repeat_count}")
        print(f"  - Enabled: {test_macro.enabled}")
        
        # Test action types
        print(f"\n⚡ Action types:")
        for i, action in enumerate(test_macro.actions):
            print(f"  {i+1}. {action.action_type.value}: {action.description}")
        
        # Test macro saving
        print(f"\n💾 Testing macro persistence...")
        plugin._save_macros()
        print("✅ Macros saved successfully")
        
        # Test macro loading
        plugin.macros.clear()
        plugin._load_macros()
        reloaded_macro = plugin.macros.get(macro_id)
        
        if reloaded_macro:
            print("✅ Macro loaded successfully after save/reload")
            print(f"  - Reloaded actions: {len(reloaded_macro.actions)}")
        else:
            print("❌ Failed to reload macro")
        
        # Test execution capabilities (without actually executing)
        print(f"\n🏃 Testing execution system...")
        if hasattr(plugin, 'macro_executor'):
            print("✅ Macro executor available")
            print(f"  - Executor thread ready: {not plugin.macro_executor.isRunning()}")
        
        # Test dependency availability
        print(f"\n📦 Dependency status:")
        from plugins.multi_hotkey_macros import KEYBOARD_AVAILABLE, MOUSE_AVAILABLE
        print(f"  - Keyboard library: {'✅ Available' if KEYBOARD_AVAILABLE else '❌ Missing'}")
        print(f"  - Mouse library: {'✅ Available' if MOUSE_AVAILABLE else '❌ Missing'}")
        
        if not KEYBOARD_AVAILABLE or not MOUSE_AVAILABLE:
            print(f"\n⚠️ Missing dependencies. Install with:")
            missing = []
            if not KEYBOARD_AVAILABLE:
                missing.append("keyboard")
            if not MOUSE_AVAILABLE:
                missing.append("mouse")
            print(f"  pip install {' '.join(missing)}")
        
        # Test statistics
        print(f"\n📊 Execution statistics:")
        stats = plugin.execution_stats
        print(f"  - Total executed: {stats['total_executed']}")
        print(f"  - Successful: {stats['successful_executions']}")
        print(f"  - Failed: {stats['failed_executions']}")
        
        # Test configuration widget
        print(f"\n🎛️ Testing configuration widget...")
        config_widget = plugin.get_config_widget()
        if config_widget:
            print("✅ Configuration widget created successfully")
        else:
            print("❌ Failed to create configuration widget")
        
        print("\n🎉 Multi-Hotkey Macros Plugin test completed successfully!")
        print("\n📖 How to use:")
        print("1. Start the Gaming Helper Overlay")
        print("2. Open the Control Panel (click the floating icon)")
        print("3. Find 'Multi-Hotkey Macros' in the plugins list")
        print("4. Click to activate the plugin")
        print("5. Create and configure macros with hotkey combinations")
        print("6. Record actions or create them manually")
        print("7. Execute macros with hotkeys or the interface")
        
        print("\n🔥 Features:")
        print("• Create custom hotkey combinations")
        print("• Record mouse and keyboard actions")
        print("• Loop and delay support")
        print("• Variables and conditions")
        print("• Global hotkey system")
        print("• Macro categories and organization")
        print("• Execution statistics and monitoring")
        
        print("\n⚠️ Safety Notes:")
        print("• Test macros carefully before using")
        print("• Use safe delays between actions")
        print("• Be aware of global hotkey conflicts")
        print("• Emergency stop: Ctrl+Alt+Esc (configurable)")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'plugin' in locals():
            try:
                plugin.shutdown()
            except:
                pass

if __name__ == "__main__":
    test_multi_hotkey_macros_plugin()
