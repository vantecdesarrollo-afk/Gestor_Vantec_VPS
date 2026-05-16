-- =================================================================================
-- AUDITORÍA DE ESTRUCTURA - PROTOCOLO L6 (VCORE)
-- Proyecto: Gestor CFDI Vantec
-- Fecha: 2026-04-02
-- Objetivo: Validación de arquitectura para Cálculo Dinámico de Saldo (Fases 1, 2, 3)
-- =================================================================================

-- 1. TABLA PRINCIPAL: COMPROBANTES (SSoT)
CREATE TABLE comprobantes (
    uuid UUID PRIMARY KEY,                   -- PK Unívoca (SSoT)
    entidad_id UUID NOT NULL,               -- FK a Tenants (Aislamiento Multi-tenant)
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    tipo_comprobante CHAR(1) NOT NULL,       -- I (Ingreso), E (Egreso), P (Pago), N (Nómina)
    moneda VARCHAR(10) DEFAULT 'MXN',
    subtotal DECIMAL(18, 6) NOT NULL,
    total DECIMAL(18, 6) NOT NULL,
    metodo_pago VARCHAR(10),                 -- PPD / PUE
    forma_pago VARCHAR(5),
    estatus_sat VARCHAR(20),                 -- Vigente / Cancelado
    version VARCHAR(10),                     -- 3.3 / 4.0
    xml_path TEXT NOT NULL,                  -- Localización física del XML
    pdf_path TEXT,                           -- Localización física del PDF
    orphan_payment BOOLEAN DEFAULT FALSE,    -- Flag para REPs sin factura (Detección L6)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comprobante_tenant 
        FOREIGN KEY (entidad_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);

-- 2. TABLA DE RELACIONES: CFDI_RELACIONADOS (N:M)
-- Soporta tanto Complementos de Pago (Pago 2.0) como Notas de Crédito (TipoRelacion)
CREATE TABLE cfdi_relacionados (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID NOT NULL,                  -- El documento que DECLARA la relación (ej: el REP o la NC)
    uuid_padre VARCHAR(36) NOT NULL,        -- UUID del documento actual (desnormalizado para consultas rápidas)
    uuid_relacionado VARCHAR(36) NOT NULL,  -- El UUID al que se afecta (Factura PPD original)
    tipo_relacion VARCHAR(10),              -- 01, 04, PAGO, etc.
    monto_pagado DECIMAL(18, 6),            -- ImpPagado (VCore Engine)
    num_parcialidad INTEGER,                -- Número de parcialidad actual
    saldo_anterior DECIMAL(18, 6),          -- ImpSaldoAnt
    saldo_insoluto DECIMAL(18, 6),          -- ImpSaldoInsoluto (Cálculo Dinámico)
    CONSTRAINT fk_relacion_cfdi 
        FOREIGN KEY (cfdi_id) REFERENCES comprobantes(uuid) ON DELETE CASCADE
);

-- 3. TABLA DE CONCEPTOS: CFDI_CONCEPTOS
-- Almacena el detalle atómico de cada factura (Útil para auditoría de NC por concepto)
CREATE TABLE cfdi_conceptos (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID NOT NULL,
    clave_prod_serv VARCHAR(20),
    cantidad DECIMAL(15, 6),
    descripcion TEXT,
    valor_unitario DECIMAL(15, 6),
    importe DECIMAL(15, 6),
    CONSTRAINT fk_concepto_cfdi 
        FOREIGN KEY (cfdi_id) REFERENCES comprobantes(uuid) ON DELETE CASCADE
);

-- 4. TABLA DE ANOMALÍAS: FINANCIAL_ANOMALIES_LOGS
-- Control de integridad para detección de duplicados y pagos huérfanos
CREATE TABLE financial_anomalies_logs (
    id SERIAL PRIMARY KEY,
    entidad_id UUID NOT NULL,
    uuid_documento UUID NOT NULL,
    tipo_anomalia VARCHAR(50) NOT NULL,      -- 'PAGO_HUERFANO', 'DUPLICADO', 'GHOST_RECOVERY'
    detalle TEXT,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estatus_anomalia VARCHAR(20) DEFAULT 'ACTIVA',
    CONSTRAINT fk_anomaly_tenant 
        FOREIGN KEY (entidad_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);
