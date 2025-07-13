# 🎮 Gaming Helper Overlay

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)](https://doc.qt.io/qtforpython/)
[![Windows](https://img.shields.io/badge/platform-Windows%2011-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active%20Development-brightgreen.svg)]()

> **Una aplicación de overlay modular para gaming con paneles flotantes y sistema de plugins extensible, construida con PySide6 para Windows 11.**

<div align="center">

### 🚀 **PROYECTO COMPLETAMENTE FUNCIONAL** ✅

*Sistema principal implementado • Interfaz moderna • Plugins integrados • Documentación completa*

[📥 Instalación](#-instalación) • [🎯 Características](#-estado-de-implementación) • [🚀 Inicio Rápido](#-inicio-rápido) • [📚 Documentación](#-documentación)

</div>

---

## 📋 Estado de Implementación

### ✅ **COMPLETADO** - Sistema Principal
- [x] **Aplicación Principal** (`main.py`) - Punto de entrada con configuración Qt6
- [x] **Arquitectura Modular** - Sistema de núcleo completamente funcional
- [x] **Gestión de Configuración** (`config_manager.py`) - YAML con persistencia
- [x] **Sistema de Plugins** (`plugin_manager.py`) - Descubrimiento y carga dinámica
- [x] **Threading Avanzado** (`thread_manager.py`) - Ejecución segura en background
- [x] **Logging Completo** - Rotación automática y niveles configurables

### ✅ **COMPLETADO** - Interfaz de Usuario  
- [x] **Paneles Flotantes** (`floating_panel.py`) - Base con transparencia y drag&drop
- [x] **Panel de Control** (`control_panel.py`) - Interfaz tabbed para gestión
- [x] **Icono Flotante** (`icon_widget.py`) - Acceso rápido siempre visible
- [x] **Ventana Principal** (`main_window.py`) - Interfaz tradicional opcional
- [x] **Gestor de Assets** (`assets_manager.py`) - Manejo de recursos
- [x] **Efectos Glassmorphism** - Diseño moderno con blur y transparencia
- [x] **Always-on-Top** - Configuración por panel individual
- [x] **Drag & Drop** - Reposicionamiento libre de paneles

### ✅ **COMPLETADO** - Plugins Integrados
- [x] **🤖 Anti-AFK Emulation** (`anti_afk.py`) - Prevención automática de desconexiones por inactividad
- [x] **🎯 Crosshair Overlay** (`crosshair.py`) - Mira personalizable con múltiples estilos
- [x] **📊 FPS Counter** (`fps_counter.py`) - Contador en tiempo real con estadísticas
- [x] **💻 CPU/GPU Monitor** (`cpu_gpu_monitor.py`) - Monitor de recursos del sistema
- [x] **Configuración por Plugin** - Archivos YAML individuales
- [x] **Activación Dinámica** - Carga/descarga en tiempo real

### ✅ **COMPLETADO** - Configuración y Datos
- [x] **Configuración Principal** (`config/config.yaml`) - Configuraciones globales
- [x] **Configuraciones por Plugin** (`config/plugins/`) - Settings específicos
- [x] **Persistencia de Datos** (`data/`) - Logs, cache y datos de usuario
- [x] **Backup Automático** - Sistema de respaldo de configuraciones
- [x] **Reset a Defaults** - Restauración de configuración original

### ✅ **COMPLETADO** - Documentación
- [x] **README Principal** - Guía completa de uso (este archivo)
- [x] **Guía de Instalación** (`INSTALLATION.md`) - Instrucciones detalladas
- [x] **Desarrollo de Plugins** (`docs/PLUGIN_DEVELOPMENT.md`) - API completa
- [x] **Arquitectura del Sistema** (`docs/ARCHITECTURE.md`) - Diseño técnico
- [x] **Changelog** (`CHANGELOG.md`) - Historial de versiones
- [x] **Licencia** (`LICENSE`) - MIT License

### ✅ **COMPLETADO** - Scripts y Herramientas
- [x] **Scripts de Inicio** (`run.bat`, `run.ps1`) - Múltiples formas de ejecutar
- [x] **Suite de Pruebas** (`test_suite.py`) - Verificación automática
- [x] **Gestión de Dependencias** (`requirements.txt`) - Instalación automatizada
- [x] **Información de Versión** (`version.py`) - Metadata del proyecto

---

## 🔧 **EN DESARROLLO** - Características Avanzadas

### ✅ **NUEVO - COMPLETADO**
- [x] **🤖 Anti-AFK Emulation** - Prevención automática de desconexiones por inactividad
  - ✅ Simulación inteligente de mouse y teclado
  - ✅ Detección automática de juegos
  - ✅ Configuración avanzada con whitelist/blacklist
  - ✅ Características de seguridad y modo conservador
  - ✅ UI completa con estado en tiempo real

### 🟡 **PARCIALMENTE IMPLEMENTADO**
- [x] **Base de Plugins** - Sistema extensible funcionando
- [ ] **🖱️ Mouse Enhancer** - Mejoras del cursor (estructura creada)
- [ ] **🖼️ Borderless Window Tool** - Gestión de ventanas (planificado)
- [ ] **⌨️ Key Overlay** - Mostrar teclas presionadas (en progreso)
- [ ] **🔊 Audio Overlay** - Visualización de audio (diseño inicial)

### 🔴 **PENDIENTE** - Integraciones Externas
- [ ] **🎮 Steam API Integration** - Integración con Steam
- [ ] **💬 Discord Rich Presence** - Estado en Discord
- [ ] **📺 Twitch API Integration** - Herramientas de streaming
- [ ] **🎵 Spotify Integration** - Control de música
- [ ] **🌐 Web Dashboard** - Panel web remoto

### 🔴 **PENDIENTE** - Funciones Premium
- [ ] **☁️ Cloud Sync** - Sincronización de configuraciones
- [ ] **📱 Mobile Companion** - App móvil complementaria
- [ ] **🤖 AI Game Detection** - Detección inteligente de juegos
- [ ] **🎙️ Voice Commands** - Control por voz
- [ ] **🥽 VR Support** - Soporte para realidad virtual

---

## 🚀 Inicio Rápido

### 📥 Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/partybrasil/gaming-helper-overlay.git
cd gaming-helper-overlay

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python main.py
```

### 🎯 Uso Inmediato

1. **🚀 Iniciar**: Ejecuta `python main.py` o usa `run.bat`
2. **👁️ Localizar**: Busca el icono flotante en tu pantalla
3. **🖱️ Abrir Panel**: Click en el icono → Panel de Control
4. **⚡ Activar Plugins**: Pestaña "Plugins" → Activar los deseados
5. **🎨 Personalizar**: Pestaña "Configuración" → Ajustar a tu gusto

---

## 🎛️ Características Principales

### 🔥 **Sistema de Plugins Extensible**
- ✅ **Carga Dinámica** - Plugins se cargan automáticamente al inicio
- ✅ **Configuración Individual** - Cada plugin tiene su configuración YAML
- ✅ **Activación en Tiempo Real** - Enable/disable sin reiniciar
- ✅ **API Completa** - BasePlugin class para desarrollo personalizado
- ✅ **Gestión de Errores** - Plugins fallidos no afectan el sistema

### 🎨 **Interfaz Moderna y Personalizable**
- ✅ **Glassmorphism Effects** - Efectos de cristal con blur
- ✅ **Transparencia Dinámica** - Control deslizante por panel
- ✅ **Always-on-Top** - Visible sobre juegos y aplicaciones
- ✅ **Drag & Drop** - Reposiciona paneles libremente
- ✅ **Responsive Design** - Se adapta a diferentes resoluciones
- ✅ **Temas Personalizables** - Claro/Oscuro con colores custom

### ⚡ **Rendimiento Optimizado para Gaming**
- ✅ **Multi-threading** - Procesos en background sin bloquear UI
- ✅ **Low CPU Mode** - Modo de bajo consumo configurable
- ✅ **Gestión de Memoria** - Límites configurables y limpieza automática
- ✅ **Threading Seguro** - Qt Signals/Slots para comunicación
- ✅ **Overlay Compatible** - Funciona con mayoría de juegos

---

## 🎮 Plugins Incluidos

### 🎯 **Crosshair Overlay** ✅
```yaml
Estado: COMPLETAMENTE FUNCIONAL
Características:
  ✅ Múltiples estilos (cruz, punto, círculo, T)
  ✅ Colores personalizables con transparencia
  ✅ Tamaños y grosores ajustables
  ✅ Presets predefinidos
  ✅ Configuración por juego
  ✅ Hotkeys configurables
  ✅ Anti-aliasing y high-DPI
```

### 📊 **FPS Counter** ✅
```yaml
Estado: COMPLETAMENTE FUNCIONAL
Características:
  ✅ Contador en tiempo real
  ✅ Estadísticas (promedio, mín, máx)
  ✅ Colores por umbral de rendimiento
  ✅ Posicionamiento flexible
  ✅ Configuración de precisión
  ✅ Historial y logging
  ✅ Alertas de rendimiento bajo
```

### 🤖 **Anti-AFK Emulation** ✅
```yaml
Estado: COMPLETAMENTE FUNCIONAL - NUEVO
Características:
  ✅ Simulación inteligente de mouse (movimientos aleatorios mínimos)
  ✅ Simulación de teclado (WASD, Space, teclas configurables)
  ✅ Detección automática de juegos activos
  ✅ Intervalos aleatorios configurables (30-60s por defecto)
  ✅ Modo seguro (movimientos ±5 píxeles)
  ✅ Whitelist/Blacklist de juegos específicos
  ✅ Detección de actividad del usuario (pausa automática)
  ✅ Configuración avanzada con múltiples opciones
  ✅ UI en tiempo real con estado y countdown
  ✅ Características de seguridad y parada de emergencia
Uso: Previene desconexiones por AFK en juegos
```

### 💻 **CPU/GPU Monitor** ✅
```yaml
Estado: COMPLETAMENTE FUNCIONAL
Características:
  ✅ Monitoreo de CPU (uso, temperatura, frecuencia)
  ✅ Monitoreo de GPU (uso, memoria, temperatura)
  ✅ Monitoreo de RAM (uso, disponible)
  ✅ Barras de progreso visuales
  ✅ Alertas configurables
  ✅ Logging de métricas
  ✅ Configuración por juego
```

---

## ⌨️ Atajos de Teclado

| Atajo | Función | Estado |
|-------|---------|--------|
| `Ctrl+Shift+O` | Toggle Overlay General | ✅ |
| `Ctrl+Shift+C` | Toggle Panel de Control | ✅ |
| `Ctrl+Shift+H` | Ocultar Todo (Emergencia) | ✅ |
| `Ctrl+Shift+X` | Toggle Crosshair | ✅ |
| `Ctrl+Shift+F` | Toggle FPS Counter | ✅ |
| `Ctrl+Shift+M` | Toggle Monitor CPU/GPU | ✅ |
| `Ctrl+Shift+N` | Siguiente Preset Crosshair | ✅ |
| `Ctrl+Shift+R` | Reset Estadísticas FPS | ✅ |

---

## 📁 Estructura del Proyecto

```
gaming-helper-overlay/                    # 📦 Proyecto Principal
├── 📄 main.py                           # ✅ Punto de entrada
├── 📄 requirements.txt                   # ✅ Dependencias Python
├── 📄 version.py                        # ✅ Información de versión
├── 📄 run.bat / run.ps1                # ✅ Scripts de inicio
├── 📄 test_suite.py                     # ✅ Suite de pruebas
│
├── 📁 core/                             # ✅ Núcleo del Sistema
│   ├── 📄 app_core.py                  # ✅ Controlador principal
│   ├── 📄 config_manager.py            # ✅ Gestor de configuración
│   ├── 📄 plugin_manager.py            # ✅ Sistema de plugins
│   └── 📄 thread_manager.py            # ✅ Gestor de hilos
│
├── 📁 ui/                               # ✅ Interfaz de Usuario
│   ├── 📄 floating_panel.py            # ✅ Paneles flotantes base
│   ├── 📄 control_panel.py             # ✅ Panel de control principal
│   ├── 📄 icon_widget.py               # ✅ Icono flotante
│   ├── 📄 main_window.py               # ✅ Ventana principal
│   └── 📄 assets_manager.py            # ✅ Gestor de assets
│
├── 📁 plugins/                          # ✅ Plugins Integrados
│   ├── 📄 crosshair.py                 # ✅ Plugin de mira
│   ├── 📄 fps_counter.py               # ✅ Contador de FPS
│   └── 📄 cpu_gpu_monitor.py           # ✅ Monitor de sistema
│
├── 📁 config/                           # ✅ Configuraciones
│   ├── 📄 config.yaml                  # ✅ Config principal
│   └── 📁 plugins/                     # ✅ Configs por plugin
│       ├── 📄 crosshair.yaml
│       ├── 📄 fps_counter.yaml
│       └── 📄 cpu_gpu_monitor.yaml
│
├── 📁 data/                             # ✅ Datos de Usuario
│   ├── 📁 logs/                        # ✅ Archivos de log
│   ├── 📁 cache/                       # ✅ Cache temporal
│   ├── 📁 user_data/                   # ✅ Datos personalizados
│   └── 📁 plugins/                     # ✅ Datos de plugins
│
├── 📁 assets/                           # ✅ Recursos
│   ├── 📁 icons/                       # ✅ Iconos y gráficos
│   ├── 📁 sounds/                      # ✅ Efectos de sonido
│   └── 📁 animations/                  # ✅ Animaciones
│
└── 📁 docs/                             # ✅ Documentación
    ├── 📄 PLUGIN_DEVELOPMENT.md        # ✅ Desarrollo de plugins
    ├── 📄 ARCHITECTURE.md              # ✅ Arquitectura del sistema
    ├── 📄 INSTALLATION.md              # ✅ Guía de instalación
    ├── 📄 CHANGELOG.md                 # ✅ Historial de cambios
    └── 📄 LICENSE                      # ✅ Licencia MIT
```

---

## 📋 TODO List - Roadmap de Desarrollo

### 🎯 **Prioridad Alta** (Próxima Versión 1.1.0)
- [ ] **🖱️ Mouse Enhancer Plugin**
  - [ ] Crosshair que sigue al mouse
  - [ ] Efectos de click visual
  - [ ] Configuración de sensibilidad
  - [ ] Múltiples estilos de cursor

- [ ] **🖼️ Borderless Window Tool**
  - [ ] Detección automática de ventanas
  - [ ] Conversión a borderless automática
  - [ ] Lista de juegos compatibles
  - [ ] Configuración por juego

- [ ] **⌨️ Key Overlay Plugin**
  - [ ] Mostrar teclas presionadas en pantalla
  - [ ] Personalización de apariencia
  - [ ] Configuración para streaming
  - [ ] Historial de teclas

- [ ] **🔧 Mejoras del Sistema**
  - [ ] Sistema de actualizaciones automáticas
  - [ ] Migración de configuraciones entre versiones
  - [ ] Optimizaciones de rendimiento
  - [ ] Detección mejorada de juegos

### 🎮 **Prioridad Media** (Versión 1.2.0)
- [ ] **🎮 Steam Integration**
  - [ ] API de Steam para detección de juegos
  - [ ] Información de juegos (achievements, tiempo jugado)
  - [ ] Configuraciones automáticas por juego
  - [ ] Rich presence personalizado

- [ ] **💬 Discord Integration**
  - [ ] Rich presence con información de gaming
  - [ ] Estado personalizable
  - [ ] Integración con plugins activos
  - [ ] Webhook notifications

- [ ] **🔊 Audio Overlay Plugin**
  - [ ] Visualización de audio en tiempo real
  - [ ] Control de volumen por aplicación
  - [ ] Detección de comunicación por voz
  - [ ] Efectos visuales de sonido

- [ ] **📺 Streaming Tools**
  - [ ] Overlays específicos para streaming
  - [ ] Integración con OBS
  - [ ] Chat overlay para Twitch
  - [ ] Alertas de follows/subs

### 🚀 **Prioridad Baja** (Versión 2.0.0+)
- [ ] **☁️ Cloud Features**
  - [ ] Sincronización de configuraciones en la nube
  - [ ] Backup automático online
  - [ ] Compartir configuraciones entre dispositivos
  - [ ] Marketplace de plugins comunitarios

- [ ] **📱 Mobile Companion**
  - [ ] App móvil para control remoto
  - [ ] Notificaciones en el móvil
  - [ ] Configuración remota
  - [ ] Estadísticas de gaming

- [ ] **🤖 AI & Machine Learning**
  - [ ] Detección inteligente de juegos
  - [ ] Sugerencias automáticas de configuración
  - [ ] Análisis de patrones de juego
  - [ ] Optimización automática de rendimiento

- [ ] **🥽 Advanced Features**
  - [ ] Soporte para VR gaming
  - [ ] Control por gestos
  - [ ] Reconocimiento de voz
  - [ ] Integración con hardware gaming (RGB, etc.)

### 🔧 **Mejoras Técnicas Continuas**
- [ ] **Performance & Optimization**
  - [ ] Perfilado de rendimiento automático
  - [ ] Optimizaciones de memoria
  - [ ] Reducción de latencia
  - [ ] Mejor gestión de threading

- [ ] **Testing & Quality**
  - [ ] Tests unitarios completos
  - [ ] Tests de integración
  - [ ] CI/CD pipeline
  - [ ] Cobertura de código 90%+

- [ ] **Documentation & Community**
  - [ ] Tutoriales en video
  - [ ] Ejemplos de plugins avanzados
  - [ ] Wiki comunitaria
  - [ ] Foro de desarrolladores

---

## 🔍 Requisitos del Sistema

### ✅ **Mínimos** (Verificados)
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10+ (Testado con 3.13.5)
- **RAM**: 4GB (App usa ~100-200MB)
- **Storage**: 500MB espacio libre
- **GPU**: DirectX 11 compatible

### 🎯 **Recomendados** (Óptimo)
- **OS**: Windows 11 (última versión)
- **Python**: 3.11+ (mejor compatibilidad)
- **RAM**: 8GB+ (para gaming + overlay)
- **Storage**: 1GB+ (para datos y plugins)
- **GPU**: Moderna con OpenGL 3.3+
- **CPU**: Multi-core (para threading óptimo)

### 📋 **Dependencias** (Auto-instaladas)
```txt
PySide6>=6.5.0          # Framework UI Qt6
PyYAML>=6.0             # Configuración YAML
psutil>=5.9.0           # Monitoreo del sistema
requests>=2.28.0        # Cliente HTTP para APIs
```

---

## 🐛 Troubleshooting

### ❓ **Problemas Comunes**

#### 🔴 La aplicación no inicia
```bash
# Verificar Python
python --version  # Debe ser 3.10+

# Reinstalar dependencias
pip install -r requirements.txt

# Ejecutar con debug
python main.py --debug
```

#### 🔴 Paneles no son visibles
1. **Verificar posición**: Pueden estar fuera de pantalla
2. **Always-on-top**: Activar en configuración
3. **Transparencia**: Revisar si no está 100% transparente
4. **Juego fullscreen**: Usar modo borderless windowed

#### 🔴 Alto uso de CPU
1. **Activar Low CPU Mode**: En configuración de rendimiento
2. **Reducir frecuencia de actualización**: FPS counter y monitor
3. **Desactivar plugins no usados**: Solo mantener los necesarios
4. **Revisar logs**: Buscar loops infinitos o errores

#### 🔴 Plugins no cargan
1. **Verificar archivos**: Comprobar integridad de archivos .py
2. **Revisar logs**: `data/logs/plugins.log` para errores específicos
3. **Configuración**: Verificar `config/plugins/` archivos
4. **Permisos**: Ejecutar como administrador si es necesario

### 🔧 **Modo Debug**

Activar logging detallado editando `config/config.yaml`:
```yaml
logging:
  level: "DEBUG"
  log_to_console: true
```

O ejecutar con flag debug:
```bash
python main.py --debug
```

---

## 🤝 Contribuir

### 📝 **Guías de Contribución**
1. **Fork** el repositorio
2. **Crear rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Commit** cambios: `git commit -m 'Add: nueva funcionalidad'`
4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`
5. **Crear Pull Request** con descripción detallada

### 🎨 **Tipos de Contribuciones**
- 🐛 **Bug fixes** - Corrección de errores
- ✨ **Features** - Nuevas funcionalidades
- 📚 **Documentation** - Mejoras de documentación
- 🎨 **UI/UX** - Mejoras de interfaz
- ⚡ **Performance** - Optimizaciones
- 🧪 **Tests** - Pruebas adicionales
- 🔌 **Plugins** - Nuevos plugins

### 📋 **Coding Standards**
- **Style**: PEP 8 compliance
- **Docstrings**: Google style
- **Type hints**: Python 3.10+ annotations
- **Tests**: Pytest para nuevas funcionalidades
- **Commits**: Conventional Commits format

---

## 📚 Documentación

### 📖 **Para Usuarios**
- **[README.md](README.md)** - Esta guía completa
- **[INSTALLATION.md](INSTALLATION.md)** - Instalación paso a paso
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de versiones

### 👨‍💻 **Para Desarrolladores**
- **[PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)** - Crear plugins personalizados
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura del sistema
- **[API Documentation](docs/)** - Referencia de API completa

### ⚙️ **Configuración**
- **[config/README.md](config/README.md)** - Guía de configuración
- **[data/README.md](data/README.md)** - Gestión de datos

---

## 📄 Licencia

```
MIT License

Copyright (c) 2024 Party Brasil

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

Ver archivo completo: **[LICENSE](LICENSE)**

---

## 👨‍💻 Autor

<div align="center">

**🎮 Party Brasil**

[![GitHub](https://img.shields.io/badge/GitHub-@partybrasil-181717?style=for-the-badge&logo=github)](https://github.com/partybrasil)
[![Email](https://img.shields.io/badge/Email-contact@partybrasil.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contact@partybrasil.dev)

*Desarrollador apasionado por gaming y herramientas que mejoran la experiencia de juego*

</div>

---

## 🙏 Agradecimientos

### 🛠️ **Tecnologías Utilizadas**
- **[PySide6](https://doc.qt.io/qtforpython/)** - Framework UI potente y moderno
- **[psutil](https://github.com/giampaolo/psutil)** - Monitoreo del sistema multiplataforma
- **[PyYAML](https://pyyaml.org/)** - Gestión de configuración elegante
- **[Python](https://python.org)** - Lenguaje base robusto y versátil

### 💡 **Inspiración**
- **Gaming Community** - Por el feedback y ideas continuas
- **Open Source Projects** - Por los ejemplos y mejores prácticas
- **Qt/PySide Documentation** - Por la excelente documentación técnica

---

<div align="center">

## 🎉 **¡PROYECTO COMPLETADO!** 🎉

### ⭐ Si te gusta el proyecto, ¡dale una estrella! ⭐

**Gaming Helper Overlay v1.0.0** - *Construido con ❤️ para la comunidad gaming*

---

### 🚀 **¿Listo para Comenzar?**

```bash
git clone https://github.com/partybrasil/gaming-helper-overlay.git
cd gaming-helper-overlay
python main.py
```

**¡Tu experiencia de gaming mejorada te espera!** 🎮✨

</div>