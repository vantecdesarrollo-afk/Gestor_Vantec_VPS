# ?? 03_GUIA_SOLUCION_ERRORES_INGESTA
**Prop車sito:** Diccionario de errores comunes para soporte t谷cnico y flujos de mitigaci車n.

## 1. Errores de Estructura XML o Formato
Cuando el archivo cae en `failed/` y genera log en `logs_ingesta/`:

| Error en Log | Causa Ra赤z | Soluci車n (Humana o v赤a n8n) |
| :--- | :--- | :--- |
| `UUID no encontrado` | El XML no ha sido timbrado por el SAT. | Notificar al emisor. El sistema debe ignorarlo autom芍ticamente. |
| `not well-formed` | El archivo XML est芍 corrupto o truncado. | Re-solicitar el archivo original. |
| `TypeError: float()...` | El Atributo `Total` est芍 vac赤o. | Validar regla de extracci車n de Tipo 'P' (Ver Documento 02). |

## 2. Errores de Negocio u Operaci車n
| Error en Log | Causa Ra赤z | Soluci車n |
| :--- | :--- | :--- |
| `Fallo en shutil.move` | Colisi車n de Permisos en Windows (File lock). | Revisar si el antivirus del host bloque車 el archivo. |
| `Ruta no encontrada` | Falla en resoluci車n f赤sica de volumen Docker. | Verificar mapeo en `docker-compose.yml` y forzar `os.path.abspath`. |

## 3. Procedimiento de Rescate y Evidencia
1. Corregir el archivo o la anomal赤a de permisos.
2. Mover de `failed/` de regreso a `inbound/`.
3. El sistema lo re-procesar芍 autom芍ticamente.
4. **Cierre:** El t谷cnico debe registrar en la bit芍cora la causa para retroalimentar los flujos de prevenci車n de n8n.