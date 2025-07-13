# Gaming Helper Overlay Configuration Files

Esta carpeta contiene todos los archivos de configuración de la aplicación Gaming Helper Overlay.

## Estructura de Archivos

### `config.yaml`
Archivo principal de configuración con todas las configuraciones globales de la aplicación.

**Secciones principales:**
- `app`: Configuraciones generales de la aplicación
- `ui`: Configuraciones de interfaz de usuario
- `plugins`: Configuraciones específicas de plugins
- `logging`: Configuraciones del sistema de logs
- `performance`: Configuraciones de rendimiento

### `plugins/`
Carpeta que contiene configuraciones específicas de cada plugin instalado.

**Archivos por plugin:**
- `crosshair.yaml`: Configuración del plugin de mira
- `fps_counter.yaml`: Configuración del contador de FPS
- `cpu_gpu_monitor.yaml`: Configuración del monitor de sistema
- `[nombre_plugin].yaml`: Configuraciones de plugins personalizados

### `themes/`
Carpeta con archivos de temas personalizados (se crea automáticamente).

### `keybinds/`
Carpeta con configuraciones de atajos de teclado personalizados (se crea automáticamente).

## Uso

### Edición Manual
Puedes editar estos archivos directamente con cualquier editor de texto que soporte YAML.

**Importante:** 
- Respeta la indentación (usa espacios, no tabs)
- Haz backup antes de editar archivos importantes
- Reinicia la aplicación para aplicar cambios

### Edición por Interfaz
La mayoría de configuraciones se pueden cambiar desde la interfaz de usuario:
1. Abre el Panel de Control
2. Ve a la pestaña "Configuración"
3. Modifica las opciones deseadas
4. Los cambios se guardan automáticamente

## Backup y Restauración

### Crear Backup
```bash
# Copia toda la carpeta de configuración
cp -r config/ config_backup_$(date +%Y%m%d)/
```

### Restaurar Backup
```bash
# Restaura desde un backup
cp -r config_backup_YYYYMMDD/* config/
```

### Reset a Valores por Defecto
Si necesitas restaurar la configuración original:
1. Cierra la aplicación
2. Elimina o renombra la carpeta `config/`
3. Reinicia la aplicación (se creará una nueva configuración por defecto)

## Estructura de config.yaml

```yaml
app:
  name: "Gaming Helper Overlay"
  version: "1.0.0"
  auto_start: false
  minimize_to_tray: true
  check_updates: true

ui:
  theme: "dark"
  transparency: 0.8
  always_on_top: true
  font_size: 12
  language: "es"

plugins:
  auto_discover: true
  enabled_plugins:
    - crosshair
    - fps_counter
    - cpu_gpu_monitor

logging:
  level: "INFO"
  max_file_size: "10MB"
  backup_count: 5
  log_to_file: true

performance:
  low_cpu_mode: false
  max_fps: 60
  thread_pool_size: 4
```

## Configuraciones Avanzadas

### Variables de Entorno
Algunas configuraciones pueden sobrescribirse con variables de entorno:

- `GAMING_OVERLAY_CONFIG_DIR`: Directorio personalizado de configuración
- `GAMING_OVERLAY_LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
- `GAMING_OVERLAY_THEME`: Tema por defecto

### Configuración Portable
Para uso portable, crea un archivo `portable.txt` en la raíz de la aplicación. Esto hará que todas las configuraciones se guarden en la carpeta de la aplicación en lugar del directorio del usuario.

## Solución de Problemas

### Archivo de Configuración Corrupto
Si la aplicación no inicia debido a un archivo de configuración corrupto:
1. Renombra `config.yaml` a `config.yaml.bak`
2. Reinicia la aplicación
3. Se creará un nuevo archivo de configuración

### Permisos de Escritura
Si tienes problemas de permisos:
1. Ejecuta la aplicación como administrador
2. O mueve la aplicación a una carpeta con permisos de escritura

### Conflictos de Plugins
Si un plugin causa problemas:
1. Edita `config.yaml`
2. Elimina el plugin problemático de `enabled_plugins`
3. Reinicia la aplicación

## Migración de Versiones

Cuando actualices la aplicación, las configuraciones se migrarán automáticamente si es necesario. Si hay cambios incompatibles, se creará un backup automático de la configuración anterior.

---

*Para más información, consulta la documentación completa en el README.md*
