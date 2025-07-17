# 🧪 Gaming Helper Overlay - Test Configuration for PowerShell
# Configuración avanzada de entorno para testing en Windows PowerShell

Write-Host "🧪 Gaming Helper Overlay - Configuración de Testing" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Variables de entorno para testing
$env:TEST_MODE = "true"
$env:LOGGING_LEVEL = "INFO"
$env:QT_QPA_PLATFORM = "offscreen"
$env:DEBUG_TESTS = "false"
$env:VERBOSE_OUTPUT = "true"
$env:TEST_TIMEOUT = "30"
$env:PLUGIN_LOAD_TIMEOUT = "10"

# Configurar PYTHONPATH
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
} else {
    $env:PYTHONPATH = "$(Get-Location)"
}

Write-Host "⚙️ Variables de entorno configuradas:" -ForegroundColor Green
Write-Host "   TEST_MODE: $env:TEST_MODE" -ForegroundColor White
Write-Host "   LOGGING_LEVEL: $env:LOGGING_LEVEL" -ForegroundColor White
Write-Host "   PYTHONPATH: Configurado" -ForegroundColor White
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python no encontrado en PATH" -ForegroundColor Red
        Write-Host "💡 Instala Python 3.10+ y agrégalo al PATH" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error verificando Python: $_" -ForegroundColor Red
    exit 1
}

# Verificar estructura del proyecto
$requiredFiles = @("test_suite.py", "main.py", "requirements.txt", "config\config.yaml")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (faltante)" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️ Archivos faltantes detectados:" -ForegroundColor Yellow
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host "💡 Asegúrate de estar en el directorio correcto del proyecto" -ForegroundColor Yellow
    exit 1
}

# Verificar dependencias básicas
Write-Host ""
Write-Host "📦 Verificando dependencias críticas..." -ForegroundColor Cyan

$dependencies = @("PySide6", "yaml", "psutil", "requests")
$missingDeps = @()

foreach ($dep in $dependencies) {
    try {
        $result = python -c "import $dep; print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $dep" -ForegroundColor Green
        } else {
            Write-Host "❌ $dep (no disponible)" -ForegroundColor Red
            $missingDeps += $dep
        }
    } catch {
        Write-Host "❌ $dep (error: $_)" -ForegroundColor Red
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️ Dependencias faltantes:" -ForegroundColor Yellow
    foreach ($dep in $missingDeps) {
        Write-Host "   - $dep" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "💡 Instala las dependencias con:" -ForegroundColor Yellow
    Write-Host "   pip install -r requirements.txt" -ForegroundColor White
    
    $response = Read-Host "¿Quieres instalar las dependencias ahora? (s/n)"
    if ($response -eq "s" -or $response -eq "S" -or $response -eq "y" -or $response -eq "Y") {
        Write-Host ""
        Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
        } else {
            Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "🎉 ¡Configuración completada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Comandos disponibles:" -ForegroundColor Cyan
Write-Host "   python test_suite.py                    # Ejecutar todos los tests" -ForegroundColor White
Write-Host "   python test_suite.py environment        # Tests específicos" -ForegroundColor White
Write-Host "   python test_suite.py --help             # Ver ayuda completa" -ForegroundColor White
Write-Host "   python run_tests.py --list              # Listar tests disponibles" -ForegroundColor White
Write-Host "   python run_tests.py quick               # Diagnosis rápida" -ForegroundColor White
Write-Host "   python run_tests.py critical -v         # Tests críticos con verbose" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para empezar, ejecuta:" -ForegroundColor Yellow
Write-Host "   python run_tests.py quick" -ForegroundColor White
Write-Host ""

# Función para ejecutar tests con menú interactivo
function Show-TestMenu {
    Write-Host "🧪 MENÚ INTERACTIVO DE TESTING" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "1. Ejecutar todos los tests" -ForegroundColor White
    Write-Host "2. Diagnosis rápida" -ForegroundColor White
    Write-Host "3. Tests críticos" -ForegroundColor White
    Write-Host "4. Tests de entorno" -ForegroundColor White
    Write-Host "5. Tests de plugins" -ForegroundColor White
    Write-Host "6. Ver lista completa de tests" -ForegroundColor White
    Write-Host "7. Salir" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Selecciona una opción (1-7)"
    
    switch ($choice) {
        "1" { 
            Write-Host "🚀 Ejecutando todos los tests..." -ForegroundColor Green
            python test_suite.py 
        }
        "2" { 
            Write-Host "🔍 Ejecutando diagnosis rápida..." -ForegroundColor Green
            python run_tests.py quick 
        }
        "3" { 
            Write-Host "⚡ Ejecutando tests críticos..." -ForegroundColor Green
            python run_tests.py critical -v 
        }
        "4" { 
            Write-Host "🌟 Ejecutando tests de entorno..." -ForegroundColor Green
            python test_suite.py environment 
        }
        "5" { 
            Write-Host "🔌 Ejecutando tests de plugins..." -ForegroundColor Green
            python test_suite.py plugins 
        }
        "6" { 
            Write-Host "📋 Lista de tests disponibles:" -ForegroundColor Green
            python run_tests.py --list 
        }
        "7" { 
            Write-Host "👋 ¡Hasta luego!" -ForegroundColor Green
            return 
        }
        default { 
            Write-Host "❌ Opción inválida. Selecciona 1-7." -ForegroundColor Red
            Show-TestMenu
        }
    }
}

# Preguntar si quiere usar el menú interactivo
$useMenu = Read-Host "¿Quieres usar el menú interactivo de testing? (s/n)"
if ($useMenu -eq "s" -or $useMenu -eq "S" -or $useMenu -eq "y" -or $useMenu -eq "Y") {
    Show-TestMenu
}
