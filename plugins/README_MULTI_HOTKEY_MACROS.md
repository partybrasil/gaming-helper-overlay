# 🎮 Multi-Hotkey / Macros Plugin

Plugin avanzado para Gaming Helper Overlay que permite crear combos de teclas personalizados, macros complejos, loops, delays y automatización completa de mouse y teclado.

## 🎯 Características Principales

### ⚡ Funcionalidades Core
- **Hotkeys Globales**: Combinaciones de teclas que funcionan en todo el sistema
- **Grabación de Macros**: Graba automáticamente las acciones de mouse y teclado
- **Editor de Macros**: Crea y edita macros manualmente con precisión
- **Loops y Repeticiones**: Ejecuta acciones múltiples veces con delays personalizados
- **Variables y Condiciones**: Sistema avanzado de variables para macros dinámicos
- **Categorización**: Organiza macros por categorías (Gaming, Productividad, etc.)

### 🖱️ Acciones de Mouse
- **Clicks**: Click izquierdo, derecho, central con coordenadas específicas
- **Movimientos**: Movimiento absoluto, relativo y suavizado
- **Scroll**: Scroll vertical y horizontal
- **Arrastrar y soltar**: Secuencias complejas de arrastre
- **Multi-click**: Doble click, triple click, clicks múltiples

### ⌨️ Acciones de Teclado
- **Teclas individuales**: Presión, mantenimiento y liberación
- **Combinaciones**: Ctrl+C, Alt+Tab, secuencias complejas
- **Texto**: Escritura automática de texto y frases
- **Teclas especiales**: F1-F12, flechas, Insert, Delete, etc.
- **Modificadores**: Shift, Ctrl, Alt, Win con detección inteligente

### 🔄 Funciones Avanzadas
- **Loops Anidados**: Bucles dentro de bucles con contadores
- **Delays Variables**: Tiempos de espera fijos y aleatorios
- **Condiciones**: Ejecución condicional basada en variables
- **Parada de Emergencia**: Hotkey global para detener todo
- **Ejecución Concurrente**: Múltiples macros ejecutándose simultáneamente

## ⚙️ Configuración

### 🕐 Configuración Global
```yaml
# Configuración general
enabled: true
global_hotkey_enabled: true
auto_save: true
notification_enabled: true

# Configuración de ejecución
execution_delay: 0.01          # delay entre acciones
max_concurrent_macros: 5       # máximo macros concurrentes
emergency_stop_key: 'ctrl+alt+esc'  # parada de emergencia

# Configuración de seguridad
safe_mode: true               # prevenir acciones peligrosas
max_action_duration: 300      # máximo 5 minutos por macro
require_confirmation: false   # confirmar antes de ejecutar
```

### 🎛️ Configuración de Grabación
```yaml
# Grabación de acciones
recording_mouse: true
recording_keyboard: true
recording_precision: 'medium'  # low, medium, high
recording_sensitivity: 0.1     # segundos entre acciones
```

## 🚀 Uso Básico

### 1. Crear un Macro Simple
1. Activar el plugin en el Control Panel
2. Hacer clic en "New Macro"
3. Darle un nombre (ej: "Quick Screenshot")
4. Asignar hotkey (ej: "ctrl+shift+s")
5. Agregar acciones:
   - Key Press: "win+shift+s"
   - Delay: 0.5 segundos

### 2. Grabar un Macro
1. Hacer clic en "Start Recording"
2. Realizar las acciones deseadas
3. Hacer clic en "Stop Recording"
4. Darle nombre y hotkey al macro grabado
5. Guardar y activar

### 3. Macro con Loop
```
1. Mouse Click en (100, 200)
2. Key Press: "space"
3. Delay: 1.0 segundos
4. Loop Start (10 iterations)
   - Key Press: "w"
   - Delay: 0.5 segundos
5. Loop End
6. Key Press: "esc"
```

## 🎮 Casos de Uso Gaming

### 🏹 MMORPGs
```yaml
# Combo de habilidades
Hotkey: "1"
Actions:
  - Key Press: "q"      # Habilidad 1
  - Delay: 0.2
  - Key Press: "w"      # Habilidad 2
  - Delay: 0.3
  - Key Press: "e"      # Habilidad 3
  - Delay: 0.1
  - Key Press: "r"      # Habilidad Ultimate
```

### 🔫 FPS Games
```yaml
# Compra rápida Counter-Strike
Hotkey: "f1"
Actions:
  - Key Press: "b"      # Abrir menú compra
  - Delay: 0.1
  - Key Press: "4"      # Rifles
  - Key Press: "2"      # AK-47/M4
  - Key Press: "esc"    # Cerrar menú
```

### 🏗️ Building Games
```yaml
# Construcción rápida
Hotkey: "shift+1"
Actions:
  - Loop Start (5)
    - Key Press: "1"    # Seleccionar material
    - Mouse Click: relative(0, 50)  # Colocar
    - Delay: 0.1
  - Loop End
```

## 💼 Casos de Uso Productividad

### 📝 Editor de Texto
```yaml
# Formato código
Hotkey: "ctrl+alt+f"
Actions:
  - Key Combo: "ctrl+a"    # Seleccionar todo
  - Key Combo: "ctrl+shift+i"  # Auto-indent
  - Key Combo: "ctrl+s"    # Guardar
  - Delay: 0.5
  - Key Press: "esc"       # Deseleccionar
```

### 🌐 Navegador Web
```yaml
# Abrir pestañas frecuentes
Hotkey: "ctrl+shift+o"
Actions:
  - Loop Start (3)
    - Key Combo: "ctrl+t"     # Nueva pestaña
    - Variable Set: url_{{loop_counter}}
    - Type Text: "{{url}}"
    - Key Press: "enter"
    - Delay: 1.0
  - Loop End
```

## 🔧 Tipos de Acciones Disponibles

### ⌨️ Teclado
- **Key Press**: Presión rápida de tecla
- **Key Hold**: Mantener tecla presionada por tiempo específico
- **Key Release**: Liberar tecla mantenida
- **Type Text**: Escribir texto completo
- **Key Combo**: Combinación de teclas (Ctrl+C, Alt+Tab)

### 🖱️ Mouse
- **Mouse Click**: Click en posición específica
- **Mouse Move**: Movimiento a coordenadas
- **Mouse Scroll**: Scroll vertical/horizontal
- **Mouse Drag**: Arrastrar desde/hasta coordenadas
- **Mouse Hold**: Mantener botón presionado

### ⏱️ Control de Flujo
- **Delay**: Pausa por tiempo específico
- **Loop Start/End**: Bucles con contadores
- **Condition**: Ejecución condicional
- **Variable Set**: Asignar valores a variables
- **Hotkey Trigger**: Activar otro macro

## 🔥 Funciones Avanzadas

### 📊 Variables del Sistema
```yaml
# Variables disponibles
{{mouse_x}}, {{mouse_y}}      # Posición actual del mouse
{{time}}, {{date}}            # Fecha y hora
{{screen_width}}, {{screen_height}}  # Resolución de pantalla
{{loop_counter}}              # Contador de loop actual
{{random_1_10}}               # Número aleatorio 1-10
```

### 🎯 Macros Condicionales
```yaml
# Macro que se adapta según la ventana activa
Actions:
  - Condition: "{{active_window}} == 'notepad.exe'"
    Then:
      - Key Combo: "ctrl+n"   # Nuevo archivo en Notepad
    Else:
      - Key Combo: "ctrl+t"   # Nueva pestaña en navegador
```

### 🌊 Movimientos Suavizados
```yaml
# Movimiento suave del mouse
Actions:
  - Mouse Move: 
      x: 500
      y: 300
      duration: 2.0      # 2 segundos de movimiento suave
      easing: "ease_in_out"
```

## 📊 Monitoreo y Estadísticas

### 📈 Métricas de Ejecución
- **Total ejecutados**: Contador de todas las ejecuciones
- **Exitosos/Fallidos**: Tasa de éxito de los macros
- **Tiempo promedio**: Duración promedio de ejecución
- **Macros más usados**: Ranking por frecuencia de uso
- **Errores comunes**: Log detallado de fallos

### 🔍 Debug y Troubleshooting
- **Modo Debug**: Ejecución paso a paso con logs
- **Previsualización**: Ver acciones sin ejecutar
- **Validación**: Verificar macros antes de ejecutar
- **Backup automático**: Respaldo de macros importantes

## ⚠️ Consideraciones de Seguridad

### 🛡️ Modo Seguro
- **Prevención de loops infinitos**: Límite máximo de iteraciones
- **Detección de acciones peligrosas**: Advertencias para comandos del sistema
- **Parada de emergencia**: Ctrl+Alt+Esc para detener todo
- **Confirmación para macros destructivos**: Diálogo antes de ejecutar

### 🚫 Limitaciones y Restricciones
- **Hotkeys reservados**: No permite usar Ctrl+Alt+Del, Win+L, etc.
- **Aplicaciones protegidas**: Algunos programas pueden bloquear la automatización
- **Tiempo máximo de ejecución**: 5 minutos por macro por defecto
- **Detección de antivirus**: Algunos antivirus pueden detectar como sospechoso

## 🔧 Solución de Problemas

### ❌ Problemas Comunes

#### Hotkeys no funcionan
- Verificar que no hay conflictos con otros programas
- Ejecutar como administrador si es necesario
- Revisar que las librerías keyboard/mouse estén instaladas

#### Macros se ejecutan lentamente
- Reducir el delay entre acciones
- Verificar que no hay otros programas consumiendo CPU
- Usar acciones más específicas en lugar de bucles largos

#### Mouse/Teclado no responde
- Verificar que las dependencias estén instaladas: `pip install keyboard mouse`
- Reiniciar el plugin
- Verificar permisos de accesibilidad en Windows

### 📋 Instalación de Dependencias
```bash
# Instalar librerías necesarias
pip install keyboard>=1.13.0
pip install mouse>=0.7.1

# Si hay problemas de permisos en Windows
pip install --user keyboard mouse

# Para desarrollo
pip install keyboard[dev] mouse[dev]
```

## 🎨 Personalización de UI

### 🖼️ Temas y Apariencia
- **Panel transparente**: Ajustar transparencia del panel principal
- **Always on top**: Mantener panel siempre visible
- **Colores por categoría**: Diferentes colores para tipos de macro
- **Iconos personalizados**: Asignar iconos a macros frecuentes

### ⚡ Atajos de Teclado del Plugin
- **F1**: Ayuda y documentación
- **F2**: Editar macro seleccionado
- **F5**: Refrescar lista de macros
- **Ctrl+N**: Nuevo macro
- **Ctrl+D**: Duplicar macro
- **Delete**: Eliminar macro seleccionado
- **Space**: Ejecutar macro seleccionado

## 📚 Ejemplos Avanzados

### 🔄 Macro de Farming Automático
```yaml
Name: "Auto Farm Loop"
Hotkey: "ctrl+shift+f"
Category: "Gaming"
Actions:
  - Loop Start (100)  # 100 iteraciones
    - Key Press: "1"        # Atacar
    - Delay: 2.0
    - Key Press: "2"        # Habilidad especial
    - Delay: 3.0
    - Mouse Move: relative(50, 0)  # Mover ligeramente
    - Condition: "{{loop_counter}} % 10 == 0"  # Cada 10 loops
      Then:
        - Key Press: "h"      # Usar poción
        - Delay: 1.0
    - Variable Set: "enemies_killed" = "{{loop_counter}}"
  - Loop End
  - Type Text: "Farming complete: {{enemies_killed}} enemies"
```

### 🎯 Macro de Construcción Precisa
```yaml
Name: "Perfect Building"
Hotkey: "ctrl+b"
Category: "Gaming"
Variables:
  - start_x: 100
  - start_y: 200
  - grid_size: 50
Actions:
  - Loop Start (5)  # 5x5 grid
    - Variable Set: "current_x" = "{{start_x}} + ({{loop_counter}} * {{grid_size}})"
    - Loop Start (5)
      - Variable Set: "current_y" = "{{start_y}} + ({{inner_loop_counter}} * {{grid_size}})"
      - Mouse Move: absolute({{current_x}}, {{current_y}})
      - Mouse Click: left
      - Delay: 0.2
    - Loop End
  - Loop End
  - Type Text: "Construction grid completed!"
```

## 📦 Exportar e Importar

### 💾 Formatos de Exportación
- **JSON**: Formato estándar para intercambio
- **YAML**: Formato legible para edición manual
- **Binary**: Formato comprimido para backups

### 🔄 Importar desde Otros Programas
- **AutoHotkey (.ahk)**: Convertidor básico de scripts AHK
- **Macro Recorder**: Importar desde grabadores comunes
- **Gaming Keyboards**: Importar macros de Razer, Logitech, etc.

---

## 🎉 ¡Macro Power Unlocked!

Con el plugin Multi-Hotkey Macros tienes control total sobre la automatización de tu PC. Desde combos simples de gaming hasta workflows complejos de productividad.

**¡Crea, personaliza y automatiza todo lo que necesites!** 🚀
