# 🔬 PILAR 2: MANUAL TÉCNICO Y DE OPERACIÓN (VCore v5.0.0)

Este documento contiene los protocolos operativos y directivas de seguridad para el mantenimiento avanzado del entorno Vantec Core. Toda intervención técnica debe alinearse a este documento de gobierno.

## 1. Gestión de Ingesta y Watcher Recursivo
El sistema utiliza un demonio centinela (`vcore_manager.py` > `watcher.py`) que detecta iterativamente cualquier XML y PDF colocado en `Upload_Universal`.

**Flujo Operativo (Idempotencia Binaria MD5):**
1. Escaneo Multiprocesado sobre la carpeta física.
2. Identificación del algoritmo MD5 del archivo entrante.
3. Si el archivo ya se registró en `comprobantes.pdf_path` u `xml_path`, se mueve automáticamente a la sub-bóveda `/logs/duplicates/`.
4. Extracción de Identidades: El motor lee en formato BOM-UTF8 asegurando los nodos XML sin corrupción.

## 2. Protocolo Anti-Contaminación (Limpieza de PDFs)
Bajo la Directiva L6 v7.6 se resolvió la fuga transaccional de "herencia basura".
El script `fix_pdf_paths.py` debe ser llamado para deduplicar forzosamente un identificador si un Pago intenta inyectar su UUID dentro de la "Factura Padre" u otros CFDI no tipo `T` (Traslado).

```python
# Extracto del Script de Deduplicación Segura:
if comp.tipo_comprobante != 'T':
    paths = [p for p in comp.pdf_path.split('|') if p.strip()]
    if len(paths) > 1:
        # Purgando UUIDs anexos ajenos al Documento
        comp.pdf_path = paths[0] 
```

![Evidencia SSoT de Depuración](../../assets/docs_manuals/Evidencia_SSoT_AAC2496.png)

## 3. Seguridad Sentinel y Timers
El protocolo Sentinel está codificado directamente en la capa de intercepción (Middleware UI).
*   **Idle Tracker:** Todo movimiento de mouse, scroll y tecleo reinicia el timer (JavaScript Tracker).
*   **Auto-Logout (15 min):** Si no hay actividad, se fuerza `removeItem('token')` local y redirección con el tag `reason=Sesión expirada`.
*   **Recuperación Criptográfica:** El módulo SMTP genera un PIN de un solo uso que encripta la nueva contraseña en bcrypt, desarmando la bóveda por 5 minutos hasta completarse.

## 4. Evidencia Visual del Log (Saneamiento)
Para corroborar la respuesta de la Idempotencia MD5 sobre el búnker, a continuación se anexa el comportamiento del motor rechazando archivos duplicados para proteger la integridad SSoT.

![Evidencia del Log Sentinel](../../assets/docs_manuals/Sentinel_Timeout.jpg)
*(Nota: El registro audit captura explícitamente qué UUID ha sido preservado y movido).*
