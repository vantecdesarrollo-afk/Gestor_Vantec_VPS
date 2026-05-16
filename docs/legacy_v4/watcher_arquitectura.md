# ARQUITECTURA DEL WATCHER
**Objetivo:** Ingesta automática sin pérdida de datos.

1. MONITOR: Solo vigila la carpeta 'Upload_Universal'.
2. COMPATIBILIDAD SAT: El Parser debe entender tanto 'FormaPagoP' como 'FormaDePagoP'. 
3. UNIDAD DE ARCHIVO: El XML y el PDF deben moverse JUNTOS. Si solo llega uno, se sube también y si posteriormente llegan un PDF del folio se valida si es qeu no se tiene y se sube o si se tiene problema se pasan a '\Orphans'.
4. LOGS DE EXCEPCIÓN: 
   - El log 'watcher_vcore.log' SOLO registra ERRORES. 
   - Si el archivo sube bien, el log debe estar vacío (Silent Success).
5. NO DESTRUIR: Queda prohibido borrar archivos del sistema sin que exista una copia en la carpeta de 'duplicates' o 'failed' del Tenant.