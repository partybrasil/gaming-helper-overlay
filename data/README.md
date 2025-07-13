# Gaming Helper Overlay Data Directory

Esta carpeta contiene todos los datos generados y utilizados por la aplicación Gaming Helper Overlay durante su funcionamiento.

## Estructura de Carpetas

### `logs/`
Contiene todos los archivos de registro de la aplicación.

**Archivos de log:**
- `app.log`: Log principal de la aplicación
- `plugins.log`: Logs específicos de plugins
- `errors.log`: Registro de errores críticos
- `performance.log`: Métricas de rendimiento
- `debug.log`: Información de depuración (solo en modo debug)

**Rotación de logs:**
- Los logs se rotan automáticamente cuando alcanzan 10MB
- Se mantienen hasta 5 archivos de backup
- Formato: `app.log.1`, `app.log.2`, etc.

### `cache/`
Almacena datos temporales y caché para mejorar el rendimiento.

**Contenido típico:**
- `icons/`: Iconos cacheados
- `themes/`: Temas descargados
- `plugin_data/`: Datos temporales de plugins
- `assets/`: Assets cacheados (imágenes, sonidos)

### `user_data/`
Datos específicos del usuario que persisten entre sesiones.

**Archivos de usuario:**
- `statistics.json`: Estadísticas de uso de la aplicación
- `session_data.json`: Datos de la sesión actual
- `custom_assets/`: Assets personalizados del usuario
- `backups/`: Backups automáticos de configuración

### `plugins/`
Datos específicos de cada plugin.

**Estructura por plugin:**
```
plugins/
├── crosshair/
│   ├── presets.json       # Presets guardados
│   ├── custom_images/     # Imágenes personalizadas
│   └── usage_stats.json   # Estadísticas de uso
├── fps_counter/
│   ├── history.json       # Historial de FPS
│   └── benchmarks.json    # Benchmarks guardados
└── cpu_gpu_monitor/
    ├── performance_data.json
    └── alerts_history.json
```

### `temp/`
Archivos temporales que se pueden eliminar sin problemas.

**Limpieza automática:**
- Se limpia al inicio de la aplicación
- Contiene archivos de trabajo temporal
- Downloads parciales y archivos de actualización

## Gestión de Datos

### Tamaño y Mantenimiento

**Tamaños típicos:**
- `logs/`: 50-100MB (dependiendo del uso)
- `cache/`: 20-50MB
- `user_data/`: 5-20MB
- `plugins/`: 10-100MB (dependiendo de plugins instalados)

**Limpieza automática:**
- Los logs antiguos se eliminan automáticamente
- La caché se limpia periódicamente
- Los archivos temporales se eliminan al inicio

### Backup de Datos

**Datos importantes a respaldar:**
- `user_data/` - Contiene configuraciones personalizadas
- `plugins/*/presets.json` - Presets personalizados
- `plugins/*/custom_*` - Assets personalizados

**Datos que NO necesitan backup:**
- `logs/` - Se regeneran automáticamente
- `cache/` - Se reconstruye automáticamente
- `temp/` - Archivos temporales

### Migración y Portabilidad

**Para mover la aplicación:**
1. Copia las carpetas `config/` y `data/user_data/`
2. Opcionalmente, copia `data/plugins/` para mantener presets
3. Los logs y caché se recrearán en la nueva ubicación

**Para reset completo:**
1. Elimina toda la carpeta `data/` (excepto `user_data/` si quieres mantener tus datos)
2. Reinicia la aplicación

## Archivos de Datos Específicos

### `statistics.json`
```json
{
  "app_launches": 42,
  "total_runtime": 86400,
  "plugin_usage": {
    "crosshair": {"activations": 25, "runtime": 3600},
    "fps_counter": {"activations": 40, "runtime": 7200}
  },
  "performance_metrics": {
    "avg_cpu_usage": 2.5,
    "avg_memory_usage": 125,
    "crash_count": 0
  }
}
```

### `session_data.json`
```json
{
  "last_session": "2024-01-01T12:00:00Z",
  "window_positions": {
    "control_panel": {"x": 100, "y": 100, "width": 400, "height": 600},
    "floating_icon": {"x": 50, "y": 50}
  },
  "active_plugins": ["crosshair", "fps_counter"],
  "current_theme": "dark"
}
```

## Privacidad y Seguridad

### Información Personal
- **NO se almacena información personal identificable**
- Solo estadísticas de uso anónimas
- Configuraciones locales únicamente

### Datos de Juegos
- Se pueden almacenar nombres de juegos detectados
- Estadísticas de rendimiento por juego (opcional)
- No se almacena contenido de juegos

### Seguridad de Archivos
- Todos los archivos son texto plano o JSON
- No se almacenan contraseñas o tokens de autenticación
- Los datos están disponibles solo para el usuario actual del sistema

## Solución de Problemas

### Datos Corruptos
Si encuentras problemas con datos corruptos:

1. **Identificar el archivo problemático:**
   - Revisa `logs/errors.log` para identificar el archivo
   
2. **Backup y eliminar:**
   ```bash
   # Hacer backup del archivo corrupto
   mv data/user_data/statistics.json data/user_data/statistics.json.bak
   
   # La aplicación recreará el archivo al reiniciar
   ```

3. **Reset completo de datos:**
   ```bash
   # Backup completo
   mv data/ data_backup_$(date +%Y%m%d)/
   
   # Reiniciar aplicación para crear datos nuevos
   ```

### Espacio en Disco
Si los datos ocupan demasiado espacio:

1. **Limpiar logs antiguos:**
   ```bash
   # Eliminar logs de más de 30 días
   find data/logs/ -name "*.log.*" -mtime +30 -delete
   ```

2. **Limpiar caché:**
   ```bash
   # Eliminar toda la caché
   rm -rf data/cache/*
   ```

3. **Limpiar archivos temporales:**
   ```bash
   # Eliminar archivos temporales
   rm -rf data/temp/*
   ```

### Permisos de Acceso
Si tienes problemas de permisos:

1. **Verificar propietario:**
   ```bash
   # Windows (PowerShell)
   Get-Acl data/ | Select-Object Owner
   
   # Cambiar propietario si es necesario
   takeown /f data\ /r /d y
   ```

2. **Ejecutar como administrador:**
   - Clic derecho en la aplicación → "Ejecutar como administrador"

## Monitoreo y Análisis

### Archivos de Métricas
La aplicación genera métricas de rendimiento en:
- `data/logs/performance.log`: Métricas detalladas
- `data/user_data/statistics.json`: Resumen de estadísticas

### Análisis de Uso
Puedes analizar tu uso de la aplicación revisando:
- Tiempo total de uso por plugin
- Frecuencia de activación de características
- Rendimiento del sistema durante el uso

---

*Para más información sobre configuración, consulta config/README.md*
