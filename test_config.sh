# 🧪 Gaming Helper Overlay - Configuración de Testing

# Variables de entorno para testing
export TEST_MODE=true
export LOGGING_LEVEL=INFO
export QT_QPA_PLATFORM=offscreen  # Para tests sin GUI en CI/CD

# Configuración de coverage (opcional - requiere: pip install coverage)
export COVERAGE_ENABLED=false

# Timeouts para tests
export TEST_TIMEOUT=30
export PLUGIN_LOAD_TIMEOUT=10

# Configuración de debugging
export DEBUG_TESTS=false
export VERBOSE_OUTPUT=true

# Configuración específica para Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    export PYTHONPATH="${PYTHONPATH};$(pwd)"
else
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
fi

echo "🧪 Configuración de testing cargada"
echo "   TEST_MODE: $TEST_MODE"
echo "   LOGGING_LEVEL: $LOGGING_LEVEL"
echo "   PYTHONPATH configurado"
