# ⚙️ 02_ESPECIFICACION_PARSER_MULTIVERSION
**Propósito:** Extracción de metadata fiscal para versiones 3.2, 3.3 y 4.0.
**Gemini Skill Requerido:** `Vantec-FastAPI-Skill` (Parsing estricto y fidelidad de datos).

## 1. Lógica de Identificación (Wildcard Namespaces)
Para garantizar la resistencia del parser ante cambios de namespaces:
* **Uso de XPath Wildcard**: Se utiliza la sintaxis `{*}Node` (ej. `.//{*}Emisor`) para buscar en cualquier namespace.
* **Case Insensitivity de Atributos**: El código intenta extraer el atributo con mayúscula y minúscula (ej. `get('Total') or get('total')`).

## 2. Regla de Oro de Extracción (Anti-Regresión de Pagos)
Queda estrictamente prohibido mapear el `SubTotal` o `Total` del nodo raíz si el documento es un REP (Pago).
* **Para CFDIs Tipo 'I' o 'E':** Extraer del nodo raíz (`get('Total')`).
* **Para CFDIs Tipo 'P':** El parser **DEBE** navegar al complemento y extraer el valor de `pago20:Totales -> MontoTotalPagos` (o su equivalente en v1.0). Entregar un Pago con valor `$0.00` se considera una falla crítica.

## 3. Estrategia de Inyección a Base de Datos
1. **Detección y Parsing**: Extrae UUID, Serie, Folio, RFC Emisor/Receptor y Total exacto.
2. **Mapeo de Ruta Absoluta**: Calcula la `ruta_resguardo` real. *Evidencia Obligatoria:* Antes de guardar, el código debe validar con `os.path.exists()` que la ruta destino sea alcanzable.
3. **Persistencia y Finalización**: Inserta en la tabla `comprobantes` y elimina el archivo efímero.