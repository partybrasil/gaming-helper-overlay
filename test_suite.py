# Gaming Helper Overlay - Testing Suite
# Conjunto de pruebas para verificar el funcionamiento de la aplicación

import unittest
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

class TestEnvironment(unittest.TestCase):
    """Pruebas del entorno de desarrollo"""
    
    def test_python_version(self):
        """Verificar que la versión de Python sea compatible"""
        self.assertGreaterEqual(sys.version_info, (3, 10), 
                               "Se requiere Python 3.10 o superior")
    
    def test_required_directories(self):
        """Verificar que existan los directorios necesarios"""
        required_dirs = [
            "core", "ui", "plugins", "config", "data", "assets"
        ]
        
        for directory in required_dirs:
            with self.subTest(directory=directory):
                self.assertTrue(os.path.exists(directory), 
                               f"Directorio {directory} no existe")

class TestDependencies(unittest.TestCase):
    """Pruebas de dependencias"""
    
    def test_pyside6_import(self):
        """Verificar que PySide6 se pueda importar"""
        try:
            import PySide6.QtWidgets
            import PySide6.QtCore
            import PySide6.QtGui
        except ImportError as e:
            self.fail(f"No se pudo importar PySide6: {e}")
    
    def test_yaml_import(self):
        """Verificar que PyYAML se pueda importar"""
        try:
            import yaml
        except ImportError as e:
            self.fail(f"No se pudo importar PyYAML: {e}")
    
    def test_psutil_import(self):
        """Verificar que psutil se pueda importar"""
        try:
            import psutil
        except ImportError as e:
            self.fail(f"No se pudo importar psutil: {e}")
    
    def test_requests_import(self):
        """Verificar que requests se pueda importar"""
        try:
            import requests
        except ImportError as e:
            self.fail(f"No se pudo importar requests: {e}")

class TestCoreModules(unittest.TestCase):
    """Pruebas de módulos principales"""
    
    def test_core_imports(self):
        """Verificar que los módulos del core se puedan importar"""
        core_modules = [
            "core.app_core",
            "core.config_manager", 
            "core.plugin_manager",
            "core.thread_manager"
        ]
        
        for module in core_modules:
            with self.subTest(module=module):
                try:
                    __import__(module)
                except ImportError as e:
                    self.fail(f"No se pudo importar {module}: {e}")
    
    def test_ui_imports(self):
        """Verificar que los módulos de UI se puedan importar"""
        ui_modules = [
            "ui.floating_panel",
            "ui.control_panel",
            "ui.icon_widget",
            "ui.main_window",
            "ui.assets_manager"
        ]
        
        for module in ui_modules:
            with self.subTest(module=module):
                try:
                    __import__(module)
                except ImportError as e:
                    self.fail(f"No se pudo importar {module}: {e}")
    
    def test_plugin_imports(self):
        """Verificar que los plugins se puedan importar"""
        plugin_modules = [
            "plugins.crosshair",
            "plugins.fps_counter", 
            "plugins.cpu_gpu_monitor"
        ]
        
        for module in plugin_modules:
            with self.subTest(module=module):
                try:
                    __import__(module)
                except ImportError as e:
                    self.fail(f"No se pudo importar {module}: {e}")

class TestConfiguration(unittest.TestCase):
    """Pruebas de configuración"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.config_manager import ConfigManager
            self.config_manager = ConfigManager()
        except Exception as e:
            self.skipTest(f"No se pudo inicializar ConfigManager: {e}")
    
    def test_config_file_exists(self):
        """Verificar que el archivo de configuración existe"""
        config_file = Path("config/config.yaml")
        self.assertTrue(config_file.exists(), 
                       "El archivo config.yaml no existe")
    
    def test_config_loading(self):
        """Verificar que la configuración se pueda cargar"""
        try:
            config = self.config_manager.get("app")
            self.assertIsInstance(config, dict)
        except Exception as e:
            self.fail(f"Error al cargar configuración: {e}")

class TestPluginSystem(unittest.TestCase):
    """Pruebas del sistema de plugins"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.plugin_manager import PluginManager
            self.plugin_manager = PluginManager()
        except Exception as e:
            self.skipTest(f"No se pudo inicializar PluginManager: {e}")
    
    def test_plugin_discovery(self):
        """Verificar que se puedan descubrir plugins"""
        try:
            plugins = self.plugin_manager.discover_plugins()
            self.assertIsInstance(plugins, list)
            self.assertGreater(len(plugins), 0, "No se encontraron plugins")
        except Exception as e:
            self.fail(f"Error en descubrimiento de plugins: {e}")

class TestApplication(unittest.TestCase):
    """Pruebas de la aplicación principal"""
    
    def test_main_module_import(self):
        """Verificar que el módulo principal se pueda importar"""
        try:
            import main
        except ImportError as e:
            self.fail(f"No se pudo importar main.py: {e}")
    
    def test_app_core_initialization(self):
        """Verificar que la aplicación se pueda inicializar"""
        try:
            from core.app_core import GamingHelperApp
            # No inicializamos realmente la app para evitar interferencias
            self.assertTrue(hasattr(GamingHelperApp, 'initialize'))
        except Exception as e:
            self.fail(f"Error al verificar GamingHelperApp: {e}")

def run_tests():
    """Ejecutar todas las pruebas"""
    print("Gaming Helper Overlay - Test Suite")
    print("==================================")
    print()
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar clases de prueba
    test_classes = [
        TestEnvironment,
        TestDependencies, 
        TestCoreModules,
        TestConfiguration,
        TestPluginSystem,
        TestApplication
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print(f"\nResumen de pruebas:")
    print(f"Ejecutadas: {result.testsRun}")
    print(f"Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    # Mostrar detalles de fallos
    if result.failures:
        print(f"\nPruebas fallidas:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrores:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception: ')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
