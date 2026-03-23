CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================================
-- ESTRUCTURA OPTIMIZADA PARA RENDIMIENTO DE DASHBOARD (FILTROS DE CONCEPTOS)
-- ==============================================================================

-- 1. Vista/Tabla Materializada o Tabla Física Sincronizada para el Listado Principal
-- Esta tabla unifica lo esencial de 'comprobantes' y 'cfdis' pero con índices duros.
CREATE TABLE dash_cfdi_documents (
    cfdi_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    uuid_fiscal VARCHAR(36) UNIQUE NOT NULL, 
    
    -- Datos de Encabezado (Para el Grid)
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    
    -- Datos Comerciales (Filtros del Dashboard)
    tipo_comprobante CHAR(1) NOT NULL,
    moneda VARCHAR(10) NOT NULL DEFAULT 'MXN', 
    tipo_cambio NUMERIC(18,6) DEFAULT 1.0,
    subtotal NUMERIC(18,6) NOT NULL,
    total NUMERIC(18,6) NOT NULL,
    metodo_pago VARCHAR(5), 
    forma_pago VARCHAR(5),
    
    -- Control de Estado
    estatus_sat VARCHAR(20), 
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices críticos para que los filtros del front no colapsen
CREATE INDEX idx_dash_cfdi_fecha ON dash_cfdi_documents(fecha_emision);
CREATE INDEX idx_dash_cfdi_moneda ON dash_cfdi_documents(moneda);
CREATE INDEX idx_dash_cfdi_tenant ON dash_cfdi_documents(tenant_id);

-- 2. Tabla de Conceptos (FÍSICA Y RELACIONAL, NO JSONB)
-- El Dashboard filtrará directamente contra esta tabla y hará un JOIN rápido
CREATE TABLE dash_cfdi_concepts (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cfdi_id UUID REFERENCES dash_cfdi_documents(cfdi_id) ON DELETE CASCADE,
    
    -- Claves para filtrado analítico
    clave_prod_serv VARCHAR(20) NOT NULL, 
    no_identificacion VARCHAR(100),
    clave_unidad VARCHAR(5) NOT NULL,
    
    -- Datos descriptivos y montos
    cantidad NUMERIC(18,6) NOT NULL,
    descripcion TEXT NOT NULL,
    valor_unitario NUMERIC(18,6) NOT NULL,
    importe NUMERIC(18,6) NOT NULL
);

-- Índices para búsqueda ultrarrápida de conceptos desde el Dashboard
CREATE INDEX idx_dash_concepts_clave ON dash_cfdi_concepts(clave_prod_serv);
CREATE INDEX idx_dash_concepts_cfdi_id ON dash_cfdi_concepts(cfdi_id);
