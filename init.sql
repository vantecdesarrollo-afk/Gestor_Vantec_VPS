-- ==================================================================
-- DUMP DE ESTRUCTURA COMPLETA (DDL): GESTOR CFDI ON-PREMISE
-- ==================================================================

-- TABLA: USERS
CREATE TABLE IF NOT EXISTS users (
    user_id uuid NOT NULL  PRIMARY KEY,
    tenant_id uuid NOT NULL,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    auth_provider VARCHAR(50),
    ldap_dn VARCHAR(255),
    is_active boolean,
    last_login timestamp with time zone,
    created_at timestamp with time zone  DEFAULT now(),
    is_superadmin boolean  DEFAULT false
);

-- TABLA: CFDI_METADATA
CREATE TABLE IF NOT EXISTS cfdi_metadata (
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

-- TABLA: TENANTS
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id uuid NOT NULL  PRIMARY KEY,
    rfc VARCHAR(13) NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    logo_path VARCHAR(500),
    is_active boolean,
    created_at timestamp with time zone  DEFAULT now()
);

-- TABLA: BITACORA_AUDITORIA
CREATE TABLE IF NOT EXISTS bitacora_auditoria (
    id integer NOT NULL DEFAULT nextval('bitacora_auditoria_id_seq'::regclass) PRIMARY KEY,
    usuario_id uuid,
    entidad_id uuid,
    accion VARCHAR(100) NOT NULL,
    detalle jsonb,
    fecha_hora timestamp with time zone  DEFAULT now()
);

-- TABLA: USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id uuid NOT NULL  PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),
    auth_provider VARCHAR(50),
    is_active boolean,
    created_at timestamp with time zone  DEFAULT now(),
    is_superadmin boolean  DEFAULT false,
    last_login timestamp with time zone
);

-- TABLA: DASH_CFDI_CONCEPTS
CREATE TABLE IF NOT EXISTS dash_cfdi_concepts (
    concept_id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    cfdi_id uuid,
    clave_prod_serv VARCHAR(20) NOT NULL,
    no_identificacion VARCHAR(100),
    clave_unidad VARCHAR(5) NOT NULL,
    cantidad NUMERIC NOT NULL,
    descripcion text NOT NULL,
    valor_unitario NUMERIC NOT NULL,
    importe NUMERIC NOT NULL
);

-- TABLA: DASH_CFDI_DOCUMENTS
CREATE TABLE IF NOT EXISTS dash_cfdi_documents (
    cfdi_id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    tenant_id uuid,
    uuid_fiscal VARCHAR(36) NOT NULL,
    serie VARCHAR(25),
    folio VARCHAR(40),
    fecha_emision timestamp without time zone NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    nombre_emisor VARCHAR(255),
    rfc_receptor VARCHAR(13) NOT NULL,
    nombre_receptor VARCHAR(255),
    tipo_comprobante character NOT NULL,
    moneda VARCHAR(10) NOT NULL DEFAULT 'MXN'::character varying,
    tipo_cambio NUMERIC  DEFAULT 1.0,
    subtotal NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    metodo_pago VARCHAR(5),
    forma_pago VARCHAR(5),
    estatus_sat VARCHAR(20),
    created_at timestamp without time zone  DEFAULT now()
);

-- TABLA: CFDIS
CREATE TABLE IF NOT EXISTS cfdis (
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

-- TABLA: ENTIDADES_FISCALES
CREATE TABLE IF NOT EXISTS entidades_fiscales (
    id uuid NOT NULL  PRIMARY KEY,
    rfc VARCHAR(13) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    is_active boolean,
    created_at timestamp with time zone  DEFAULT now(),
    logo_url VARCHAR(500)
);

-- TABLA: EMAIL_QUEUE
CREATE TABLE IF NOT EXISTS email_queue (
    id integer NOT NULL DEFAULT nextval('email_queue_id_seq'::regclass) PRIMARY KEY,
    entidad_id uuid NOT NULL,
    cfdi_uuid VARCHAR(36) NOT NULL,
    destinatario VARCHAR(255) NOT NULL,
    estado VARCHAR(20),
    intentos integer,
    proximo_intento timestamp with time zone,
    created_at timestamp with time zone  DEFAULT now()
);

-- TABLA: EMAIL_LOGS
CREATE TABLE IF NOT EXISTS email_logs (
    id integer NOT NULL DEFAULT nextval('email_logs_id_seq'::regclass) PRIMARY KEY,
    email_queue_id integer NOT NULL,
    respuesta_smtp text,
    fecha_intento timestamp with time zone  DEFAULT now()
);

-- TABLA: ENTIDAD_SMTP_CONFIGS
CREATE TABLE IF NOT EXISTS entidad_smtp_configs (
    id integer NOT NULL DEFAULT nextval('entidad_smtp_configs_id_seq'::regclass) PRIMARY KEY,
    entidad_id uuid NOT NULL,
    hostname VARCHAR(255),
    port integer NOT NULL,
    username VARCHAR(255) NOT NULL,
    password_encrypted text NOT NULL,
    _use_tls_deprecated boolean,
    created_at timestamp with time zone  DEFAULT now(),
    from_address VARCHAR(255),
    security_type VARCHAR(50)  DEFAULT 'STARTTLS'::character varying,
    authentication_type VARCHAR(50)  DEFAULT 'LOGIN'::character varying,
    host VARCHAR(255)
);

-- TABLA: TENANT_STORAGE_CONFIGS
CREATE TABLE IF NOT EXISTS tenant_storage_configs (
    id integer NOT NULL DEFAULT nextval('tenant_storage_configs_id_seq'::regclass) PRIMARY KEY,
    tenant_id uuid NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    base_path VARCHAR(500) NOT NULL
);

-- TABLA: COMPROBANTES
CREATE TABLE IF NOT EXISTS comprobantes (
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

-- TABLA: CFDI_RELACIONADOS
CREATE TABLE IF NOT EXISTS cfdi_relacionados (
    id integer NOT NULL DEFAULT nextval('cfdi_relacionados_id_seq'::regclass) PRIMARY KEY,
    cfdi_id uuid NOT NULL,
    uuid_padre VARCHAR(36) NOT NULL,
    uuid_relacionado VARCHAR(36) NOT NULL,
    tipo_relacion VARCHAR(10),
    monto_pagado NUMERIC,
    saldo_insoluto NUMERIC,
    num_parcialidad integer
);

-- TABLA: ENTIDAD_STORAGE_CONFIGS
CREATE TABLE IF NOT EXISTS entidad_storage_configs (
    id integer NOT NULL DEFAULT nextval('entidad_storage_configs_id_seq'::regclass) PRIMARY KEY,
    entidad_id uuid NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    base_path VARCHAR(500) NOT NULL
);

-- TABLA: USUARIO_ENTIDAD_ACCESO
CREATE TABLE IF NOT EXISTS usuario_entidad_acceso (
    usuario_id uuid NOT NULL,
    entidad_id uuid NOT NULL,
    rol VARCHAR(50) NOT NULL,
    fecha_asignacion timestamp with time zone  DEFAULT now(),
        CONSTRAINT usuario_entidad_acceso_pkey PRIMARY KEY (usuario_id, entidad_id)
);

-- TABLA: PLANTILLAS_CORREO
CREATE TABLE IF NOT EXISTS plantillas_correo (
    id integer NOT NULL DEFAULT nextval('plantillas_correo_id_seq'::regclass) PRIMARY KEY,
    entidad_id uuid,
    tipo_plantilla VARCHAR(50) NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    cuerpo_html text NOT NULL,
    created_at timestamp with time zone  DEFAULT now()
);

-- ==================================================================
-- DATOS POR DEFECTO PARA PRIMER INICIO
-- ==================================================================
INSERT INTO users (user_id, username, password_hash, is_active, is_superadmin, tenant_id) VALUES
('00000000-0000-0000-0000-000000000001', 'admin', 'pbkdf2:sha256:600000$p4O2X8uPzH87ZgR5$e8f7762696fe08cfa361664bfeb83c8d195f1fa02f690f7797825b07fb88cfeb', true, true, '00000000-0000-0000-0000-000000000001')
ON CONFLICT (username) DO NOTHING;

INSERT INTO tenants (tenant_id, rfc, business_name, is_active) VALUES
('00000000-0000-0000-0000-000000000001', 'XAXX010101000', 'Empresa Demo S.A.', true)
ON CONFLICT (rfc) DO NOTHING;
