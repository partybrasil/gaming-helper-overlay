#!/usr/bin/env python3
"""
🧪 Gaming Helper Overlay - Test Runner
Ejecutor de tests con opciones avanzadas y diagnóstico
"""

import sys
import argparse
import subprocess
from pathlib import Path

def print_header():
    """Mostrar header del test runner"""
    print(f"\n{'='*60}")
    print("🧪 Gaming Helper Overlay - Test Runner")
    print(f"{'='*60}")

def print_available_tests():
    """Mostrar tests disponibles"""
    tests = {
        'all': 'Ejecutar todos los tests (49 tests)',
        'environment': 'Tests de entorno de desarrollo',
        'dependencies': 'Tests de dependencias y librerías',
        'core': 'Tests de módulos principales',
        'config': 'Tests de configuración YAML',
        'plugins': 'Tests del sistema de plugins',
        'app': 'Tests de aplicación principal',
        'ui': 'Tests de componentes UI',
        'threads': 'Tests de gestión de hilos',
        'tools': 'Tests de herramientas',
        'specific': 'Tests de plugins específicos',
        'assets': 'Tests de gestión de assets',
        'files': 'Tests de estructura de archivos',
        'integration': 'Tests de integración',
        'performance': 'Tests de rendimiento',
        'quick': 'Diagnosis rápida básica',
        'critical': 'Solo tests críticos (environment + dependencies + core)'
    }
    
    print("\n📋 Tests Disponibles:")
    print("-" * 40)
    for test, desc in tests.items():
        print(f"  {test:<12} : {desc}")

def run_quick_diagnosis():
    """Ejecutar diagnosis rápida"""
    print("\n🔍 Ejecutando diagnosis rápida...")
    
    # Verificar Python
    version = sys.version_info
    if version >= (3, 10):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requerido: 3.10+)")
        return False
    
    # Verificar dependencias críticas
    critical_deps = ['PySide6', 'yaml', 'psutil', 'requests']
    failed_deps = []
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            failed_deps.append(dep)
    
    # Verificar archivos principales
    critical_files = [
        'main.py', 'test_suite.py', 'requirements.txt',
        'config/config.yaml', 'core/app_core.py'
    ]
    
    missing_files = []
    for file in critical_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    # Resultado
    if not failed_deps and not missing_files:
        print("\n🎉 ¡Diagnosis exitosa! Sistema listo para usar.")
        print("💡 Puedes ejecutar: python test_suite.py")
        return True
    else:
        print(f"\n⚠️ Problemas encontrados:")
        if failed_deps:
            print(f"  📦 Dependencias faltantes: {', '.join(failed_deps)}")
            print(f"  💡 Solución: pip install -r requirements.txt")
        if missing_files:
            print(f"  📁 Archivos faltantes: {', '.join(missing_files)}")
            print(f"  💡 Solución: Verificar instalación del proyecto")
        return False

def run_test_suite(test_type='all', verbose=False, buffer=False):
    """Ejecutar tests específicos"""
    
    # Mapeo de tipos de test a clases
    test_mapping = {
        'environment': 'TestEnvironment',
        'dependencies': 'TestDependencies',
        'core': 'TestCoreModules',
        'config': 'TestConfiguration',
        'plugins': 'TestPluginSystem',
        'app': 'TestApplication',
        'ui': 'TestUIComponents',
        'threads': 'TestThreadManager',
        'tools': 'TestToolManager',
        'specific': 'TestSpecificPlugins',
        'assets': 'TestAssetManager',
        'files': 'TestFileStructure',
        'integration': 'TestIntegration',
        'performance': 'TestPerformance'
    }
    
    # Construir comando
    if test_type == 'all':
        cmd = ['python', 'test_suite.py']
    elif test_type == 'critical':
        # Tests críticos: environment, dependencies, core
        cmd = ['python', '-m', 'unittest', 
               'test_suite.TestEnvironment',
               'test_suite.TestDependencies', 
               'test_suite.TestCoreModules']
        if verbose:
            cmd.append('-v')
        if buffer:
            cmd.append('-b')
    elif test_type in test_mapping:
        cmd = ['python', '-m', 'unittest', f'test_suite.{test_mapping[test_type]}']
        if verbose:
            cmd.append('-v')
        if buffer:
            cmd.append('-b')
    else:
        print(f"❌ Tipo de test desconocido: {test_type}")
        return False
    
    # Ejecutar comando
    print(f"\n🚀 Ejecutando tests: {test_type}")
    print(f"💻 Comando: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='🧪 Gaming Helper Overlay Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py                    # Ejecutar todos los tests
  python run_tests.py environment        # Solo tests de entorno
  python run_tests.py --list             # Listar tests disponibles
  python run_tests.py quick              # Diagnosis rápida
  python run_tests.py critical -v        # Tests críticos con verbosidad
  python run_tests.py plugins --buffer   # Tests de plugins con buffer
        """
    )
    
    parser.add_argument('test_type', nargs='?', default='all',
                       help='Tipo de test a ejecutar (default: all)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Salida verbose para unittest')
    parser.add_argument('-b', '--buffer', action='store_true',
                       help='Buffer output durante ejecución')
    parser.add_argument('-l', '--list', action='store_true',
                       help='Listar tests disponibles')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Solo diagnosis rápida')
    
    args = parser.parse_args()
    
    print_header()
    
    # Mostrar tests disponibles
    if args.list:
        print_available_tests()
        return
    
    # Diagnosis rápida
    if args.quick or args.test_type == 'quick':
        success = run_quick_diagnosis()
        sys.exit(0 if success else 1)
    
    # Verificar que el archivo test_suite.py existe
    if not Path('test_suite.py').exists():
        print("❌ Error: test_suite.py no encontrado")
        print("💡 Asegúrate de estar en el directorio del proyecto")
        sys.exit(1)
    
    # Ejecutar tests
    success = run_test_suite(args.test_type, args.verbose, args.buffer)
    
    if success:
        print(f"\n🎉 Tests completados exitosamente!")
    else:
        print(f"\n❌ Algunos tests fallaron. Revisa la salida arriba.")
        print(f"💡 Para diagnosis: python run_tests.py quick")
        print(f"💡 Para tests críticos: python run_tests.py critical -v")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
