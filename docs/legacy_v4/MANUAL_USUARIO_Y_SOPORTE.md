# MANUAL DE USUARIO Y SOPORTE (Gestor CFDI)

Este manual describe el funcionamiento administrativo del sistema Gestor CFDI Vantec para personal de operación y soporte técnico.

---

## 1. Proceso de Carga de Facturas (Ingesta)

El sistema cuenta con un **Watcher (Vigilante)** que monitorea carpetas de forma automática. Para cargar facturas (XML y PDF):

1. **Ubicar la carpeta maestra**: Acceda a `\Operacion_CFDI\Upload_Universal`.
2. **Depositar archivos**: Copie sus archivos XML y PDF directamente en esta carpeta.
3. **Procesamiento automático**: 
   - El sistema leerá el **RFC del Emisor** dentro del XML.
   - Si el RFC está registrado, moverá los archivos a la carpeta del cliente correspondiente automáticamente.
   - Si el XML es corrupto, se moverá a `\Invalid_ADN`.
   - Si el RFC no existe en el sistema, se moverá a `\Orphans`.

---

## 2. Ubicación de Archivos y Troubleshooting

### ¿A dónde se fueron mis archivos?
Una vez procesados, los archivos se organizan por RFC en `\Operacion_CFDI\[RFC_DEL_CLIENTE]`. Dentro encontrará:
- `\processing`: Archivos en cola de lectura.
- `\failed`: Archivos que el SAT rechazaría o con errores técnicos.
- `\Files`: **Bóveda Final**. Aquí se guardan permanentemente organizados por Año y Mes.
- `\logs`: Archivos de texto que explican por qué falló un documento específico.

### Diccionario Visual de Carpetas
| Carpeta | Uso |
| :--- | :--- |
| `Upload_Universal` | **Deposite aquí todo.** Es la única entrada. |
| `Invalid_ADN` | El archivo no es un XML de factura válido. |
| `Orphans` | El RFC no ha sido dado de alta en la Configuración del sistema. |
| `Files` | El archivo ya está seguro en la base de datos y disponible en el Dashboard. |

---

## 3. Soporte Técnico: Reiniciar el Vigilante (Watcher)

Si deposita archivos en `Upload_Universal` y no desaparecen después de 10 segundos, el servicio debe reiniciarse.

### Opción A (PM2)
Abra una terminal y ejecute:
```bash
pm2 restart vantec-watcher
```

### Opción B (Windows Service / NSSM)
1. Presione `Win + R`, escriba `services.msc` y enter.
2. Busque el servicio llamado **"VantecWatcher"**.
3. Haga clic derecho y seleccione **"Reiniciar"**.

---

## 4. Notas de Seguridad
- Nunca borre archivos directamente de la carpeta `Files`, use la interfaz del sistema.
- Los archivos en `failed` deben ser revisados por un contador para validar su estructura fiscal.
