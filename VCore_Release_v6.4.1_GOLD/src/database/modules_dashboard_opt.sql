-- Optimización Quirúrgica de Dashboard (Estrategia Cero Riesgo)
-- 1. Conversión de Vista Regular a Materialized para permitir persistencia y refresco
DROP VIEW IF EXISTS v_ppd_semaforo_status CASCADE;

CREATE MATERIALIZED VIEW v_ppd_semaforo_status AS
SELECT 
    c.uuid,
    c.folio,
    c.total,
    c.rfc_receptor,
    c.entidad_id,
    COALESCE(SUM(r.monto_pagado), 0) as total_pagado,
    c.total - COALESCE(SUM(r.monto_pagado), 0) as saldo_insoluto,
    CASE 
        WHEN c.orphan_payment = TRUE THEN 'AUSENTE'
        WHEN COALESCE(SUM(r.monto_pagado), 0) <= 0 THEN 'PENDIENTE'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) > 0 THEN 'PARCIAL'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) <= 0 THEN 'PAGADO'
        ELSE 'PENDIENTE'
    END as estado_semaforo
FROM comprobantes c
LEFT JOIN cfdi_relacionados r ON c.uuid = r.uuid_relacionado::UUID
WHERE (c.metodo_pago = 'PPD' AND c.tipo_comprobante = 'I')
GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id;

-- Índice para acelerar el refresco y la visualización
CREATE UNIQUE INDEX idx_v_ppd_uuid ON v_ppd_semaforo_status(uuid);

-- 2. Función y Trigger para Refresco Automático en Pagos
CREATE OR REPLACE FUNCTION fn_refresh_ppd_dashboard()
RETURNS TRIGGER AS $$
BEGIN
    -- Refresco concurrente para no bloquear lecturas del dashboard
    REFRESH MATERIALIZED VIEW CONCURRENTLY v_ppd_semaforo_status;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_refresh_on_payment ON cfdi_relacionados;
CREATE TRIGGER tr_refresh_on_payment
AFTER INSERT OR UPDATE OR DELETE ON cfdi_relacionados
FOR EACH STATEMENT
EXECUTE FUNCTION fn_refresh_ppd_dashboard();

-- 3. Refresco Inicial
REFRESH MATERIALIZED VIEW v_ppd_semaforo_status;
