# 📊 Manual de Usuario - Vantec VCORE Dashboard (Protocolos L5)

Este manual es su guía para operar el **Vantec VCore Dashboard**, el sistema que le otorga control total sobre sus comprobantes fiscales.

---

## 🎨 1. Entorno de Trabajo Vantec
El Dashboad presenta un diseño intuitivo basado en el **ADN Vantec** (Azul Real `#1E3A5F` y Azul Cielo `#4EBCE9`), garantizando que la visibilidad de su información sea prioritaria. 

### Secciones Clave:
1.  **📊 Dashboard Global:** Resumen de facturación, pagos aplicados y estatus de deuda.
2.  **📂 Explorador de Documentos:** Listado masivo con búsqueda inteligente por Folio, RFC y UUID.
3.  **📧 Centro de Reenvío:** Capacidad para enviar facturas (XML + PDF) directamente a sus clientes por correo electrónico.

---

## 📥 2. Carga Universal (El Buzón Simple)
Para cargar facturas, usted **no necesita navegar menús complejos**. Simplemente "suelte" sus archivos (XML, PDF o ambos) en la carpeta compartida:
`Operacion_CFDI\Upload_Universal`

### ¿Qué hace VCore por usted?
-   **Valida el XML (Ancla):** Crea el registro en su contabilidad.
-   **Busca el PDF (Testigo):** Si soltó solo el XML, VCore buscará en su "memoria fiscal" (Orphans) si el PDF ya llegó previamente.
-   **Seguridad:** Si el archivo es basura o no fiscal, el sistema lo expulsará automáticamente a la carpeta `Invalid_ADN`.

---

## 📨 3. Cómo reenviar un comprobante
1.  Busque la factura en el **Explorador**.
2.  Haga clic en el botón de **Reenvío**.
3.  Ingrese el correo del destinatario y presione **Enviar**.
    *VCore adjuntará automáticamente el XML y el PDF correspondiente.*

---

## 💡 4. Consejos VCORE
-   **Carga de Anexos:** Si tiene una proforma o acuse, simplemente suéltelo en el buzón. VCore lo detectará como anexo y lo sumará al expediente de la factura existente.
-   **Estado de Salud:** Si ve un contador de **[2]** en el campo de adjuntos, significa que tiene la Factura + un Anexo guardado.

---

**Centro de Ayuda Vantec**
*El Estándar de Oro en Gestión Fiscal*
🏁 **ESTATUS: TOTALMENTE OPERATIVO**
