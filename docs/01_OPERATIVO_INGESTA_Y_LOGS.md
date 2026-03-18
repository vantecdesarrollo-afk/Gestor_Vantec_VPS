# ?? GESTOR CFDI - MANUAL OPERATIVO DE INGESTA
**M車dulo:** Inbound Engine (Sustituci車n de Legacy)
**Gemini Skill Requerido:** `Vantec-FastAPI-Skill` (Manejo estricto de I/O y rutas absolutas).

## 1. Pipeline de 4 Estados (Regla de Oro Anti-Colisi車n)
El sistema opera en 4 zonas de carpetas adyacentes a la definida en `WATCHER_ZONES`. Todo movimiento debe usar `os.path.abspath`:

1. **`inbound/` (Carpeta Monitoreada)**: Donde el ERP/Cliente deposita los archivos (XML y PDF).
2. **`processing/`**: Los archivos se mueven aqu赤 **at車micamente** ANTES de ser le赤dos. Esto evita colisiones de lectura mientras se copian por red en Windows.
3. **`failed/`**: Destino de archivos con problemas estructurales o versiones no soportadas.
4. **`logs_ingesta/`**: Carpeta para archivos `.log` detallados del error con el nombre `<Archivo>_error.log`.

## 2. Flujo de Procesamiento y Validaci車n Obligatoria
1. **Detecci車n**: XML y PDF caen en `inbound`.
2. **Movimiento**: Traslado inmediato a `processing`.
3. **Indexaci車n**: El parser lee metadata del XML y calcula la `ruta_resguardo` real (Validaci車n de Sad Path: ?Qu谷 pasa si el XML no tiene UUID?).
4. **Persistencia**: Se inserta en la tabla `comprobantes` v赤a PostgreSQL, respetando el aislamiento `entidad_id`.
5. **Limpieza**: Se elimina la copia ef赤mera de `processing/`.

## 3. Soporte, Logs y Alertas (Integraci車n n8n)
En caso de falla, el `.log` en `logs_ingesta/` contiene la traza `str(e)` de la excepci車n. 
* **Regla de Observabilidad:** Todo error cr赤tico en esta fase debe disparar un Webhook as赤ncrono a nuestro VPS de **n8n** para notificar al equipo de soporte antes de que el cliente lo reporte.