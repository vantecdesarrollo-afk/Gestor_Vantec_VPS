-- init_schema.sql
-- DDL para el Gestor CFDI Vantec
-- Generado para instalación limpia en PostgreSQL

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TABLA: tenants
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfc VARCHAR(13) UNIQUE NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    logo_path VARCHAR(500),
    base_repository_path VARCHAR(1000),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABLA: users
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superadmin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP
);

-- 3. TABLA: comprobantes (Principal v4.0)
CREATE TABLE comprobantes (
    uuid UUID PRIMARY KEY,
    entidad_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    serie VARCHAR(25),
    folio VARCHAR(25),
    fecha_emision TIMESTAMP,
    rfc_emisor VARCHAR(13),
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13),
    nombre_receptor VARCHAR(255),
    tipo_comprobante VARCHAR(1), -- I, E, P, N, T
    moneda VARCHAR(3),
    total NUMERIC(18, 6),
    estatus_sat VARCHAR(20),
    ruta_resguardo VARCHAR(500),
    metodo_pago VARCHAR(10),
    forma_pago VARCHAR(2),
    version VARCHAR(10),
    ingestado_at TIMESTAMP,
    status VARCHAR(50),
    tipo_cambio NUMERIC(18, 6),
    descuento NUMERIC(18, 6),
    total_impuestos_trasladados NUMERIC(18, 6),
    total_impuestos_retenidos NUMERIC(18, 6),
    subtotal NUMERIC(18, 6),
    xml_path VARCHAR(1000),
    pdf_path VARCHAR(1000)
);

-- 4. TABLA: cfdi_relacionados
CREATE TABLE cfdi_relacionados (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID REFERENCES comprobantes(uuid) ON DELETE CASCADE,
    uuid_padre VARCHAR(36) NOT NULL,
    uuid_relacionado VARCHAR(36) NOT NULL,
    tipo_relacion VARCHAR(10),
    monto_pagado NUMERIC(18, 6),
    saldo_insoluto NUMERIC(18, 6),
    num_parcialidad INTEGER
);

-- 5. TABLA: cfdis (Bóveda Histórica)
CREATE TABLE cfdis (
    cfdi_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    uuid VARCHAR(36) NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    rfc_receptor VARCHAR(13) NOT NULL,
    issue_date TIMESTAMP NOT NULL,
    total NUMERIC(18, 6) NOT NULL,
    version VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'VALID',
    xml_file_path VARCHAR(1000) NOT NULL,
    pdf_file_path VARCHAR(1000),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_cfdis_uuid ON cfdis(uuid);

-- 6. TABLA: cfdi_conceptos
CREATE TABLE cfdi_conceptos (
    id SERIAL PRIMARY KEY,
    cfdi_id UUID NOT NULL REFERENCES cfdis(cfdi_id) ON DELETE CASCADE,
    clave_prod_serv VARCHAR(20),
    cantidad NUMERIC(15, 6),
    clave_unitario VARCHAR(10),
    descripcion TEXT,
    valor_unitario NUMERIC(15, 6),
    importe NUMERIC(15, 6)
);

-- 7. TABLA: entidad_smtp_configs
CREATE TABLE entidad_smtp_configs (
    id SERIAL PRIMARY KEY,
    entidad_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    host VARCHAR(255),
    port INTEGER,
    username VARCHAR(255),
    password_encrypted VARCHAR(500),
    from_address VARCHAR(255),
    security_type VARCHAR(50),
    authentication_type VARCHAR(50)
);

-- 8. TABLA: usuario_entidad_acceso (Roles)
CREATE TABLE usuario_entidad_acceso (
    usuario_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    entidad_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    rol VARCHAR(50) NOT NULL, -- 'ADMIN', 'OPERADOR', 'VISOR'
    PRIMARY KEY (usuario_id, entidad_id)
);

-- 9. TABLA: dash_cfdi_documents (Optimización Dashboard)
CREATE TABLE dash_cfdi_documents (
    cfdi_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    uuid_fiscal VARCHAR(36) UNIQUE NOT NULL,
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    tipo_comprobante CHAR(1) NOT NULL,
    moneda VARCHAR(10) DEFAULT 'MXN',
    tipo_cambio NUMERIC(18, 6) DEFAULT 1.0,
    subtotal NUMERIC(18, 6) NOT NULL,
    total NUMERIC(18, 6) NOT NULL,
    metodo_pago VARCHAR(5),
    forma_pago VARCHAR(5),
    estatus_sat VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. TABLA: dash_cfdi_concepts
CREATE TABLE dash_cfdi_concepts (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cfdi_id UUID REFERENCES dash_cfdi_documents(cfdi_id) ON DELETE CASCADE,
    clave_prod_serv VARCHAR(20) NOT NULL,
    no_identificacion VARCHAR(100),
    clave_unidad VARCHAR(5) NOT NULL,
    cantidad NUMERIC(18, 6) NOT NULL,
    descripcion TEXT NOT NULL,
    valor_unitario NUMERIC(18, 6) NOT NULL,
    importe NUMERIC(18, 6) NOT NULL
);

CREATE TABLE cfdi_quarantine (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    rfc_emisor VARCHAR(20),
    rfc_receptor VARCHAR(20),
    xml_path VARCHAR(500),
    pdf_path VARCHAR(500),
    motivo_rechazo VARCHAR(255) DEFAULT 'Vulnerabilidad prevenida: RFC Emisor no registrado',
    fecha_deteccion TIMESTAMPTZ DEFAULT NOW()
);

-- 12. TABLA: auth_recovery_tokens (L6 v3.5)
CREATE TABLE auth_recovery_tokens (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);
