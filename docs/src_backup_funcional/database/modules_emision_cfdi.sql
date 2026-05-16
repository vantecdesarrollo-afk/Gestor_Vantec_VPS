-- ==============================================================================
-- SCRIPT MAESTRO #2: MÓDULO DE EMISIÓN, CFDI Y DASHBOARD (PostgreSQL)
-- Objetivo: Reparar los filtros de Moneda/Conceptos y el grid de Emisión
-- ==============================================================================

-- 1. Tabla Principal de CFDI (Basado en el legado, optimizado para el Dashboard)
CREATE TABLE cfdi_documents (
    cfdi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id INT REFERENCES cat_entities(entity_id) ON DELETE CASCADE, -- Liga con la entidad dueña
    uuid_fiscal VARCHAR(36) UNIQUE NOT NULL, -- UUID del SAT
    
    -- Datos de Encabezado (Para el Grid de Emisión)
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision TIMESTAMP NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    
    -- Datos Comerciales (¡AQUÍ ESTÁN LOS FILTROS DEL DASHBOARD!)
    tipo_comprobante CHAR(1) NOT NULL, -- I, E, T, P, N
    moneda VARCHAR(3) NOT NULL DEFAULT 'MXN', -- Filtro de Moneda resuelto
    tipo_cambio DECIMAL(18,6) DEFAULT 1.0,
    subtotal DECIMAL(18,6) NOT NULL,
    total DECIMAL(18,6) NOT NULL,
    metodo_pago VARCHAR(3), -- PUE, PPD
    forma_pago VARCHAR(2),
    
    -- Control de Estado de Operación
    estatus VARCHAR(20) DEFAULT 'PROCESADO', -- PROCESADO, ERROR, CANCELADO
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices críticos: Esto es lo que evitará que el Dashboard colapse al filtrar
CREATE INDEX idx_cfdi_fecha ON cfdi_documents(fecha_emision);
CREATE INDEX idx_cfdi_moneda ON cfdi_documents(moneda);
CREATE INDEX idx_cfdi_rfc_rec ON cfdi_documents(rfc_receptor);
CREATE INDEX idx_cfdi_entidad ON cfdi_documents(entity_id);

-- 2. Tabla de Conceptos (Normalizada)
-- Al separar los conceptos, el Dashboard puede filtrar productos sin romper la consulta principal
CREATE TABLE cfdi_concepts (
    concept_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cfdi_id UUID REFERENCES cfdi_documents(cfdi_id) ON DELETE CASCADE,
    
    clave_prod_serv VARCHAR(20) NOT NULL, -- Filtro de Conceptos del Dashboard
    no_identificacion VARCHAR(100),
    cantidad DECIMAL(18,6) NOT NULL,
    clave_unidad VARCHAR(5) NOT NULL,
    descripcion TEXT NOT NULL,
    valor_unitario DECIMAL(18,6) NOT NULL,
    importe DECIMAL(18,6) NOT NULL
);

-- Índices para búsqueda ultrarrápida de conceptos
CREATE INDEX idx_cfdi_concepts_clave ON cfdi_concepts(clave_prod_serv);
CREATE INDEX idx_cfdi_concepts_cfdi_id ON cfdi_concepts(cfdi_id);
