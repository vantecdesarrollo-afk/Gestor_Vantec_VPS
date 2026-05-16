-- 07_VANTEC_CORE_DDL_V3_AUDIT.sql (Revision de CTO)
-- SSoT: Comprobantes + Pagos + Saldos PPD

-- 1. EXTENSIONES
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. COMPROBANTES (Entidad Maestra)
-- La columna 'orphan_payment' es crítica para el cumplimiento L6 (Vantec Ghost Protocol)
CREATE TABLE IF NOT EXISTS comprobantes (
    uuid UUID PRIMARY KEY,
    entidad_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    tipo_comprobante VARCHAR(1) NOT NULL, -- I, E, P, T, N
    moneda VARCHAR(10) DEFAULT 'MXN',
    subtotal NUMERIC(18, 6) NOT NULL,
    total NUMERIC(18, 6) NOT NULL,
    metodo_pago VARCHAR(10), -- PPD o PUE
    forma_pago VARCHAR(5),
    estatus_sat VARCHAR(20) DEFAULT 'Vigente',
    version VARCHAR(10),
    xml_path VARCHAR(1000) NOT NULL,
    pdf_path VARCHAR(1000),
    orphan_payment BOOLEAN DEFAULT FALSE, -- Flag para REPS sin Factura de Ingreso
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id),
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'VISOR', -- REQUISITO CTO V3.1
    is_active BOOLEAN DEFAULT TRUE,
    is_superadmin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. VISTA DE MONITOREO DE EMISIÓN (Semáforo Inteligente)
-- FIX CTO: Manejo de NULL en saldo_insoluto -> PENDIENTE
CREATE OR REPLACE VIEW v_ppd_semaforo_status AS
SELECT 
    c.uuid,
    c.folio,
    c.total,
    COALESCE(SUM(r.monto_pagado), 0) as total_pagado,
    c.total - COALESCE(SUM(r.monto_pagado), 0) as saldo_insoluto,
    CASE 
        WHEN COALESCE(SUM(r.monto_pagado), 0) <= 0 THEN 'PENDIENTE'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) > 0 THEN 'PARCIAL'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) <= 0 THEN 'PAGADO'
        ELSE 'PENDIENTE' -- Caso NULL o Error
    END as estado_semaforo
FROM comprobantes c
LEFT JOIN cfdi_relacionados r ON LOWER(CAST(c.uuid AS TEXT)) = LOWER(r.uuid_relacionado)
WHERE c.metodo_pago = 'PPD' 
  AND c.tipo_comprobante = 'I'
GROUP BY c.uuid, c.folio, c.total;
