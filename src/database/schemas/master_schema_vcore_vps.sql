-- ==============================================================================
-- VANTEC VCORE L6 - MASTER SCHEMA (ULTRA-GOLD v6.4.0)
-- ESTRUCTURA COMPLETA: 19 TABLAS SINCRONIZADAS CON DUMP FORENSE + ADN VPS
-- ==============================================================================

-- 1. PREPARACIÓN DE ENTORNO Y SEGURIDAD
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS plpgsql;

-- 2. BLOQUE MAESTRO: ENTIDADES Y USUARIOS (SSOT)
CREATE TABLE IF NOT EXISTS public.tenants (
    tenant_id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfc character varying(13) NOT NULL UNIQUE,
    business_name character varying(200) NOT NULL,
    api_key character varying(255) UNIQUE, -- [VPS Hardening] Inyectado para autenticación de Agente
    base_repository_path character varying(1000),
    logo_path character varying(500),
    is_active boolean DEFAULT true
);

CREATE TABLE IF NOT EXISTS public.users (
    user_id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id uuid REFERENCES public.tenants(tenant_id) ON DELETE SET NULL,
    username character varying(100) NOT NULL UNIQUE,
    password_hash character varying(255) NOT NULL,
    email character varying(150),
    is_active boolean DEFAULT true,
    is_superadmin boolean DEFAULT false,
    rol character varying(20) DEFAULT 'VISOR'
);

CREATE TABLE IF NOT EXISTS public.usuario_entidad_acceso (
    usuario_id uuid NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    entidad_id uuid NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    rol character varying(50) NOT NULL,
    PRIMARY KEY (usuario_id, entidad_id)
);

CREATE TABLE IF NOT EXISTS public.auth_recovery_tokens (
    id SERIAL PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    token character varying(255) NOT NULL UNIQUE,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean DEFAULT false
);

-- 3. MOTOR DE COMPROBANTES Y ADN FISCAL
CREATE TABLE IF NOT EXISTS public.comprobantes (
    uuid uuid NOT NULL PRIMARY KEY,
    entidad_id uuid NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    md5_hash character varying(32), -- [VPS Hardening] Inyectado para Idempotencia
    serie character varying(25),
    folio character varying(40),
    fecha_emision timestamp without time zone NOT NULL,
    rfc_emisor character varying(13) NOT NULL,
    nombre_emisor character varying(255),
    rfc_receptor character varying(13) NOT NULL,
    nombre_receptor character varying(255),
    tipo_comprobante character varying(1) NOT NULL,
    moneda character varying(10) DEFAULT 'MXN',
    subtotal numeric(18,6) NOT NULL,
    total numeric(18,6) NOT NULL,
    metodo_pago character varying(10),
    forma_pago character varying(5),
    estatus_sat character varying(20),
    version character varying(10),
    xml_path character varying(1000) NOT NULL,
    pdf_path TEXT, -- [VPS Hardening] TEXT para soporte Multi-PDF con pipes infinitos
    orphan_payment boolean DEFAULT false,
    regimen_fiscal_receptor character varying(100),
    domicilio_fiscal_receptor character varying(5),
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.cfdi_relacionados (
    id SERIAL PRIMARY KEY,
    cfdi_id uuid REFERENCES public.comprobantes(uuid) ON DELETE CASCADE,
    uuid_padre character varying(36) NOT NULL,
    uuid_relacionado character varying(36) NOT NULL,
    tipo_relacion character varying(10),
    monto_pagado numeric(18,6),
    num_parcialidad integer,
    saldo_anterior numeric(18,6),
    saldo_insoluto numeric(18,6)
);

CREATE TABLE IF NOT EXISTS public.cfdi_conceptos (
    id SERIAL PRIMARY KEY,
    cfdi_id uuid NOT NULL REFERENCES public.comprobantes(uuid) ON DELETE CASCADE,
    clave_prod_serv character varying(20),
    cantidad numeric(15,6),
    descripcion text,
    valor_unitario numeric(15,6),
    importe numeric(15,6)
);

CREATE TABLE IF NOT EXISTS public.cfdi_aplicaciones_manuales (
    id SERIAL PRIMARY KEY,
    entidad_id uuid NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    uuid_origen uuid NOT NULL,
    uuid_destino uuid NOT NULL,
    monto_aplicado numeric(18,6) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT now(),
    folio_origen character varying(40),
    folio_destino character varying(40)
);

-- 4. SUBSISTEMA DE COMUNICACIÓN (EMAIL ENGINE)
CREATE TABLE IF NOT EXISTS public.entidad_smtp_configs (
    id SERIAL PRIMARY KEY,
    entidad_id uuid REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    host character varying(255),
    port integer,
    username character varying(255),
    password_encrypted character varying(500),
    from_address character varying(255),
    security_type character varying(50) DEFAULT 'STARTTLS',
    authentication_type character varying(50) DEFAULT 'LOGIN'
);

CREATE TABLE IF NOT EXISTS public.email_queue (
    id SERIAL PRIMARY KEY,
    entidad_id uuid NOT NULL REFERENCES public.tenants(tenant_id),
    cfdi_uuid character varying(36) NOT NULL,
    destinatario character varying(255) NOT NULL,
    estado character varying(20) DEFAULT 'PENDIENTE',
    intentos integer DEFAULT 0,
    proximo_intento timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.email_logs (
    id SERIAL PRIMARY KEY,
    email_queue_id integer NOT NULL REFERENCES public.email_queue(id) ON DELETE CASCADE,
    respuesta_smtp text,
    fecha_intento timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.plantillas_correo (
    id SERIAL PRIMARY KEY,
    entidad_id uuid REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    tipo_plantilla character varying(50) NOT NULL,
    asunto character varying(255) NOT NULL,
    cuerpo_html text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);

-- 5. SUBSISTEMA DE AUDITORÍA Y SEGREGACIÓN L6
CREATE TABLE IF NOT EXISTS public.bitacora_auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id uuid REFERENCES public.users(user_id) ON DELETE SET NULL,
    entidad_id uuid REFERENCES public.tenants(tenant_id) ON DELETE SET NULL,
    accion character varying(100) NOT NULL,
    detalle jsonb,
    fecha_hora timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.financial_anomalies_logs (
    id SERIAL PRIMARY KEY,
    entidad_id uuid REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    uuid_documento uuid NOT NULL,
    tipo_anomalia character varying(50) NOT NULL,
    detalle text,
    fecha_deteccion timestamp without time zone DEFAULT now(),
    estatus_anomalia character varying(20) DEFAULT 'ACTIVA'
);

CREATE TABLE IF NOT EXISTS public.tenant_storage_configs (
    id SERIAL PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    source_type character varying(50) NOT NULL,
    base_path character varying(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.entidad_storage_configs (
    id SERIAL PRIMARY KEY,
    entidad_id uuid NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    source_type character varying(50) NOT NULL,
    base_path character varying(500) NOT NULL
);

-- 6. TABLAS LEGACY (COMPATIBILIDAD V1.0)
CREATE TABLE IF NOT EXISTS public.entidades_fiscales (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfc character varying(13) NOT NULL UNIQUE,
    razon_social character varying(255) NOT NULL,
    is_active boolean DEFAULT true,
    logo_url character varying(500),
    created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.usuarios (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    username character varying(100) NOT NULL UNIQUE,
    email character varying(255) NOT NULL UNIQUE,
    hashed_password character varying(255),
    auth_provider character varying(50) DEFAULT 'LOCAL',
    is_active boolean DEFAULT true,
    is_superadmin boolean DEFAULT false,
    last_login timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.cfdi_metadata (
    uuid character varying(36) PRIMARY KEY,
    tenant_id uuid NOT NULL,
    rfc_emisor character varying(13) NOT NULL,
    rfc_receptor character varying(13) NOT NULL,
    fecha_emision timestamp with time zone NOT NULL,
    tipo_comprobante character varying(1) NOT NULL,
    total numeric(18,6) NOT NULL,
    estado character varying(20),
    tiene_pdf boolean DEFAULT false,
    fecha_registro timestamp with time zone DEFAULT now()
);

-- 7. VISTAS MATERIALIZADAS E INTELIGENCIA DE NEGOCIO
DROP MATERIALIZED VIEW IF EXISTS v_ppd_semaforo_status CASCADE;
CREATE MATERIALIZED VIEW v_ppd_semaforo_status AS
SELECT 
    c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id, c.fecha_emision,
    COALESCE(SUM(r.monto_pagado), 0) as total_pagado,
    CASE 
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) < 1.00 THEN 0.00 
        ELSE (c.total - COALESCE(SUM(r.monto_pagado), 0)) 
    END as saldo_insoluto,
    CASE 
        WHEN c.orphan_payment = TRUE THEN 'AUSENTE'
        WHEN COALESCE(SUM(r.monto_pagado), 0) <= 0 THEN 'PENDIENTE'
        WHEN (c.total - COALESCE(SUM(r.monto_pagado), 0)) < 1.00 THEN 'PAGADO'
        ELSE 'PARCIAL'
    END as estado_semaforo
FROM comprobantes c
LEFT JOIN cfdi_relacionados r ON c.uuid = r.uuid_relacionado::UUID
WHERE (c.metodo_pago = 'PPD' AND c.tipo_comprobante = 'I')
GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id, c.fecha_emision;

CREATE UNIQUE INDEX IF NOT EXISTS idx_v_ppd_uuid ON v_ppd_semaforo_status(uuid);

-- 8. TRIGGERS: LÓGICA DE AUTOMATIZACIÓN
CREATE OR REPLACE FUNCTION fn_perdon_centavos()
RETURNS TRIGGER AS $$
DECLARE
    v_total_factura NUMERIC(18,6);
    v_pagado_previo NUMERIC(18,6);
    v_diferencia NUMERIC(18,6);
BEGIN
    SELECT total INTO v_total_factura FROM comprobantes WHERE uuid = NEW.uuid_relacionado::UUID;
    SELECT COALESCE(SUM(monto_pagado), 0) INTO v_pagado_previo FROM cfdi_relacionados 
    WHERE uuid_relacionado = NEW.uuid_relacionado AND id IS DISTINCT FROM NEW.id;
    v_diferencia := v_total_factura - (v_pagado_previo + NEW.monto_pagado);
    IF v_diferencia > 0 AND v_diferencia <= 1.00 THEN
        NEW.monto_pagado := NEW.monto_pagado + v_diferencia;
        NEW.saldo_insoluto := 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_perdon_centavos ON cfdi_relacionados;
CREATE TRIGGER tr_perdon_centavos
BEFORE INSERT OR UPDATE ON cfdi_relacionados
FOR EACH ROW EXECUTE FUNCTION fn_perdon_centavos();
