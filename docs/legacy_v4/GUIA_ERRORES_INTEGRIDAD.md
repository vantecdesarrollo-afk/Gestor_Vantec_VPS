# Guía de Errores de Integridad Financiera (VCORE L6)

Esta guía detalla los estados de auditoría generados por el motor de conciliación de Vantec.

## Estatus: AUSENTE (Fantasma Rojo 👻)

**Significado**: 
El sistema ha detectado un **Pago (REP)** o un registro de ingreso que hace referencia a una factura con método de pago **PPD**, pero dicha factura "padre" **no se encuentra registrada** en la base de datos de Vantec.

**Causas comunes**:
1. **Omisión de Ingesta**: La factura PPD fue emitida pero no se ha cargado al sistema (vía Watcher o Carga Manual).
2. **Desfase de Auditoría**: El pago llegó a la zona de ingesta antes que la factura original.
3. **Error de Emisor**: El emisor del pago referenció un UUID inexistente o erróneo.

**Acción Requerida**:
- Localizar el archivo XML de la factura PPD faltante y depositarlo en la carpeta de ingesta (`Operacion_CFDI\Upload`).
- El Watcher procesará la factura y el estatus del pago cambiará automáticamente de **AUSENTE** a **Pagado/Parcial** en el próximo ciclo de sincronización.

---
*Documento generado bajo el Protocolo L6 de Integridad Financiera.*
