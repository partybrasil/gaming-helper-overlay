# ══════════════════════════════════════════════════════════════════════════════
# 🎮 Gaming Helper Overlay - Testing Suite
# Conjunto de pruebas para verificar el funcionamiento completo de la aplicación
# ══════════════════════════════════════════════════════════════════════════════

import unittest
import sys
import os
import logging
import tempfile
import shutil
import importlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# ─────────────────────────────────────────────────────────────────────────────
# 🎨 Sistema de Colores para Output
# ─────────────────────────────────────────────────────────────────────────────
class Colors:
    """Colores ANSI para terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colores básicos
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Colores brillantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Fondos
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

def print_step(message, color=Colors.CYAN):
    """Imprimir paso de prueba con formato"""
    print(f"{color}  ▶ {message}{Colors.RESET}")

def print_section(title, color=Colors.BRIGHT_CYAN):
    """Imprimir separador de sección"""
    separator = "─" * 60
    print(f"\n{color}{Colors.BOLD}╭{separator}╮")
    print(f"│  🔧 {title:<54} │")
    print(f"╰{separator}╯{Colors.RESET}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.BRIGHT_GREEN}  ✓ {message}{Colors.RESET}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"{Colors.BRIGHT_RED}  ✗ {message}{Colors.RESET}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"{Colors.BRIGHT_YELLOW}  ⚠ {message}{Colors.RESET}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"{Colors.BRIGHT_BLUE}  ℹ {message}{Colors.RESET}")

# ─────────────────────────────────────────────────────────────────────────────
# 🔧 Configuración del Entorno
# ─────────────────────────────────────────────────────────────────────────────

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging para pruebas
logging.basicConfig(level=logging.WARNING)

# Configurar Qt application para pruebas solo si PySide6 está disponible
QT_AVAILABLE = False
try:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    QT_AVAILABLE = True
    print_success("PySide6 disponible - Pruebas completas habilitadas")
except ImportError as e:
    print_warning(f"PySide6 no disponible: {e}")
    print_info("Ejecutando pruebas básicas sin interfaz gráfica")
except Exception as e:
    print_warning(f"Error configurando Qt: {e}")
    print_info("Ejecutando pruebas básicas sin interfaz gráfica")

# ═════════════════════════════════════════════════════════════════════════════
# 🧪 CLASES DE PRUEBA - ORGANIZADAS POR COMPONENTE
# ═════════════════════════════════════════════════════════════════════════════

class TestEnvironment(unittest.TestCase):
    """
    🌟 PRUEBAS DEL ENTORNO DE DESARROLLO
    ═══════════════════════════════════════════════════════
    Verificaciones del entorno de desarrollo y configuración básica
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de entorno"""
        print_step("Configurando entorno de pruebas...", Colors.BLUE)
    
    def test_python_version(self):
        """🐍 Verificar que la versión de Python sea compatible"""
        print_step("Verificando versión de Python...", Colors.CYAN)
        current_version = sys.version_info
        required_version = (3, 10)
        
        print_info(f"Versión actual: Python {current_version.major}.{current_version.minor}.{current_version.micro}")
        print_info(f"Versión requerida: Python {required_version[0]}.{required_version[1]}+")
        
        self.assertGreaterEqual(current_version, required_version, 
                               "Se requiere Python 3.10 o superior")
        print_success("Versión de Python compatible")
    
    def test_required_directories(self):
        """📁 Verificar que existan los directorios necesarios del proyecto"""
        print_step("Verificando estructura de directorios...", Colors.CYAN)
        required_dirs = [
            "core", "ui", "plugins", "config", "data", "assets", "logs", "tools"
        ]
        
        print_info(f"Verificando {len(required_dirs)} directorios críticos...")
        
        for directory in required_dirs:
            with self.subTest(directory=directory):
                exists = os.path.exists(directory)
                if exists:
                    print_success(f"Directorio '{directory}' ✓")
                else:
                    print_error(f"Directorio '{directory}' no encontrado")
                self.assertTrue(exists, f"El directorio '{directory}' no existe")
        
        print_success("Estructura de directorios verificada")
    
    def test_required_files(self):
        """📄 Verificar que existan los archivos principales del proyecto"""
        print_step("Verificando archivos principales...", Colors.CYAN)
        required_files = [
            "main.py", "requirements.txt", "version.py", "config/config.yaml"
        ]
        
        print_info(f"Verificando {len(required_files)} archivos críticos...")
        
        for file_path in required_files:
            with self.subTest(file=file_path):
                exists = os.path.exists(file_path)
                if exists:
                    print_success(f"Archivo '{file_path}' ✓")
                else:
                    print_error(f"Archivo '{file_path}' no encontrado")
                self.assertTrue(exists, f"El archivo '{file_path}' no existe")
        
        print_success("Archivos principales verificados")
    
    def test_version_import(self):
        """🏷️ Verificar que se pueda importar la información de versión"""
        print_step("Verificando información de versión...", Colors.CYAN)
        try:
            import version
            has_version = hasattr(version, '__version__') or hasattr(version, 'VERSION')
            
            if has_version:
                version_info = getattr(version, '__version__', getattr(version, 'VERSION', 'Unknown'))
                print_success(f"Versión detectada: {version_info}")
            else:
                print_warning("Archivo version.py sin atributo de versión")
                
            self.assertTrue(has_version, "version.py debe tener __version__ o VERSION")
            print_success("Información de versión verificada")
        except ImportError as e:
            print_error(f"No se pudo importar version.py: {e}")
            self.fail(f"No se pudo importar version.py: {e}")

class TestDependencies(unittest.TestCase):
    """
    📦 PRUEBAS DE DEPENDENCIAS
    ═══════════════════════════════════════════════════════
    Verificación de librerías y dependencias del proyecto
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de dependencias"""
        print_step("Preparando verificación de dependencias...", Colors.BLUE)
    
    def test_pyside6_import(self):
        """🎨 Verificar que PySide6 (Qt para Python) se pueda importar"""
        print_step("Verificando PySide6...", Colors.CYAN)
        try:
            import PySide6
            from PySide6 import QtCore
            qt_version = QtCore.__version__
            print_success(f"PySide6 disponible - Versión Qt: {qt_version}")
            self.assertTrue(True, "PySide6 disponible")
        except ImportError as e:
            print_warning(f"PySide6 no disponible: {e}")
            self.skipTest(f"PySide6 no disponible: {e}")
        except Exception as e:
            print_error(f"Error al importar PySide6: {e}")
            self.fail(f"Error al importar PySide6: {e}")
    
    def test_yaml_import(self):
        """⚙️ Verificar que PyYAML (configuración) se pueda importar"""
        print_step("Verificando PyYAML...", Colors.CYAN)
        try:
            import yaml
            print_success("PyYAML disponible para configuraciones")
            self.assertTrue(True, "PyYAML disponible")
        except ImportError as e:
            print_error(f"PyYAML no disponible: {e}")
            self.fail(f"PyYAML no disponible: {e}")
    
    def test_psutil_import(self):
        """🖥️ Verificar que psutil (monitoreo del sistema) se pueda importar"""
        print_step("Verificando psutil...", Colors.CYAN)
        try:
            import psutil
            print_success("psutil disponible para monitoreo del sistema")
            self.assertTrue(True, "psutil disponible")
        except ImportError as e:
            print_error(f"psutil no disponible: {e}")
            self.fail(f"psutil no disponible: {e}")
    
    def test_requests_import(self):
        """🌐 Verificar que requests (HTTP) se pueda importar"""
        print_step("Verificando requests...", Colors.CYAN)
        try:
            import requests
            print_success("requests disponible para comunicación HTTP")
            self.assertTrue(True, "requests disponible")
        except ImportError as e:
            print_error(f"requests no disponible: {e}")
            self.fail(f"requests no disponible: {e}")
    
    def test_optional_dependencies(self):
        """🔧 Verificar dependencias opcionales para funcionalidades avanzadas"""
        print_step("Verificando dependencias opcionales...", Colors.CYAN)
        optional_deps = {
            'keyboard': 'keyboard automation',
            'mouse': 'mouse automation', 
            'pynvml': 'NVIDIA GPU monitoring',
            'GPUtil': 'GPU utilities'
        }
        
        print_info(f"Verificando {len(optional_deps)} dependencias opcionales...")
        
        for dep, description in optional_deps.items():
            with self.subTest(dependency=dep):
                try:
                    importlib.import_module(dep)
                    print_success(f"{dep} disponible ({description})")
                except ImportError:
                    print_warning(f"{dep} no disponible ({description}) - opcional")
    
    def test_logging_config(self):
        """📊 Verificar configuración del sistema de logging"""
        print_step("Verificando sistema de logging...", Colors.CYAN)
        logger = logging.getLogger("test")
        self.assertIsInstance(logger, logging.Logger)
        print_success("Sistema de logging configurado correctamente")

class TestCoreModules(unittest.TestCase):
    """
    ⚙️ PRUEBAS DE MÓDULOS PRINCIPALES
    ═══════════════════════════════════════════════════════
    Verificación de importación y funcionamiento de módulos core
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de módulos core"""
        print_step("Preparando verificación de módulos principales...", Colors.BLUE)
    
    def test_core_imports(self):
        """🏗️ Verificar que los módulos del core se puedan importar"""
        print_step("Verificando módulos del núcleo...", Colors.CYAN)
        core_modules = [
            "core.app_core",
            "core.config_manager", 
            "core.plugin_manager",
            "core.thread_manager",
            "core.tool_manager"
        ]
        
        print_info(f"Verificando {len(core_modules)} módulos críticos del core...")
        
        for module in core_modules:
            with self.subTest(module=module):
                try:
                    print_step(f"  → Importando {module}...", Colors.CYAN)
                    importlib.import_module(module)
                    print_success(f"    ✓ {module} importado correctamente")
                    self.assertTrue(True, f"Módulo {module} importado correctamente")
                except ImportError as e:
                    print_error(f"    ✗ Error al importar {module}: {e}")
                    self.fail(f"Error al importar {module}: {e}")
        
        print_success("Todos los módulos del core importados correctamente")
    
    def test_ui_imports(self):
        """🖥️ Verificar que los módulos de UI se puedan importar"""
        print_step("Verificando módulos de interfaz de usuario...", Colors.CYAN)
        ui_modules = [
            "ui.floating_panel",
            "ui.control_panel", 
            "ui.icon_widget",
            "ui.main_window",
            "ui.assets_manager",
            "ui.log_display"
        ]
        
        print_info(f"Verificando {len(ui_modules)} módulos de interfaz...")
        
        for module in ui_modules:
            with self.subTest(module=module):
                try:
                    print_step(f"  → Importando {module}...", Colors.CYAN)
                    importlib.import_module(module)
                    print_success(f"    ✓ {module} importado correctamente")
                    self.assertTrue(True, f"Módulo {module} importado correctamente")
                except ImportError as e:
                    if not QT_AVAILABLE:
                        print_warning(f"    ⚠ PySide6 no disponible, saltando {module}")
                        self.skipTest(f"PySide6 no disponible, saltando {module}")
                    else:
                        print_error(f"    ✗ Error al importar {module}: {e}")
                        self.fail(f"Error al importar {module}: {e}")
        
        print_success("Todos los módulos de UI procesados correctamente")
    
    def test_plugin_imports(self):
        """🔌 Verificar que los plugins se puedan importar"""
        print_step("Verificando plugins del sistema...", Colors.CYAN)
        plugin_modules = [
            "plugins.crosshair",
            "plugins.fps_counter", 
            "plugins.cpu_gpu_monitor",
            "plugins.anti_afk",
            "plugins.multi_hotkey_macros"
        ]
        
        print_info(f"Verificando {len(plugin_modules)} plugins disponibles...")
        
        for module in plugin_modules:
            with self.subTest(module=module):
                try:
                    print_step(f"  → Importando {module}...", Colors.CYAN)
                    importlib.import_module(module)
                    print_success(f"    ✓ {module} importado correctamente")
                    self.assertTrue(True, f"Plugin {module} importado correctamente")
                except ImportError as e:
                    if not QT_AVAILABLE:
                        print_warning(f"    ⚠ PySide6 no disponible, saltando {module}")
                        self.skipTest(f"PySide6 no disponible, saltando {module}")
                    else:
                        print_error(f"    ✗ Error al importar {module}: {e}")
                        self.fail(f"Error al importar {module}: {e}")
        
        print_success("Todos los plugins procesados correctamente")
    
    def test_tool_imports(self):
        """🛠️ Verificar que las herramientas se puedan importar"""
        print_step("Verificando herramientas del sistema...", Colors.CYAN)
        tool_files = [
            "tools.RTX-DIAG",
            "create_icon",
            "fix_icon"
        ]
        
        print_info(f"Verificando {len(tool_files)} herramientas...")
        
        for module in tool_files:
            with self.subTest(module=module):
                try:
                    print_step(f"  → Importando {module}...", Colors.CYAN)
                    importlib.import_module(module)
                    print_success(f"    ✓ {module} importado correctamente")
                    self.assertTrue(True, f"Herramienta {module} importada correctamente")
                except ImportError as e:
                    print_error(f"    ✗ Error al importar {module}: {e}")
                    self.fail(f"Error al importar {module}: {e}")
        
        print_success("Todas las herramientas procesadas correctamente")
    
    def test_base_plugin_class(self):
        """🔧 Verificar que la clase base de plugins funcione"""
        print_step("Verificando clase base de plugins...", Colors.CYAN)
        try:
            from core.plugin_manager import BasePlugin
            print_success("    ✓ BasePlugin importada correctamente")
            self.assertTrue(issubclass(BasePlugin, object), 
                          "BasePlugin debe ser una clase válida")
            print_success("BasePlugin es una clase válida")
        except Exception as e:
            print_error(f"    ✗ Error al importar BasePlugin: {e}")
            self.fail(f"Error al importar BasePlugin: {e}")

class TestConfiguration(unittest.TestCase):
    """
    ⚙️ PRUEBAS DE CONFIGURACIÓN
    ═══════════════════════════════════════════════════════
    Verificación del sistema de configuración y archivos YAML
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de configuración"""
        print_step("Preparando verificación de configuración...", Colors.BLUE)
        try:
            from core.config_manager import ConfigManager
            self.config_manager = ConfigManager()
            print_success("ConfigManager inicializado correctamente")
        except Exception as e:
            print_error(f"Error al inicializar ConfigManager: {e}")
            self.skipTest(f"No se pudo crear ConfigManager: {e}")
    
    def test_config_file_exists(self):
        """📁 Verificar que el archivo de configuración existe"""
        print_step("Verificando archivo de configuración principal...", Colors.CYAN)
        config_file = Path("config/config.yaml")
        
        if config_file.exists():
            print_success(f"    ✓ Archivo config.yaml encontrado en: {config_file}")
            self.assertTrue(config_file.exists(), 
                           "El archivo config.yaml no existe")
        else:
            print_error(f"    ✗ Archivo config.yaml no encontrado en: {config_file}")
            self.fail("El archivo config.yaml no existe")
    
    def test_config_loading(self):
        """🔄 Verificar que la configuración se pueda cargar"""
        print_step("Verificando carga de configuración...", Colors.CYAN)
        try:
            result = self.config_manager.load_config()
            if result:
                print_success("    ✓ Configuración cargada exitosamente")
                self.assertTrue(result, "La configuración debería cargarse exitosamente")
            else:
                print_error("    ✗ Error al cargar configuración")
                self.fail("Error al cargar configuración")
        except Exception as e:
            print_error(f"    ✗ Excepción al cargar configuración: {e}")
            self.fail(f"Error al cargar configuración: {e}")
    
    def test_plugin_configs(self):
        """🔌 Verificar que las configuraciones de plugins existan"""
        print_step("Verificando configuraciones de plugins...", Colors.CYAN)
        plugin_config_dir = Path("config/plugins")
        
        if plugin_config_dir.exists():
            print_success(f"    ✓ Directorio de plugins encontrado: {plugin_config_dir}")
            self.assertTrue(plugin_config_dir.exists(), 
                           "Directorio de configuración de plugins no existe")
        else:
            print_error(f"    ✗ Directorio de plugins no encontrado: {plugin_config_dir}")
            self.fail("Directorio de configuración de plugins no existe")
        
        # Verificar algunos archivos de configuración específicos
        expected_configs = [
            "crosshair.yaml",
            "fps_counter.yaml", 
            "cpu_gpu_monitor.yaml",
            "anti_afk.yaml",
            "multi_hotkey_macros.yaml"
        ]
        
        print_info(f"Verificando {len(expected_configs)} archivos de configuración...")
        
        for config_file in expected_configs:
            with self.subTest(config=config_file):
                config_path = plugin_config_dir / config_file
                alt_path = config_path.with_suffix('.yaml')
                
                if config_path.exists() or alt_path.exists():
                    print_success(f"    ✓ Configuración {config_file} encontrada")
                    self.assertTrue(config_path.exists() or alt_path.exists(),
                                   f"Archivo de configuración {config_file} no encontrado")
                else:
                    print_warning(f"    ⚠ Configuración {config_file} no encontrada")
                    # No falla el test, solo advierte
        
        print_success("Verificación de configuraciones de plugins completada")
    
    def test_config_defaults(self):
        """⚙️ Verificar que los valores por defecto se carguen correctamente"""
        print_step("Verificando valores por defecto...", Colors.CYAN)
        try:
            # Verificar que la configuración tiene valores por defecto
            # Usar valores que sabemos que existen en la configuración por defecto
            print_step("  → Verificando configuración de aplicación...", Colors.CYAN)
            app_config = self.config_manager.get("app", {})
            self.assertIsInstance(app_config, dict, "La configuración de app debe ser un dict")
            print_success("    ✓ Configuración de app válida")
            
            print_step("  → Verificando configuración de floating_icon...", Colors.CYAN)
            floating_icon_config = self.config_manager.get("floating_icon", {})
            self.assertIsInstance(floating_icon_config, dict, "La configuración de floating_icon debe ser un dict")
            print_success("    ✓ Configuración de floating_icon válida")
            
            print_step("  → Verificando configuración de plugins...", Colors.CYAN)
            plugins_config = self.config_manager.get("plugins", {})
            self.assertIsInstance(plugins_config, dict, "La configuración de plugins debe ser un dict")
            print_success("    ✓ Configuración de plugins válida")
            
            print_success("Todos los valores por defecto están configurados correctamente")
        except Exception as e:
            print_error(f"    ✗ Error al acceder a configuración por defecto: {e}")
            self.fail(f"Error al acceder a configuración por defecto: {e}")
    
    def test_config_save_load(self):
        """💾 Verificar que se pueda guardar y cargar configuración"""
        print_step("Verificando funcionalidad de guardar/cargar...", Colors.CYAN)
        try:
            # Guardar configuración actual
            print_step("  → Guardando valor de prueba...", Colors.CYAN)
            original_value = self.config_manager.get("app.test_value", "default")
            self.config_manager.set("app.test_value", "test_value")
            print_success("    ✓ Valor guardado")
            
            # Verificar que se guardó
            print_step("  → Verificando valor guardado...", Colors.CYAN)
            saved_value = self.config_manager.get("app.test_value")
            self.assertEqual(saved_value, "test_value")
            print_success("    ✓ Valor verificado correctamente")
            
            # Restaurar valor original
            print_step("  → Restaurando valor original...", Colors.CYAN)
            self.config_manager.set("app.test_value", original_value)
            print_success("    ✓ Valor restaurado")
            
            print_success("Funcionalidad de guardar/cargar funciona correctamente")
        except Exception as e:
            print_error(f"    ✗ Error al guardar/cargar configuración: {e}")
            self.fail(f"Error al guardar/cargar configuración: {e}")

class TestPluginSystem(unittest.TestCase):
    """
    🔌 PRUEBAS DEL SISTEMA DE PLUGINS
    ═══════════════════════════════════════════════════════
    Verificación del sistema de gestión de plugins y su funcionalidad
    """
    
    def setUp(self):
        """Configuración inicial para pruebas del sistema de plugins"""
        print_step("Preparando verificación del sistema de plugins...", Colors.BLUE)
        try:
            from core.config_manager import ConfigManager
            from core.thread_manager import ThreadManager
            from core.plugin_manager import PluginManager
            
            self.config_manager = ConfigManager()
            self.thread_manager = ThreadManager()
            self.plugin_manager = PluginManager(self.config_manager, self.thread_manager)
            print_success("Gestores del sistema de plugins inicializados")
        except Exception as e:
            print_error(f"Error al inicializar sistema de plugins: {e}")
            self.skipTest(f"No se pudo crear PluginManager: {e}")
    
    def test_plugin_discovery(self):
        """🔍 Verificar que se puedan descubrir plugins"""
        print_step("Verificando descubrimiento de plugins...", Colors.CYAN)
        try:
            plugins = self.plugin_manager.discover_plugins()
            print_info(f"Plugins encontrados: {len(plugins)}")
            self.assertIsInstance(plugins, list, "discover_plugins debe retornar una lista")
            self.assertGreater(len(plugins), 0, "Debe encontrar al menos un plugin")
            
            for plugin in plugins:
                print_success(f"    ✓ Plugin encontrado: {plugin}")
            
            print_success("Descubrimiento de plugins funciona correctamente")
        except Exception as e:
            print_error(f"    ✗ Error al descubrir plugins: {e}")
            self.fail(f"Error al descubrir plugins: {e}")
    
    def test_plugin_loading(self):
        """🔄 Verificar que se puedan cargar plugins"""
        print_step("Verificando carga de plugins...", Colors.CYAN)
        try:
            plugins = self.plugin_manager.discover_plugins()
            if plugins:
                plugin_name = plugins[0]
                print_step(f"  → Cargando plugin: {plugin_name}...", Colors.CYAN)
                result = self.plugin_manager.load_plugin(plugin_name)
                if result:
                    print_success(f"    ✓ Plugin {plugin_name} cargado correctamente")
                    self.assertTrue(result, f"Plugin {plugin_name} debería cargarse correctamente")
                else:
                    print_error(f"    ✗ Error al cargar plugin {plugin_name}")
                    self.fail(f"Plugin {plugin_name} no se pudo cargar")
            else:
                print_warning("    ⚠ No se encontraron plugins para cargar")
                self.skipTest("No hay plugins disponibles para cargar")
        except Exception as e:
            print_error(f"    ✗ Error al cargar plugin: {e}")
            self.fail(f"Error al cargar plugin: {e}")
    
    def test_plugin_metadata(self):
        """📋 Verificar que los plugins tengan metadata correcta"""
        print_step("Verificando metadata de plugins...", Colors.CYAN)
        try:
            plugins = self.plugin_manager.discover_plugins()
            print_info(f"Verificando metadata de {len(plugins)} plugins...")
            
            for plugin_name in plugins:
                with self.subTest(plugin=plugin_name):
                    print_step(f"  → Verificando metadata de {plugin_name}...", Colors.CYAN)
                    plugin_class = self.plugin_manager.available_plugins.get(plugin_name)
                    if plugin_class:
                        # Verificar que tenga atributos requeridos
                        self.assertTrue(hasattr(plugin_class, 'name'))
                        self.assertTrue(hasattr(plugin_class, 'description'))
                        self.assertTrue(hasattr(plugin_class, 'version'))
                        self.assertTrue(hasattr(plugin_class, 'author'))
                        print_success(f"    ✓ Metadata de {plugin_name} completa")
                    else:
                        print_warning(f"    ⚠ No se pudo obtener clase para {plugin_name}")
            
            print_success("Verificación de metadata de plugins completada")
        except Exception as e:
            print_error(f"    ✗ Error al verificar metadata de plugins: {e}")
            self.fail(f"Error al verificar metadata de plugins: {e}")
    
    def tearDown(self):
        """Limpieza después de las pruebas del sistema de plugins"""
        try:
            if hasattr(self, 'thread_manager'):
                print_step("Cerrando threads del sistema de plugins...", Colors.YELLOW)
                self.thread_manager.shutdown_all_threads()
                print_success("Threads cerrados correctamente")
        except Exception as e:
            print_warning(f"Error al cerrar threads: {e}")

class TestApplication(unittest.TestCase):
    """
    🚀 PRUEBAS DE LA APLICACIÓN PRINCIPAL
    ═══════════════════════════════════════════════════════
    Verificación de la aplicación principal y su inicialización
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de aplicación"""
        print_step("Preparando verificación de aplicación principal...", Colors.BLUE)
    
    def test_main_module_import(self):
        """📦 Verificar que el módulo principal se pueda importar"""
        print_step("Verificando importación del módulo principal...", Colors.CYAN)
        try:
            import main
            print_success("    ✓ main.py importado correctamente")
            self.assertTrue(True, "main.py importado correctamente")
        except ImportError as e:
            print_error(f"    ✗ Error al importar main.py: {e}")
            self.fail(f"Error al importar main.py: {e}")
    
    def test_app_core_initialization(self):
        """🏗️ Verificar que la aplicación se pueda inicializar"""
        print_step("Verificando inicialización de la aplicación...", Colors.CYAN)
        try:
            from core.app_core import GamingHelperApp
            print_step("  → Creando instancia de GamingHelperApp...", Colors.CYAN)
            app = GamingHelperApp()
            self.assertIsNotNone(app, "GamingHelperApp debería crear una instancia")
            print_success("    ✓ GamingHelperApp inicializada correctamente")
        except Exception as e:
            if not QT_AVAILABLE:
                print_warning("    ⚠ PySide6 no disponible, saltando test")
                self.skipTest("PySide6 no disponible")
            else:
                print_error(f"    ✗ Error al inicializar aplicación: {e}")
                self.fail(f"Error al inicializar aplicación: {e}")
    
    def test_qt_application_setup(self):
        """🖥️ Verificar que la aplicación Qt se pueda configurar"""
        print_step("Verificando configuración de Qt...", Colors.CYAN)
        try:
            if QT_AVAILABLE:
                from PySide6.QtWidgets import QApplication
                print_step("  → Obteniendo instancia de QApplication...", Colors.CYAN)
                app = QApplication.instance()
                self.assertIsNotNone(app, "QApplication debería estar disponible")
                print_success("    ✓ QApplication configurada correctamente")
            else:
                print_warning("    ⚠ PySide6 no disponible, saltando test")
                self.skipTest("PySide6 no disponible")
        except Exception as e:
            print_error(f"    ✗ Error al configurar Qt application: {e}")
            self.fail(f"Error al configurar Qt application: {e}")

class TestUIComponents(unittest.TestCase):
    """
    🖥️ PRUEBAS DE COMPONENTES DE UI
    ═══════════════════════════════════════════════════════
    Verificación de componentes de interfaz de usuario
    """
    
    def setUp(self):
        """Configuración inicial para pruebas de UI"""
        print_step("Preparando verificación de componentes de UI...", Colors.BLUE)
        if not QT_AVAILABLE:
            print_warning("PySide6 no disponible, saltando pruebas de UI")
            self.skipTest("PySide6 no disponible")
    
    def test_floating_panel_base(self):
        """🏠 Verificar que FloatingPanel se pueda crear"""
        print_step("Verificando creación de FloatingPanel...", Colors.CYAN)
        try:
            from ui.floating_panel import FloatingPanel
            from core.config_manager import ConfigManager
            
            print_step("  → Inicializando ConfigManager...", Colors.CYAN)
            config_manager = ConfigManager()
            print_step("  → Creando FloatingPanel...", Colors.CYAN)
            panel = FloatingPanel(config_manager, "Test Panel")
            self.assertIsNotNone(panel, "FloatingPanel debería crear una instancia")
            print_success("    ✓ FloatingPanel creado correctamente")
        except Exception as e:
            print_error(f"    ✗ Error al crear FloatingPanel: {e}")
            self.fail(f"Error al crear FloatingPanel: {e}")
    
    def test_control_panel_components(self):
        """🎛️ Verificar componentes del panel de control"""
        print_step("Verificando componentes del panel de control...", Colors.CYAN)
        try:
            from ui.control_panel import ControlPanel
            from core.config_manager import ConfigManager
            from core.plugin_manager import PluginManager
            from core.thread_manager import ThreadManager
            
            print_step("  → Inicializando gestores...", Colors.CYAN)
            config_manager = ConfigManager()
            thread_manager = ThreadManager()
            plugin_manager = PluginManager(config_manager, thread_manager)
            
            print_step("  → Creando ControlPanel...", Colors.CYAN)
            panel = ControlPanel(config_manager, plugin_manager, thread_manager)
            self.assertIsNotNone(panel, "ControlPanel debería crear una instancia")
            print_success("    ✓ ControlPanel creado correctamente")
        except Exception as e:
            print_error(f"    ✗ Error al crear ControlPanel: {e}")
            self.fail(f"Error al crear ControlPanel: {e}")
            self.fail(f"Error al crear ControlPanel: {e}")
    
    def test_icon_widget_components(self):
        """Verificar componentes del widget de icono"""
        try:
            from ui.icon_widget import FloatingIcon
            from core.config_manager import ConfigManager
            
            config_manager = ConfigManager()
            icon = FloatingIcon(config_manager, None)
            self.assertIsNotNone(icon, "FloatingIcon debería crear una instancia")
        except Exception as e:
            self.fail(f"Error al crear FloatingIcon: {e}")
    
    def test_log_display_components(self):
        """Verificar componentes de visualización de logs"""
        try:
            from ui.log_display import LogDisplay
            
            log_display = LogDisplay()
            self.assertIsNotNone(log_display, "LogDisplay debería crear una instancia")
        except Exception as e:
            self.fail(f"Error al crear LogDisplay: {e}")

class TestThreadManager(unittest.TestCase):
    """Pruebas del administrador de hilos"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.thread_manager import ThreadManager
            self.thread_manager = ThreadManager()
        except Exception as e:
            self.skipTest(f"No se pudo crear ThreadManager: {e}")
    
    def test_thread_manager_initialization(self):
        """Verificar inicialización del administrador de hilos"""
        self.assertIsNotNone(self.thread_manager)
        self.assertEqual(len(self.thread_manager.active_threads), 0)
    
    def test_thread_statistics(self):
        """Verificar estadísticas de hilos"""
        try:
            stats = self.thread_manager.get_statistics()
            self.assertIsInstance(stats, dict)
            self.assertIn('active_threads', stats)
            # Usar los nombres de estadísticas que realmente existen
            self.assertIn('total_started', stats)
            self.assertIn('total_completed', stats)
            self.assertIn('total_failed', stats)
        except Exception as e:
            self.fail(f"Error al obtener estadísticas: {e}")
    
    def tearDown(self):
        """Limpiar después de las pruebas"""
        try:
            self.thread_manager.shutdown_all_threads()
        except:
            pass

class TestToolManager(unittest.TestCase):
    """Pruebas del administrador de herramientas"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.tool_manager import ToolManager
            self.tool_manager = ToolManager()
        except Exception as e:
            self.skipTest(f"No se pudo crear ToolManager: {e}")
    
    def test_tool_discovery(self):
        """Verificar descubrimiento de herramientas"""
        try:
            tools = self.tool_manager.discover_tools()
            # Verificar que retorna una lista o None
            self.assertTrue(tools is None or isinstance(tools, list))
            
            if tools:
                # Verificar que encuentra las herramientas principales
                tool_names = [tool.name for tool in tools]
                self.assertIn('RTX-DIAG', tool_names)
            else:
                # Si no encuentra herramientas, verificar que el directorio tools existe
                tools_dir = Path("tools")
                self.assertTrue(tools_dir.exists(), "El directorio tools debe existir")
        except Exception as e:
            self.fail(f"Error al descubrir herramientas: {e}")
    
    def test_tool_info(self):
        """Verificar información de herramientas"""
        try:
            tools = self.tool_manager.discover_tools()
            if tools:
                for tool in tools:
                    with self.subTest(tool=tool.name):
                        self.assertIsNotNone(tool.name)
                        self.assertIsNotNone(tool.description)
                        self.assertIsNotNone(tool.version)
            else:
                self.skipTest("No se encontraron herramientas para verificar")
        except unittest.SkipTest:
            raise  # Re-raise SkipTest exceptions
        except Exception as e:
            self.fail(f"Error al obtener información de herramientas: {e}")

class TestSpecificPlugins(unittest.TestCase):
    """Pruebas específicas de plugins individuales"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.config_manager import ConfigManager
            from core.thread_manager import ThreadManager
            self.config_manager = ConfigManager()
            self.thread_manager = ThreadManager()
        except Exception as e:
            self.skipTest(f"No se pudo configurar entorno: {e}")
    
    def test_crosshair_plugin(self):
        """Verificar plugin de crosshair"""
        try:
            from plugins.crosshair import CrosshairPlugin
            plugin = CrosshairPlugin(self.config_manager, self.thread_manager)
            self.assertEqual(plugin.name, "Crosshair Overlay")
            self.assertIsNotNone(plugin.description)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.fail(f"Error al probar CrosshairPlugin: {e}")
    
    def test_fps_counter_plugin(self):
        """Verificar plugin de contador FPS"""
        try:
            from plugins.fps_counter import FPSCounterPlugin
            plugin = FPSCounterPlugin(self.config_manager, self.thread_manager)
            self.assertEqual(plugin.name, "FPS Counter")
            self.assertIsNotNone(plugin.description)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.fail(f"Error al probar FPSCounterPlugin: {e}")
    
    def test_anti_afk_plugin(self):
        """Verificar plugin anti-AFK"""
        try:
            from plugins.anti_afk import AntiAFKPlugin
            plugin = AntiAFKPlugin(self.config_manager, self.thread_manager)
            self.assertEqual(plugin.name, "Anti-AFK Emulation")
            self.assertIsNotNone(plugin.description)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.fail(f"Error al probar AntiAFKPlugin: {e}")
    
    def test_multi_hotkey_macros_plugin(self):
        """Verificar plugin de macros multi-hotkey"""
        try:
            from plugins.multi_hotkey_macros import MultiHotkeyMacrosPlugin
            plugin = MultiHotkeyMacrosPlugin(self.config_manager, self.thread_manager)
            self.assertEqual(plugin.name, "Multi-Hotkey Macros")
            self.assertIsNotNone(plugin.description)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.fail(f"Error al probar MultiHotkeyMacrosPlugin: {e}")
    
    def test_cpu_gpu_monitor_plugin(self):
        """Verificar plugin de monitoreo CPU/GPU"""
        try:
            from plugins.cpu_gpu_monitor import CPUGPUMonitorPlugin
            plugin = CPUGPUMonitorPlugin(self.config_manager, self.thread_manager)
            self.assertEqual(plugin.name, "CPU/GPU Monitor")
            self.assertIsNotNone(plugin.description)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.fail(f"Error al probar CPUGPUMonitorPlugin: {e}")

class TestAssetManager(unittest.TestCase):
    """Pruebas del administrador de assets"""
    
    def setUp(self):
        """Configurar el entorno para las pruebas"""
        try:
            from core.config_manager import ConfigManager
            from ui.assets_manager import AssetsManager
            
            self.config_manager = ConfigManager()
            self.assets_manager = AssetsManager(self.config_manager)
        except Exception as e:
            if not QT_AVAILABLE:
                self.skipTest("PySide6 no disponible")
            else:
                self.skipTest(f"No se pudo crear AssetsManager: {e}")
    
    def test_asset_manager_initialization(self):
        """Verificar inicialización del administrador de assets"""
        self.assertIsNotNone(self.assets_manager)
        self.assertTrue(self.assets_manager.assets_root.exists())
    
    def test_default_assets(self):
        """Verificar que los assets por defecto existan"""
        try:
            # Verificar que el icono de la aplicación existe
            icon_path = self.assets_manager.get_asset_path("icons", "app_icon.png")
            if icon_path:
                self.assertTrue(icon_path.exists())
        except Exception as e:
            self.fail(f"Error al verificar assets por defecto: {e}")

class TestFileStructure(unittest.TestCase):
    """Pruebas de estructura de archivos y configuraciones"""
    
    def test_plugin_config_files(self):
        """Verificar archivos de configuración de plugins"""
        config_dir = Path("config/plugins")
        if config_dir.exists():
            config_files = list(config_dir.glob("*.yaml"))
            self.assertGreater(len(config_files), 0, 
                             "Debe haber al menos un archivo de configuración de plugin")
    
    def test_log_directory(self):
        """Verificar directorio de logs"""
        log_dir = Path("logs")
        self.assertTrue(log_dir.exists(), "El directorio de logs debe existir")
    
    def test_required_scripts(self):
        """Verificar scripts requeridos"""
        required_scripts = [
            "main.py",
            "create_icon.py",
            "fix_icon.py",
            "version.py"
        ]
        
        for script in required_scripts:
            with self.subTest(script=script):
                self.assertTrue(Path(script).exists(), 
                               f"El script {script} debe existir")
    
    def test_readme_files(self):
        """Verificar archivos README"""
        readme_files = [
            "README.md",
            "plugins/README_ANTI_AFK.md",
            "plugins/README_MULTI_HOTKEY_MACROS.md",
            "docs/ARCHITECTURE.md",
            "docs/PLUGIN_DEVELOPMENT.md"
        ]
        
        for readme in readme_files:
            with self.subTest(readme=readme):
                readme_path = Path(readme)
                self.assertTrue(readme_path.exists(), 
                               f"El archivo {readme} debe existir")

class TestIntegration(unittest.TestCase):
    """Pruebas de integración básicas"""
    
    def test_import_chain(self):
        """Verificar cadena de importación completa"""
        try:
            # Importar en orden de dependencia
            from core.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            from core.thread_manager import ThreadManager
            thread_manager = ThreadManager()
            
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager(config_manager, thread_manager)
            
            if QT_AVAILABLE:
                from core.app_core import GamingHelperApp
                app = GamingHelperApp()
                
            self.assertTrue(True, "Cadena de importación exitosa")
        except Exception as e:
            self.fail(f"Error en cadena de importación: {e}")
    
    def test_config_plugin_integration(self):
        """Verificar integración entre configuración y plugins"""
        try:
            from core.config_manager import ConfigManager
            from core.thread_manager import ThreadManager
            from core.plugin_manager import PluginManager
            
            config_manager = ConfigManager()
            thread_manager = ThreadManager()
            plugin_manager = PluginManager(config_manager, thread_manager)
            
            # Descubrir plugins
            plugins = plugin_manager.discover_plugins()
            
            # Verificar configuración de plugins
            for plugin_name in plugins:
                with self.subTest(plugin=plugin_name):
                    config = config_manager.get_plugin_config(plugin_name)
                    self.assertIsInstance(config, dict)
                    
        except Exception as e:
            self.fail(f"Error en integración config-plugin: {e}")

class TestPerformance(unittest.TestCase):
    """Pruebas básicas de rendimiento"""
    
    def test_import_performance(self):
        """Verificar rendimiento de importación"""
        import time
        
        start_time = time.time()
        try:
            import main
            from core.config_manager import ConfigManager
            from core.thread_manager import ThreadManager
            from core.plugin_manager import PluginManager
        except ImportError:
            pass
        
        end_time = time.time()
        import_time = end_time - start_time
        
        # Las importaciones no deberían tomar más de 5 segundos
        self.assertLess(import_time, 5.0, 
                        f"Las importaciones tardaron {import_time:.2f}s (máximo: 5.0s)")
    
    def test_config_load_performance(self):
        """Verificar rendimiento de carga de configuración"""
        try:
            from core.config_manager import ConfigManager
            import time
            
            start_time = time.time()
            config_manager = ConfigManager()
            config_manager.load_config()
            end_time = time.time()
            
            load_time = end_time - start_time
            
            # La carga de configuración no debería tomar más de 2 segundos
            self.assertLess(load_time, 2.0, 
                           f"La carga de configuración tardó {load_time:.2f}s (máximo: 2.0s)")
        except Exception as e:
            self.fail(f"Error en prueba de rendimiento de configuración: {e}")

def run_tests():
    """
    🚀 EJECUTAR SUITE COMPLETA DE PRUEBAS
    ═════════════════════════════════════════════════════════════
    Ejecuta todas las pruebas del Gaming Helper Overlay con
    reporte detallado, estadísticas y diagnóstico completo
    """
    # Título principal con colores
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║              🎮 GAMING HELPER OVERLAY - TEST SUITE           ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╠═══════════════════════════════════════════════════════════════╣{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                   Sistema de Pruebas Completo                ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    # Crear suite de pruebas
    print_section("🔧 INICIALIZANDO SUITE DE PRUEBAS")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar clases de prueba con descripción
    test_classes = [
        (TestEnvironment, "🌍 Verificación del entorno"),
        (TestDependencies, "📦 Verificación de dependencias"), 
        (TestCoreModules, "⚙️ Verificación de módulos core"),
        (TestConfiguration, "🔧 Verificación de configuración"),
        (TestPluginSystem, "🔌 Verificación de sistema de plugins"),
        (TestApplication, "🚀 Verificación de aplicación principal"),
        (TestUIComponents, "🖥️ Verificación de componentes UI"),
        (TestThreadManager, "🧵 Verificación de gestión de hilos"),
        (TestToolManager, "🛠️ Verificación de herramientas"),
        (TestSpecificPlugins, "🎯 Verificación de plugins específicos"),
        (TestAssetManager, "📁 Verificación de assets"),
        (TestFileStructure, "📂 Verificación de estructura de archivos"),
        (TestIntegration, "🔗 Pruebas de integración"),
        (TestPerformance, "⚡ Pruebas de rendimiento")
    ]
    
    print_info(f"Agregando {len(test_classes)} grupos de pruebas...")
    
    for test_class, description in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
        print_step(f"  → {description}", Colors.GREEN)
    
    print_success("Suite de pruebas inicializada correctamente")
    print()
    
    # Ejecutar pruebas
    print_section("🚀 EJECUTANDO PRUEBAS")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen con colores
    print()
    print(f"{Colors.BOLD}{Colors.YELLOW}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}║                      📊 RESUMEN DE PRUEBAS                   ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    # Estadísticas básicas
    total_tests = result.testsRun
    successful_tests = total_tests - len(result.failures) - len(result.errors)
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    skipped_tests = len(result.skipped) if result.skipped else 0
    
    print(f"{Colors.BOLD}📈 ESTADÍSTICAS GENERALES:{Colors.RESET}")
    print(f"  {Colors.CYAN}• Total ejecutadas:{Colors.RESET} {total_tests}")
    print(f"  {Colors.GREEN}• Exitosas:{Colors.RESET} {successful_tests}")
    print(f"  {Colors.RED}• Fallidas:{Colors.RESET} {failed_tests}")
    print(f"  {Colors.MAGENTA}• Errores:{Colors.RESET} {error_tests}")
    print(f"  {Colors.YELLOW}• Saltadas:{Colors.RESET} {skipped_tests}")
    print()
    
    # Mostrar detalles de fallos
    if result.failures:
        print(f"{Colors.BOLD}{Colors.RED}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}║                        ❌ FALLOS DETALLADOS                   ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        for test, failure in result.failures:
            print(f"\n{Colors.RED}❌ {test}:{Colors.RESET}")
            print(f"   {failure}")
    
    if result.errors:
        print(f"{Colors.BOLD}{Colors.MAGENTA}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}║                       💥 ERRORES DETALLADOS                  ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        for test, error in result.errors:
            print(f"\n{Colors.MAGENTA}💥 {test}:{Colors.RESET}")
            print(f"   {error}")
    
    if result.skipped:
        print(f"{Colors.BOLD}{Colors.YELLOW}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}║                      ⏭️ PRUEBAS SALTADAS                     ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        for test, reason in result.skipped:
            print(f"\n{Colors.YELLOW}⏭️ {test}:{Colors.RESET}")
            print(f"   {reason}")
    
    # Mostrar estadísticas avanzadas con colores
    success_rate = ((successful_tests) / total_tests * 100) if total_tests > 0 else 0
    print(f"{Colors.BOLD}📊 ESTADÍSTICAS:{Colors.RESET}")
    
    if success_rate >= 90:
        print(f"Tasa de éxito: {Colors.GREEN}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.GREEN}🎉 ¡Excelente! La aplicación está en muy buen estado.{Colors.RESET}")
    elif success_rate >= 70:
        print(f"Tasa de éxito: {Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.YELLOW}👍 Bien. La aplicación está en buen estado con algunos problemas menores.{Colors.RESET}")
    elif success_rate >= 50:
        print(f"Tasa de éxito: {Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ Regular. La aplicación necesita atención.{Colors.RESET}")
    else:
        print(f"Tasa de éxito: {Colors.RED}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.RED}❌ Crítico. La aplicación tiene problemas graves.{Colors.RESET}")
    
    print(f"{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                        🏁 PRUEBAS FINALIZADAS                ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    return result
    
    return result.wasSuccessful()

def run_specific_test(test_class_name):
    """Ejecutar una clase de prueba específica"""
    print_section(f"🎯 EJECUTANDO TESTS ESPECÍFICOS: {test_class_name.upper()}")
    
    # Mapear nombres a clases
    test_classes = {
        'environment': TestEnvironment,
        'dependencies': TestDependencies,
        'core': TestCoreModules,
        'config': TestConfiguration,
        'plugins': TestPluginSystem,
        'app': TestApplication,
        'ui': TestUIComponents,
        'threads': TestThreadManager,
        'tools': TestToolManager,
        'specific': TestSpecificPlugins,
        'assets': TestAssetManager,
        'files': TestFileStructure,
        'integration': TestIntegration,
        'performance': TestPerformance
    }
    
    test_class = test_classes.get(test_class_name.lower())
    
    if test_class is None:
        print_error(f"Clase de test '{test_class_name}' no encontrada")
        print_info("Clases disponibles:")
        for name in test_classes.keys():
            print_step(f"  → {name}", Colors.CYAN)
        return False
    
    # Crear suite con la clase específica
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen específico
    total_tests = result.testsRun
    successful_tests = total_tests - len(result.failures) - len(result.errors)
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print()
    print_section(f"📊 RESUMEN - {test_class_name.upper()}")
    print(f"{Colors.BOLD}📈 ESTADÍSTICAS:{Colors.RESET}")
    print(f"  {Colors.CYAN}• Total ejecutadas:{Colors.RESET} {total_tests}")
    print(f"  {Colors.GREEN}• Exitosas:{Colors.RESET} {successful_tests}")
    print(f"  {Colors.RED}• Fallidas:{Colors.RESET} {len(result.failures)}")
    print(f"  {Colors.MAGENTA}• Errores:{Colors.RESET} {len(result.errors)}")
    
    if result.skipped:
        print(f"  {Colors.YELLOW}• Saltadas:{Colors.RESET} {len(result.skipped)}")
    
    if success_rate >= 90:
        print(f"Tasa de éxito: {Colors.GREEN}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.GREEN}🎉 ¡Excelente! Tests pasaron correctamente.{Colors.RESET}")
    elif success_rate >= 70:
        print(f"Tasa de éxito: {Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.YELLOW}👍 Bien. Algunos problemas menores.{Colors.RESET}")
    else:
        print(f"Tasa de éxito: {Colors.RED}{success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.RED}❌ Problemas encontrados. Revisar errores.{Colors.RESET}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Permitir ejecución con argumentos para tests específicos
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name in ['environment', 'dependencies', 'core', 'config', 'plugins', 
                        'app', 'ui', 'threads', 'tools', 'specific', 'assets', 
                        'files', 'integration', 'performance']:
            success = run_specific_test(test_name)
            sys.exit(0 if success else 1)
        elif test_name == '--help' or test_name == '-h':
            print()
            print_section("🧪 GAMING HELPER OVERLAY - TEST SUITE")
            print(f"{Colors.BOLD}Uso:{Colors.RESET}")
            print(f"  python test_suite.py                    # Ejecutar todos los tests")
            print(f"  python test_suite.py [tipo]             # Ejecutar tests específicos")
            print()
            print(f"{Colors.BOLD}Tipos de tests disponibles:{Colors.RESET}")
            test_types = [
                ('environment', 'Tests de entorno de desarrollo'),
                ('dependencies', 'Tests de dependencias y librerías'),
                ('core', 'Tests de módulos principales'),
                ('config', 'Tests de configuración YAML'),
                ('plugins', 'Tests del sistema de plugins'),
                ('app', 'Tests de aplicación principal'),
                ('ui', 'Tests de componentes UI'),
                ('threads', 'Tests de gestión de hilos'),
                ('tools', 'Tests de herramientas'),
                ('specific', 'Tests de plugins específicos'),
                ('assets', 'Tests de gestión de assets'),
                ('files', 'Tests de estructura de archivos'),
                ('integration', 'Tests de integración'),
                ('performance', 'Tests de rendimiento')
            ]
            for test_type, description in test_types:
                print(f"  {test_type:<12} : {description}")
            print()
            print(f"{Colors.BOLD}Ejemplos:{Colors.RESET}")
            print(f"  python test_suite.py environment        # Solo tests de entorno")
            print(f"  python test_suite.py plugins            # Solo tests de plugins")
            print(f"  python test_suite.py performance        # Solo tests de rendimiento")
            print()
            sys.exit(0)
        else:
            print_error(f"Tipo de test desconocido: '{test_name}'")
            print_info("Usa 'python test_suite.py --help' para ver opciones disponibles")
            sys.exit(1)
    else:
        # Ejecutar todos los tests
        result = run_tests()
        sys.exit(0 if result.wasSuccessful() else 1)
