-- ==================================================================
-- DUMP DE ESTRUCTURA (DDL): CFDI, EMISIÓN, CONCEPTOS, MONEDAS
-- ==================================================================

-- TABLA: CFDIS
CREATE TABLE cfdis (
    cfdi_id uuid NOT NULL  PRIMARY KEY,
    tenant_id uuid NOT NULL,
    uuid VARCHAR(36) NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    rfc_receptor VARCHAR(13) NOT NULL,
    issue_date timestamp with time zone NOT NULL,
    total NUMERIC NOT NULL,
    version VARCHAR(10) NOT NULL,
    status VARCHAR(50),
    xml_file_path VARCHAR(1000) NOT NULL,
    pdf_file_path VARCHAR(1000),
    created_at timestamp with time zone  DEFAULT now(),
    source_type VARCHAR(50)  DEFAULT 'UPLOAD_MANUAL'::character varying,
    tipo_comprobante character,
    serie VARCHAR(25),
    folio VARCHAR(40),
    metadata_xml jsonb,
    metodo_pago VARCHAR(5),
    forma_pago VARCHAR(5),
    parent_uuid VARCHAR(36)
);

-- NOTA DE CONCEPTOS EN CFDIS:
-- Los conceptos no tienen tabla dedicada. Se asume que se procesan del XML en `metadata_xml` (jsonb).


-- TABLA: COMPROBANTES
CREATE TABLE comprobantes (
    uuid uuid NOT NULL  PRIMARY KEY,
    serie VARCHAR(20),
    folio VARCHAR(50),
    rfc_emisor VARCHAR(13),
    rfc_receptor VARCHAR(13),
    version VARCHAR(5),
    total NUMERIC,
    ruta_resguardo text,
    fecha_emision timestamp without time zone,
    ingestado_at timestamp without time zone,
    entidad_id uuid,
    tipo_comprobante character varying,
    metodo_pago character varying,
    forma_pago character varying,
    status character varying  DEFAULT 'VALID'::character varying,
    moneda VARCHAR(10)  DEFAULT 'MXN'::character varying,
    tipo_cambio NUMERIC,
    descuento NUMERIC,
    total_impuestos_trasladados NUMERIC,
    total_impuestos_retenidos NUMERIC,
    subtotal NUMERIC  DEFAULT 0,
    nombre_emisor VARCHAR(255),
    nombre_receptor VARCHAR(255),
    estatus_sat VARCHAR(20)
);

-- NOTA DE CONCEPTOS EN COMPROBANTES:
-- Esta tabla posee `moneda` y `tipo_cambio` para el listado básico.


-- TABLA: CFDI_RELACIONADOS
CREATE TABLE cfdi_relacionados (
    id integer NOT NULL DEFAULT nextval('cfdi_relacionados_id_seq'::regclass) PRIMARY KEY,
    cfdi_id uuid NOT NULL,
    uuid_padre VARCHAR(36) NOT NULL,
    uuid_relacionado VARCHAR(36) NOT NULL,
    tipo_relacion VARCHAR(10),
    monto_pagado NUMERIC,
    saldo_insoluto NUMERIC,
    num_parcialidad integer
);

-- NOTA DE CONCEPTOS EN CFDI_RELACIONADOS:

-- TABLA: CFDI_METADATA
CREATE TABLE cfdi_metadata (
    uuid VARCHAR(36) NOT NULL  PRIMARY KEY,
    tenant_id uuid NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    rfc_receptor VARCHAR(13) NOT NULL,
    fecha_emision timestamp with time zone NOT NULL,
    tipo_comprobante VARCHAR(1) NOT NULL,
    total NUMERIC NOT NULL,
    estado VARCHAR(20),
    tiene_pdf boolean,
    fecha_registro timestamp with time zone  DEFAULT now()
);

-- NOTA DE CONCEPTOS EN CFDI_METADATA:

