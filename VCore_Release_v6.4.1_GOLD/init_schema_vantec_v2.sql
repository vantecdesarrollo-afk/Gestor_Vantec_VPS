-- init_schema_vantec_v2.sql (SSoT Consolidado)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TENANTS & USERS & SMTP (Catálogos Base)
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfc VARCHAR(13) UNIQUE NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    base_repository_path VARCHAR(1000),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'VISOR', -- ADMIN, OPERADOR, VISOR
    is_active BOOLEAN DEFAULT TRUE,
    is_superadmin BOOLEAN DEFAULT FALSE
);

CREATE TABLE entidad_smtp_configs (
    id SERIAL PRIMARY KEY,
    entidad_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    host VARCHAR(255),
    port INTEGER,
    username VARCHAR(255),
    password_encrypted VARCHAR(500),
    from_address VARCHAR(255)
);

-- 2. COMPROBANTES (SSoT ÚNICO - Reemplaza a cfdis y dash_cfdi_documents)
CREATE TABLE comprobantes (
    uuid UUID PRIMARY KEY,
    entidad_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    tipo_comprobante VARCHAR(1) NOT NULL,
    moneda VARCHAR(10) DEFAULT 'MXN',
    subtotal NUMERIC(18, 6) NOT NULL,
    total NUMERIC(18, 6) NOT NULL,
    metodo_pago VARCHAR(10),
    forma_pago VARCHAR(5),
    estatus_sat VARCHAR(20),
    version VARCHAR(10),
    xml_path VARCHAR(1000) NOT NULL,
    pdf_path VARCHAR(1000),
    orphan_payment BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_comprobantes_fecha ON comprobantes(fecha_emision);
CREATE INDEX idx_comprobantes_rfc ON comprobantes(rfc_emisor, rfc_receptor);

-- 3. CFDI RELACIONADOS Y CONCEPTOS
CREATE TABLE cfdi_relacionados (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID REFERENCES comprobantes(uuid) ON DELETE CASCADE,
    uuid_padre VARCHAR(36) NOT NULL,
    uuid_relacionado VARCHAR(36) NOT NULL,
    tipo_relacion VARCHAR(10),
    monto_pagado NUMERIC(18, 6),
    num_parcialidad INTEGER,
    saldo_anterior NUMERIC(18, 6),
    saldo_insoluto NUMERIC(18, 6)
);

CREATE TABLE cfdi_conceptos (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID NOT NULL REFERENCES comprobantes(uuid) ON DELETE CASCADE,
    clave_prod_serv VARCHAR(20),
    cantidad NUMERIC(15, 6),
    descripcion TEXT,
    valor_unitario NUMERIC(15, 6),
    importe NUMERIC(15, 6)
);
