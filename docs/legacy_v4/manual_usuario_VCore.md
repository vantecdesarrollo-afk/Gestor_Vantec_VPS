# 📘 Manual de Operación Vantec (Nivel Usuario)

Bienvenido al **Gestor de CFDI Vantec**. Este manual le guiará a través de las reglas básicas para asegurar que sus facturas y documentos logísticos estén siempre sincronizados y disponibles.

---

## 🐣 1. La Regla de Oro: El XML es el Acta de Nacimiento
Para el sistema, el archivo **.xml** es el documento único y oficial. Sin él, la factura no existe en el Dashboard.

> [!IMPORTANT]
> **Sin XML no hay registro financiero.**
> Esta regla es **UNIVERSAL** y protege todas sus facturas de **Ingreso, Egreso, Traslado, Nómina y Pagos**. El sistema ahora cuenta con **Superpoderes de Lectura (Híbrida)** que detectan la identidad de sus facturas incluso si están comprimidas o son de formato moderno. El XML sigue siendo el ancla obligatoria para el Dashboard.

---

## 📂 2. ¿Por qué mi archivo fue rechazado? (El Filtro de Triaje)
Dependiendo de la naturaleza del archivo, el sistema lo enviará a uno de los dos "cementerios" de auditoría:

### A. Carpeta `Invalid_ADN` (Filtro Civil)
**¿Qué hay aquí?** Basura o errores de carga.
- Archivos que **NO son facturas** (ej. una foto, un Word o un PDF sin datos fiscales).
- El sistema los rechaza totalmente porque no tienen validez legal. Si su archivo termina aquí, revise que sea un PDF de factura real. El motor v3.1 es infalible: si hay datos fiscales, los encontrará.

### B. Carpeta `Orphans` (Filtro Fiscal)
**¿Qué hay aquí?** Alertas de Gestión de Alta Prioridad.
- Facturas reales que **NO tienen su XML** registrado.
- Es una alerta para que usted suba el XML correspondiente. Esta protección es **UNIVERSAL** para sus facturas de Ingreso, Egreso, Nómina y Traslado.

---

## 🛠️ 3. Guía de Rescate: Cómo recuperar un archivo de Orphans
Si su PDF fue enviado a `Orphans` por falta de XML, siga estos pasos:

1.  **Subir el XML:** Cargue el archivo XML correspondiente a la carpeta `Upload_Universal`.
2.  **Ventana de Gracia:** Espere 30 segundos (el sistema protege el archivo contra errores de Windows).
3.  **Mover el PDF:** Mueva su archivo desde `Orphans` de vuelta a la carpeta `Upload_Universal`.
4.  **Éxito:** El sistema lo detectará, vinculará y actualizará su Dashboard automáticamente.

---

## 🚀 4. Multicarga: Arrastre y Olvide
El sistema es inteligente. Usted no necesita preocuparse por "pegar" el PDF a la factura manualmente.

- **Carga Inicial:** Puede subir el XML y el PDF juntos en la misma carpeta.
- **Carga Posterior (Anexos):** Si ya tiene una factura en el Dashboard y le llega un nuevo PDF (ej. una constancia de entrega o evidencia logística), simplemente arrástrelo a la carpeta de carga. 
- **Magia Vantec (Match Identitario):** El sistema leerá el interior del PDF, encontrará el UUID de la factura y lo "pegará" automáticamente al registro existente.

---

## 📂 5. El Menú PDF: ¿Qué significa el [2]?
Cuando vea un indicador rojo **[2]** (o superior) junto al ícono del PDF, significa que esa factura posee múltiples documentos vinculados (ej. Factura Fiscal + Evidencia Logística).

### Cómo usarlo:
1.  **Clic en el Ícono:** En lugar de una descarga automática, se abrirá un menú desplegable justo debajo del botón.
2.  **Selección:** Elija el nombre del archivo original que desea consultar.
3.  **Descarga Directa:** El navegador iniciará una descarga limpia del archivo seleccionado (peso real de +100KB).

---

> [!TIP]
> Si una factura no tiene el ícono de PDF activo, asegúrese de haber subido el PDF correcto a la carpeta de Vigilancia (Upload Universal) siguiendo el orden cronológico: **Primero XML, luego PDF.**
