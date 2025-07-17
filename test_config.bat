@echo off
REM 🧪 Gaming Helper Overlay - Test Configuration for Windows
REM Configuración de entorno para testing en Windows

echo 🧪 Configurando entorno de testing para Windows...

REM Variables de entorno para testing
set TEST_MODE=true
set LOGGING_LEVEL=INFO
set QT_QPA_PLATFORM=offscreen

REM Configuración de debugging
set DEBUG_TESTS=false
set VERBOSE_OUTPUT=true

REM Timeouts para tests
set TEST_TIMEOUT=30
set PLUGIN_LOAD_TIMEOUT=10

REM Configurar PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

echo    TEST_MODE: %TEST_MODE%
echo    LOGGING_LEVEL: %LOGGING_LEVEL%
echo    PYTHONPATH configurado
echo.

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no encontrado en PATH
    echo 💡 Asegúrate de que Python esté instalado y en PATH
    pause
    exit /b 1
)

REM Verificar que el directorio sea correcto
if not exist "test_suite.py" (
    echo ❌ Error: test_suite.py no encontrado
    echo 💡 Asegúrate de estar en el directorio del proyecto
    pause
    exit /b 1
)

echo ✅ Configuración completada. Listo para ejecutar tests.
echo.
echo 📖 Comandos disponibles:
echo    python test_suite.py              # Todos los tests
echo    python test_suite.py environment  # Tests específicos
echo    python run_tests.py --help        # Ver opciones del runner
echo    python run_tests.py quick         # Diagnosis rápida
echo.
