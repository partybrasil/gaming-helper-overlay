# Gaming Helper Overlay - PowerShell Launcher
# Script de inicio para Windows PowerShell

Write-Host "Gaming Helper Overlay - Launcher" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor instala Python 3.10+ desde https://python.org" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si las dependencias están instaladas
Write-Host "Verificando dependencias..." -ForegroundColor Yellow

try {
    python -c "import PySide6" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencias OK" -ForegroundColor Green
    }
    else {
        throw "Dependencies not found"
    }
}
catch {
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

# Crear directorios necesarios si no existen
$directories = @("data", "data\logs", "data\cache", "data\user_data", "data\plugins", "data\temp")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Creado directorio: $dir" -ForegroundColor Gray
    }
}

# Limpiar archivos temporales anteriores
if (Test-Path "data\temp\*") {
    Remove-Item "data\temp\*" -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Iniciando Gaming Helper Overlay..." -ForegroundColor Green
Write-Host "Para cerrar la aplicación, cierra esta ventana o usa Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Ejecutar la aplicación
try {
    python main.py
}
catch {
    Write-Host ""
    Write-Host "La aplicación se cerró con un error." -ForegroundColor Red
    Write-Host "Revisa los logs en data\logs\ para más información." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "La aplicación se ha cerrado." -ForegroundColor Cyan
Read-Host "Presiona Enter para salir"
