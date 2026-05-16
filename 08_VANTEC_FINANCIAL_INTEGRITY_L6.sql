-- 08_VANTEC_FINANCIAL_INTEGRITY_L6.sql
-- Auditoría de Anomalías y Refinamiento de Semáforo

-- 1. Tabla de Auditoría de Anomalías Financieras (L6 Protocol)
CREATE TABLE IF NOT EXISTS financial_anomalies_logs (
    id SERIAL PRIMARY KEY,
    entidad_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    uuid_documento UUID NOT NULL,
    tipo_anomalia VARCHAR(50) NOT NULL, -- 'PAGO_HUERFANO', 'MONTO_DISCREPANTE', 'GHOST_RECOVERY'
    detalle TEXT,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estatus_anomalia VARCHAR(20) DEFAULT 'ACTIVA' -- 'ACTIVA', 'RESUELTA'
);

-- 2. Indice para búsquedas rápidas de REPs huérfanos
CREATE INDEX IF NOT EXISTS idx_comprobantes_orphan ON comprobantes(orphan_payment) WHERE orphan_payment = TRUE;

-- 3. Vista de Monitoreo PPD y Pagos Ausentes (Semáforo v3.2 - Auditoría V2)
DROP VIEW IF EXISTS v_ppd_semaforo_status CASCADE;
CREATE OR REPLACE VIEW v_ppd_semaforo_status AS
SELECT 
    c.uuid,
    c.folio,
    c.total,
    c.rfc_receptor,
    c.entidad_id,
    COALESCE(SUM(r.monto_pagado), 0) as total_pagado,
    c.total - COALESCE(SUM(r.monto_pagado), 0) as saldo_insoluto,
    CASE 
        -- Lógica Quirúrgica: COALESCE(factura_padre.uuid, 'AUSENTE')
        -- En este contexto, si orphan_payment es true, emitimos 'AUSENTE'
        WHEN c.orphan_payment = TRUE THEN 'AUSENTE'
        WHEN COALESCE(SUM(r.monto_pagado), 0) <= 0 THEN 'PENDIENTE'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) > 0 THEN 'PARCIAL'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) <= 0 THEN 'PAGADO'
        ELSE 'PENDIENTE'
    END as estado_semaforo
FROM comprobantes c
LEFT JOIN cfdi_relacionados r ON c.uuid = r.uuid_relacionado::UUID
WHERE (c.metodo_pago = 'PPD' AND c.tipo_comprobante = 'I')
   OR (c.tipo_comprobante = 'P') -- Incluimos todos los pagos para detectar Ausencia
GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id;
