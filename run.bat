@echo off
echo Gaming Helper Overlay - Launcher
echo ================================

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.10+ desde https://python.org
    pause
    exit /b 1
)

:: Verificar la versión de Python
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

:: Verificar si las dependencias están instaladas
echo Verificando dependencias...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
) else (
    echo Dependencias OK
)

:: Crear directorios necesarios si no existen
if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs
if not exist "data\cache" mkdir data\cache
if not exist "data\user_data" mkdir data\user_data
if not exist "data\plugins" mkdir data\plugins
if not exist "data\temp" mkdir data\temp

:: Limpiar archivos temporales anteriores
if exist "data\temp\*" del /q "data\temp\*" >nul 2>&1

echo.
echo Iniciando Gaming Helper Overlay...
echo Para cerrar la aplicación, cierra esta ventana o usa Ctrl+C
echo.

:: Ejecutar la aplicación
python main.py

:: Si llegamos aquí, la aplicación se cerró
echo.
echo La aplicación se ha cerrado.
pause
