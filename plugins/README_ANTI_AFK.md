# 🤖 Anti-AFK Emulation Plugin

Plugin para Gaming Helper Overlay que previene expulsiones automáticas por inactividad (AFK) simulando inputs de mouse y teclado de forma inteligente.

## 🎯 Características Principales

### ⚡ Funcionalidades Core
- **Simulación de Mouse**: Movimientos aleatorios mínimos (configurable)
- **Simulación de Teclado**: Presión automática de teclas (WASD, Space, etc.)
- **Detección Inteligente de Juegos**: Solo se activa cuando detecta juegos
- **Detección de Actividad**: Se pausa cuando detecta actividad del usuario
- **Intervalos Aleatorios**: Evita detección por patrones predecibles

### 🛡️ Características de Seguridad
- **Modo Seguro**: Movimientos mínimos del mouse (±5 píxeles)
- **Retorno del Mouse**: Vuelve a la posición original
- **Parada de Emergencia**: Se detiene si detecta input del usuario
- **Límites de Frecuencia**: Máximo de acciones por minuto
- **Whitelist/Blacklist**: Control específico por juegos

### 🎮 Detección de Juegos
- **Detección Automática**: Identifica procesos y ventanas de juegos
- **Whitelist**: Lista de juegos específicos donde funcionar
- **Blacklist**: Lista de juegos donde NO funcionar
- **Patrones Inteligentes**: Detecta juegos por proceso y título

## ⚙️ Configuración

### 🕐 Configuración de Tiempo
```yaml
timing:
  interval_min: 30      # Mínimo segundos entre acciones
  interval_max: 60      # Máximo segundos entre acciones
  activity_threshold: 30 # Segundos de inactividad antes de iniciar
```

### 🖱️ Configuración de Mouse
```yaml
mouse:
  movement_range: 10    # Píxeles máximos de movimiento
  return_enabled: true  # Regresar a posición original
  clicks_enabled: false # Habilitar clicks del mouse
```

### ⌨️ Configuración de Teclado
```yaml
keyboard:
  keys: ["space", "w", "a", "s", "d"]  # Teclas a presionar
  hold_time: 50         # Milisegundos mantener presionada
```

## 🚀 Uso

### 1. Activación Básica
1. Abrir Gaming Helper Overlay
2. Hacer clic en el ícono flotante
3. Ir a la pestaña "Plugins"
4. Encontrar "Anti-AFK Emulation"
5. Hacer clic para activar
6. Hacer clic en "Start Anti-AFK"

### 2. Configuración Rápida
- **Intervalo**: Ajustar tiempo entre acciones (30-60s recomendado)
- **Acción**: Elegir Mouse, Teclado o Aleatorio
- **Solo en Juegos**: Marcar para activar solo cuando hay juegos
- **Modo Seguro**: Mantener marcado para movimientos mínimos

### 3. Configuración Avanzada
- Hacer clic en "Advanced Settings"
- Configurar teclas específicas
- Configurar whitelist/blacklist de juegos
- Ajustar configuraciones de seguridad

## 🎮 Casos de Uso

### MMORPGs
```yaml
# Configuración para MMOs (conservative)
interval_min: 45
interval_max: 90
action_type: "mouse_only"
safe_mode: true
```

### FPS Games
```yaml
# Configuración para FPS (standard)
interval_min: 30
interval_max: 60
keyboard_keys: ["w", "a", "s", "d"]
action_type: "keyboard_only"
```

### Idle Games
```yaml
# Configuración para juegos idle (aggressive)
interval_min: 15
interval_max: 30
action_type: "random"
safe_mode: false
```

## ⚠️ Consideraciones de Seguridad

### ✅ Buenas Prácticas
- Usar **Modo Seguro** siempre que sea posible
- Configurar **intervalos largos** (30-60 segundos)
- Activar **detección de actividad** del usuario
- Usar **whitelist** para juegos específicos
- Probar configuración antes de uso prolongado

### ❌ Evitar
- Intervalos muy cortos (< 15 segundos)
- Movimientos grandes del mouse (> 20 píxeles)
- Uso en juegos competitivos rankeds
- Desactivar todas las características de seguridad
- Uso 24/7 sin supervisión

### 🔒 Aspectos Legales/ToS
- **Responsabilidad del Usuario**: Verificar ToS del juego
- **Solo para Prevención de AFK**: No para automatización de gameplay
- **Uso Ético**: No para obtener ventajas competitivas
- **Supervisión**: Uso bajo supervisión del usuario

## 🛠️ Solución de Problemas

### ❓ Problemas Comunes

**El plugin no se activa**
- Verificar que esté habilitado en configuración
- Verificar que se detecte un juego (si está configurado)
- Revisar logs para errores

**No detecta el juego**
- Asegurarse de que el juego esté en ventana activa
- Verificar whitelist/blacklist
- Desactivar "Only in games" temporalmente

**Inputs no funcionan**
- Verificar permisos de administrador
- Asegurarse de que el juego no bloquee inputs externos
- Probar diferentes tipos de acción (mouse/keyboard)

**Muy frecuente/infrecuente**
- Ajustar intervalos min/max
- Verificar configuración de randomización
- Revisar límites de seguridad

## 📊 Monitoreo

### 📈 Indicadores de Estado
- **🟢 ACTIVE**: Plugin funcionando
- **🔴 INACTIVE**: Plugin detenido
- **🎮 Game Detected**: Juego detectado
- **⏱️ Next Action**: Próxima acción en X segundos

### 📝 Logs
```
[Anti-AFK] Started - Interval: 30-60s
[Anti-AFK] Game detected: Minecraft
[Anti-AFK] Mouse moved by (3, -2)
[Anti-AFK] User activity detected - pausing
[Anti-AFK] Key pressed: space
```

## 🔧 Desarrollo

### 📁 Archivos del Plugin
```
plugins/
├── anti_afk.py              # Plugin principal
├── anti_afk_advanced.py     # Configuración avanzada
└── config/plugins/
    └── anti_afk.yaml         # Configuración YAML
```

### 🔌 API del Plugin
```python
# Iniciar Anti-AFK
plugin._start_anti_afk()

# Detener Anti-AFK
plugin._stop_anti_afk()

# Detectar juego activo
is_game = plugin._is_game_active()

# Simular movimiento de mouse
plugin._simulate_mouse_movement()

# Simular presión de tecla
plugin._simulate_key_press()
```

## 📋 Checklist de Configuración

- [ ] Plugin activado en Gaming Helper
- [ ] Intervalos configurados (30-60s recomendado)
- [ ] Modo seguro activado
- [ ] Detección de juegos configurada
- [ ] Whitelist/Blacklist según necesidad
- [ ] Probado en entorno controlado
- [ ] Logs verificados
- [ ] ToS del juego revisado

## 🔄 Versiones

### v1.0.0 (Actual)
- ✅ Simulación básica de mouse y teclado
- ✅ Detección inteligente de juegos
- ✅ Configuración avanzada
- ✅ Características de seguridad
- ✅ Whitelist/Blacklist de juegos
- ✅ UI completa con estado en tiempo real

### 🔮 Futuras Mejoras
- [ ] Patrones de movimiento más sofisticados
- [ ] Integración con APIs de juegos
- [ ] Perfiles automáticos por juego
- [ ] Machine learning para patrones naturales
- [ ] Sincronización cloud de configuraciones

---

**⚠️ Disclaimer**: Este plugin está diseñado para prevenir desconexiones automáticas por inactividad. El usuario es responsable de verificar la compatibilidad con los términos de servicio de cada juego. Usar éticamente y bajo supervisión.

**🤝 Soporte**: Para problemas o sugerencias, crear issue en el repositorio del Gaming Helper Overlay.
