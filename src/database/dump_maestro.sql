--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.16
-- Dumped by pg_dump version 9.6.16

-- Started on 2026-04-17 15:28:59

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 12387)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2353 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 2 (class 3079 OID 16978)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 2354 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 232 (class 1255 OID 18783)
-- Name: fn_refresh_dashboard(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_refresh_dashboard() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 
            BEGIN 
                RETURN NEW; 
            END; 
            $$;


--
-- TOC entry 231 (class 1255 OID 18684)
-- Name: fn_refresh_ppd_dashboard(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_refresh_ppd_dashboard() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW CONCURRENTLY v_ppd_semaforo_status;
                RETURN NULL;
            END;
            $$;


--
-- TOC entry 233 (class 1255 OID 18784)
-- Name: fn_refresh_ppd_matview(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_refresh_ppd_matview() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 
            BEGIN 
                RETURN NEW; 
            END; 
            $$;


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 220 (class 1259 OID 18796)
-- Name: auth_recovery_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_recovery_tokens (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean DEFAULT false
);


--
-- TOC entry 219 (class 1259 OID 18794)
-- Name: auth_recovery_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_recovery_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2355 (class 0 OID 0)
-- Dependencies: 219
-- Name: auth_recovery_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_recovery_tokens_id_seq OWNED BY public.auth_recovery_tokens.id;


--
-- TOC entry 198 (class 1259 OID 16739)
-- Name: bitacora_auditoria; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bitacora_auditoria (
    id integer NOT NULL,
    usuario_id uuid,
    entidad_id uuid,
    accion character varying(100) NOT NULL,
    detalle jsonb,
    fecha_hora timestamp with time zone DEFAULT now()
);


--
-- TOC entry 197 (class 1259 OID 16737)
-- Name: bitacora_auditoria_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bitacora_auditoria_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2356 (class 0 OID 0)
-- Dependencies: 197
-- Name: bitacora_auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bitacora_auditoria_id_seq OWNED BY public.bitacora_auditoria.id;


--
-- TOC entry 218 (class 1259 OID 18787)
-- Name: cfdi_aplicaciones_manuales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cfdi_aplicaciones_manuales (
    id integer NOT NULL,
    entidad_id uuid NOT NULL,
    uuid_origen uuid NOT NULL,
    uuid_destino uuid NOT NULL,
    monto_aplicado numeric(18,6) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT now(),
    folio_origen character varying(40),
    folio_destino character varying(40)
);


--
-- TOC entry 217 (class 1259 OID 18785)
-- Name: cfdi_aplicaciones_manuales_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cfdi_aplicaciones_manuales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2357 (class 0 OID 0)
-- Dependencies: 217
-- Name: cfdi_aplicaciones_manuales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cfdi_aplicaciones_manuales_id_seq OWNED BY public.cfdi_aplicaciones_manuales.id;


--
-- TOC entry 211 (class 1259 OID 18507)
-- Name: cfdi_conceptos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cfdi_conceptos (
    id integer NOT NULL,
    cfdi_id uuid NOT NULL,
    clave_prod_serv character varying(20),
    cantidad numeric(15,6),
    descripcion text,
    valor_unitario numeric(15,6),
    importe numeric(15,6)
);


--
-- TOC entry 210 (class 1259 OID 18505)
-- Name: cfdi_conceptos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cfdi_conceptos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2358 (class 0 OID 0)
-- Dependencies: 210
-- Name: cfdi_conceptos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cfdi_conceptos_id_seq OWNED BY public.cfdi_conceptos.id;


--
-- TOC entry 188 (class 1259 OID 16559)
-- Name: cfdi_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cfdi_metadata (
    uuid character varying(36) NOT NULL,
    tenant_id uuid NOT NULL,
    rfc_emisor character varying(13) NOT NULL,
    rfc_receptor character varying(13) NOT NULL,
    fecha_emision timestamp with time zone NOT NULL,
    tipo_comprobante character varying(1) NOT NULL,
    total numeric(18,6) NOT NULL,
    estado character varying(20),
    tiene_pdf boolean,
    fecha_registro timestamp with time zone DEFAULT now()
);


--
-- TOC entry 209 (class 1259 OID 18494)
-- Name: cfdi_relacionados; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cfdi_relacionados (
    id integer NOT NULL,
    cfdi_id uuid,
    uuid_padre character varying(36) NOT NULL,
    uuid_relacionado character varying(36) NOT NULL,
    tipo_relacion character varying(10),
    monto_pagado numeric(18,6),
    num_parcialidad integer,
    saldo_anterior numeric(18,6),
    saldo_insoluto numeric(18,6)
);


--
-- TOC entry 208 (class 1259 OID 18492)
-- Name: cfdi_relacionados_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cfdi_relacionados_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2359 (class 0 OID 0)
-- Dependencies: 208
-- Name: cfdi_relacionados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cfdi_relacionados_id_seq OWNED BY public.cfdi_relacionados.id;


--
-- TOC entry 205 (class 1259 OID 18461)
-- Name: comprobantes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comprobantes (
    uuid uuid NOT NULL,
    entidad_id uuid NOT NULL,
    serie character varying(25),
    folio character varying(40),
    fecha_emision timestamp without time zone NOT NULL,
    rfc_emisor character varying(13) NOT NULL,
    nombre_emisor character varying(255),
    rfc_receptor character varying(13) NOT NULL,
    nombre_receptor character varying(255),
    tipo_comprobante character varying(1) NOT NULL,
    moneda character varying(10),
    subtotal numeric(18,6) NOT NULL,
    total numeric(18,6) NOT NULL,
    metodo_pago character varying(10),
    forma_pago character varying(5),
    estatus_sat character varying(20),
    version character varying(10),
    xml_path character varying(1000) NOT NULL,
    pdf_path character varying(1000),
    created_at timestamp without time zone DEFAULT now(),
    orphan_payment boolean DEFAULT false,
    regimen_fiscal_receptor character varying(100),
    domicilio_fiscal_receptor character varying(5)
);


--
-- TOC entry 202 (class 1259 OID 16876)
-- Name: email_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.email_logs (
    id integer NOT NULL,
    email_queue_id integer NOT NULL,
    respuesta_smtp text,
    fecha_intento timestamp with time zone DEFAULT now()
);


--
-- TOC entry 201 (class 1259 OID 16874)
-- Name: email_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.email_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2360 (class 0 OID 0)
-- Dependencies: 201
-- Name: email_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.email_logs_id_seq OWNED BY public.email_logs.id;


--
-- TOC entry 200 (class 1259 OID 16862)
-- Name: email_queue; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.email_queue (
    id integer NOT NULL,
    entidad_id uuid NOT NULL,
    cfdi_uuid character varying(36) NOT NULL,
    destinatario character varying(255) NOT NULL,
    estado character varying(20),
    intentos integer,
    proximo_intento timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


--
-- TOC entry 199 (class 1259 OID 16860)
-- Name: email_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.email_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2361 (class 0 OID 0)
-- Dependencies: 199
-- Name: email_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.email_queue_id_seq OWNED BY public.email_queue.id;


--
-- TOC entry 207 (class 1259 OID 18478)
-- Name: entidad_smtp_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entidad_smtp_configs (
    id integer NOT NULL,
    entidad_id uuid,
    host character varying(255),
    port integer,
    username character varying(255),
    password_encrypted character varying(500),
    from_address character varying(255),
    security_type character varying(50),
    authentication_type character varying(50)
);


--
-- TOC entry 206 (class 1259 OID 18476)
-- Name: entidad_smtp_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.entidad_smtp_configs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2362 (class 0 OID 0)
-- Dependencies: 206
-- Name: entidad_smtp_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.entidad_smtp_configs_id_seq OWNED BY public.entidad_smtp_configs.id;


--
-- TOC entry 196 (class 1259 OID 16723)
-- Name: entidad_storage_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entidad_storage_configs (
    id integer NOT NULL,
    entidad_id uuid NOT NULL,
    source_type character varying(50) NOT NULL,
    base_path character varying(500) NOT NULL
);


--
-- TOC entry 195 (class 1259 OID 16721)
-- Name: entidad_storage_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.entidad_storage_configs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2363 (class 0 OID 0)
-- Dependencies: 195
-- Name: entidad_storage_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.entidad_storage_configs_id_seq OWNED BY public.entidad_storage_configs.id;


--
-- TOC entry 192 (class 1259 OID 16635)
-- Name: entidades_fiscales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entidades_fiscales (
    id uuid NOT NULL,
    rfc character varying(13) NOT NULL,
    razon_social character varying(255) NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    logo_url character varying(500)
);


--
-- TOC entry 214 (class 1259 OID 18610)
-- Name: financial_anomalies_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.financial_anomalies_logs (
    id integer NOT NULL,
    entidad_id uuid NOT NULL,
    uuid_documento uuid NOT NULL,
    tipo_anomalia character varying(50) NOT NULL,
    detalle text,
    fecha_deteccion timestamp without time zone DEFAULT now(),
    estatus_anomalia character varying(20) DEFAULT 'ACTIVA'::character varying
);


--
-- TOC entry 213 (class 1259 OID 18608)
-- Name: financial_anomalies_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.financial_anomalies_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2364 (class 0 OID 0)
-- Dependencies: 213
-- Name: financial_anomalies_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.financial_anomalies_logs_id_seq OWNED BY public.financial_anomalies_logs.id;


--
-- TOC entry 194 (class 1259 OID 16706)
-- Name: plantillas_correo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plantillas_correo (
    id integer NOT NULL,
    entidad_id uuid,
    tipo_plantilla character varying(50) NOT NULL,
    asunto character varying(255) NOT NULL,
    cuerpo_html text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- TOC entry 193 (class 1259 OID 16704)
-- Name: plantillas_correo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.plantillas_correo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2365 (class 0 OID 0)
-- Dependencies: 193
-- Name: plantillas_correo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.plantillas_correo_id_seq OWNED BY public.plantillas_correo.id;


--
-- TOC entry 190 (class 1259 OID 16572)
-- Name: tenant_storage_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_storage_configs (
    id integer NOT NULL,
    tenant_id uuid NOT NULL,
    source_type character varying(50) NOT NULL,
    base_path character varying(500) NOT NULL
);


--
-- TOC entry 189 (class 1259 OID 16570)
-- Name: tenant_storage_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tenant_storage_configs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2366 (class 0 OID 0)
-- Dependencies: 189
-- Name: tenant_storage_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tenant_storage_configs_id_seq OWNED BY public.tenant_storage_configs.id;


--
-- TOC entry 203 (class 1259 OID 18436)
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    tenant_id uuid NOT NULL,
    rfc character varying(13) NOT NULL,
    business_name character varying(200) NOT NULL,
    base_repository_path character varying(1000),
    logo_path character varying(500),
    is_active boolean
);


--
-- TOC entry 204 (class 1259 OID 18446)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id uuid NOT NULL,
    tenant_id uuid,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email character varying(150),
    is_active boolean,
    is_superadmin boolean,
    rol character varying(20) DEFAULT 'VISOR'::character varying
);


--
-- TOC entry 212 (class 1259 OID 18521)
-- Name: usuario_entidad_acceso; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuario_entidad_acceso (
    usuario_id uuid NOT NULL,
    entidad_id uuid NOT NULL,
    rol character varying(50) NOT NULL
);


--
-- TOC entry 191 (class 1259 OID 16622)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id uuid NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255),
    auth_provider character varying(50),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    is_superadmin boolean DEFAULT false,
    last_login timestamp with time zone
);


--
-- TOC entry 216 (class 1259 OID 18778)
-- Name: v_ppd_semaforo_status; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_ppd_semaforo_status AS
 SELECT c.uuid,
    c.folio,
    c.total,
    c.rfc_receptor,
    c.entidad_id,
    c.fecha_emision,
    COALESCE(sum(r.monto_pagado), (0)::numeric) AS total_pagado,
    ((c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)))::numeric(18,2) AS saldo_insoluto
   FROM (public.comprobantes c
     LEFT JOIN public.cfdi_relacionados r ON (((c.uuid)::text = lower(btrim((r.uuid_relacionado)::text)))))
  WHERE (((c.tipo_comprobante)::text = 'I'::text) AND ((c.metodo_pago)::text = 'PPD'::text))
  GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id, c.fecha_emision;


--
-- TOC entry 215 (class 1259 OID 18718)
-- Name: v_ppd_semaforo_status_source; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_ppd_semaforo_status_source AS
 SELECT c.uuid,
    c.folio,
    c.total,
    c.rfc_receptor,
    c.entidad_id,
    COALESCE(sum(r.monto_pagado), (0)::numeric) AS total_pagado,
    (c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)) AS saldo_raw,
        CASE
            WHEN ((c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)) < 1.00) THEN 0.00
            ELSE (c.total - COALESCE(sum(r.monto_pagado), (0)::numeric))
        END AS saldo_insoluto,
        CASE
            WHEN ((c.total - COALESCE(sum(r.monto_pagado), (0)::numeric)) < 1.00) THEN 'PAGADO'::text
            WHEN (COALESCE(sum(r.monto_pagado), (0)::numeric) <= (0)::numeric) THEN 'PENDIENTE'::text
            ELSE 'PARCIAL'::text
        END AS estado_semaforo
   FROM (public.comprobantes c
     LEFT JOIN public.cfdi_relacionados r ON ((lower((c.uuid)::text) = lower((r.uuid_relacionado)::text))))
  WHERE (((c.metodo_pago)::text = 'PPD'::text) AND ((c.tipo_comprobante)::text = 'I'::text))
  GROUP BY c.uuid, c.folio, c.total, c.rfc_receptor, c.entidad_id;


--
-- TOC entry 2157 (class 2604 OID 18799)
-- Name: auth_recovery_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_recovery_tokens ALTER COLUMN id SET DEFAULT nextval('public.auth_recovery_tokens_id_seq'::regclass);


--
-- TOC entry 2140 (class 2604 OID 16742)
-- Name: bitacora_auditoria id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora_auditoria ALTER COLUMN id SET DEFAULT nextval('public.bitacora_auditoria_id_seq'::regclass);


--
-- TOC entry 2155 (class 2604 OID 18790)
-- Name: cfdi_aplicaciones_manuales id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_aplicaciones_manuales ALTER COLUMN id SET DEFAULT nextval('public.cfdi_aplicaciones_manuales_id_seq'::regclass);


--
-- TOC entry 2151 (class 2604 OID 18510)
-- Name: cfdi_conceptos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_conceptos ALTER COLUMN id SET DEFAULT nextval('public.cfdi_conceptos_id_seq'::regclass);


--
-- TOC entry 2150 (class 2604 OID 18497)
-- Name: cfdi_relacionados id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_relacionados ALTER COLUMN id SET DEFAULT nextval('public.cfdi_relacionados_id_seq'::regclass);


--
-- TOC entry 2144 (class 2604 OID 16879)
-- Name: email_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_logs ALTER COLUMN id SET DEFAULT nextval('public.email_logs_id_seq'::regclass);


--
-- TOC entry 2142 (class 2604 OID 16865)
-- Name: email_queue id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_queue ALTER COLUMN id SET DEFAULT nextval('public.email_queue_id_seq'::regclass);


--
-- TOC entry 2149 (class 2604 OID 18481)
-- Name: entidad_smtp_configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_smtp_configs ALTER COLUMN id SET DEFAULT nextval('public.entidad_smtp_configs_id_seq'::regclass);


--
-- TOC entry 2139 (class 2604 OID 16726)
-- Name: entidad_storage_configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_storage_configs ALTER COLUMN id SET DEFAULT nextval('public.entidad_storage_configs_id_seq'::regclass);


--
-- TOC entry 2152 (class 2604 OID 18613)
-- Name: financial_anomalies_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_anomalies_logs ALTER COLUMN id SET DEFAULT nextval('public.financial_anomalies_logs_id_seq'::regclass);


--
-- TOC entry 2137 (class 2604 OID 16709)
-- Name: plantillas_correo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plantillas_correo ALTER COLUMN id SET DEFAULT nextval('public.plantillas_correo_id_seq'::regclass);


--
-- TOC entry 2133 (class 2604 OID 16575)
-- Name: tenant_storage_configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_storage_configs ALTER COLUMN id SET DEFAULT nextval('public.tenant_storage_configs_id_seq'::regclass);


--
-- TOC entry 2209 (class 2606 OID 18803)
-- Name: auth_recovery_tokens auth_recovery_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_recovery_tokens
    ADD CONSTRAINT auth_recovery_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 2211 (class 2606 OID 18805)
-- Name: auth_recovery_tokens auth_recovery_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_recovery_tokens
    ADD CONSTRAINT auth_recovery_tokens_token_key UNIQUE (token);


--
-- TOC entry 2179 (class 2606 OID 16748)
-- Name: bitacora_auditoria bitacora_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora_auditoria
    ADD CONSTRAINT bitacora_auditoria_pkey PRIMARY KEY (id);


--
-- TOC entry 2207 (class 2606 OID 18793)
-- Name: cfdi_aplicaciones_manuales cfdi_aplicaciones_manuales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_aplicaciones_manuales
    ADD CONSTRAINT cfdi_aplicaciones_manuales_pkey PRIMARY KEY (id);


--
-- TOC entry 2201 (class 2606 OID 18515)
-- Name: cfdi_conceptos cfdi_conceptos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_conceptos
    ADD CONSTRAINT cfdi_conceptos_pkey PRIMARY KEY (id);


--
-- TOC entry 2161 (class 2606 OID 16564)
-- Name: cfdi_metadata cfdi_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_metadata
    ADD CONSTRAINT cfdi_metadata_pkey PRIMARY KEY (uuid);


--
-- TOC entry 2199 (class 2606 OID 18499)
-- Name: cfdi_relacionados cfdi_relacionados_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_relacionados
    ADD CONSTRAINT cfdi_relacionados_pkey PRIMARY KEY (id);


--
-- TOC entry 2193 (class 2606 OID 18469)
-- Name: comprobantes comprobantes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes
    ADD CONSTRAINT comprobantes_pkey PRIMARY KEY (uuid);


--
-- TOC entry 2183 (class 2606 OID 16885)
-- Name: email_logs email_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_logs
    ADD CONSTRAINT email_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 2181 (class 2606 OID 16868)
-- Name: email_queue email_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_pkey PRIMARY KEY (id);


--
-- TOC entry 2197 (class 2606 OID 18486)
-- Name: entidad_smtp_configs entidad_smtp_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_smtp_configs
    ADD CONSTRAINT entidad_smtp_configs_pkey PRIMARY KEY (id);


--
-- TOC entry 2177 (class 2606 OID 16731)
-- Name: entidad_storage_configs entidad_storage_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_storage_configs
    ADD CONSTRAINT entidad_storage_configs_pkey PRIMARY KEY (id);


--
-- TOC entry 2171 (class 2606 OID 16640)
-- Name: entidades_fiscales entidades_fiscales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidades_fiscales
    ADD CONSTRAINT entidades_fiscales_pkey PRIMARY KEY (id);


--
-- TOC entry 2173 (class 2606 OID 16642)
-- Name: entidades_fiscales entidades_fiscales_rfc_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidades_fiscales
    ADD CONSTRAINT entidades_fiscales_rfc_key UNIQUE (rfc);


--
-- TOC entry 2205 (class 2606 OID 18620)
-- Name: financial_anomalies_logs financial_anomalies_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_anomalies_logs
    ADD CONSTRAINT financial_anomalies_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 2175 (class 2606 OID 16715)
-- Name: plantillas_correo plantillas_correo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plantillas_correo
    ADD CONSTRAINT plantillas_correo_pkey PRIMARY KEY (id);


--
-- TOC entry 2163 (class 2606 OID 16580)
-- Name: tenant_storage_configs tenant_storage_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_storage_configs
    ADD CONSTRAINT tenant_storage_configs_pkey PRIMARY KEY (id);


--
-- TOC entry 2185 (class 2606 OID 18443)
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (tenant_id);


--
-- TOC entry 2187 (class 2606 OID 18445)
-- Name: tenants tenants_rfc_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_rfc_key UNIQUE (rfc);


--
-- TOC entry 2189 (class 2606 OID 18453)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 2191 (class 2606 OID 18455)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 2203 (class 2606 OID 18525)
-- Name: usuario_entidad_acceso usuario_entidad_acceso_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario_entidad_acceso
    ADD CONSTRAINT usuario_entidad_acceso_pkey PRIMARY KEY (usuario_id, entidad_id);


--
-- TOC entry 2165 (class 2606 OID 16634)
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- TOC entry 2167 (class 2606 OID 16630)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 2169 (class 2606 OID 16632)
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- TOC entry 2194 (class 1259 OID 18626)
-- Name: idx_comprobantes_orphan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_comprobantes_orphan ON public.comprobantes USING btree (orphan_payment) WHERE (orphan_payment = true);


--
-- TOC entry 2195 (class 1259 OID 18475)
-- Name: ix_comprobantes_uuid; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comprobantes_uuid ON public.comprobantes USING btree (uuid);


--
-- TOC entry 2226 (class 2606 OID 18806)
-- Name: auth_recovery_tokens auth_recovery_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_recovery_tokens
    ADD CONSTRAINT auth_recovery_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 2215 (class 2606 OID 16754)
-- Name: bitacora_auditoria bitacora_auditoria_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora_auditoria
    ADD CONSTRAINT bitacora_auditoria_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.entidades_fiscales(id);


--
-- TOC entry 2214 (class 2606 OID 16749)
-- Name: bitacora_auditoria bitacora_auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora_auditoria
    ADD CONSTRAINT bitacora_auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- TOC entry 2222 (class 2606 OID 18516)
-- Name: cfdi_conceptos cfdi_conceptos_cfdi_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_conceptos
    ADD CONSTRAINT cfdi_conceptos_cfdi_id_fkey FOREIGN KEY (cfdi_id) REFERENCES public.comprobantes(uuid) ON DELETE CASCADE;


--
-- TOC entry 2221 (class 2606 OID 18500)
-- Name: cfdi_relacionados cfdi_relacionados_cfdi_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cfdi_relacionados
    ADD CONSTRAINT cfdi_relacionados_cfdi_id_fkey FOREIGN KEY (cfdi_id) REFERENCES public.comprobantes(uuid) ON DELETE CASCADE;


--
-- TOC entry 2219 (class 2606 OID 18470)
-- Name: comprobantes comprobantes_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes
    ADD CONSTRAINT comprobantes_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.tenants(tenant_id);


--
-- TOC entry 2217 (class 2606 OID 16886)
-- Name: email_logs email_logs_email_queue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_logs
    ADD CONSTRAINT email_logs_email_queue_id_fkey FOREIGN KEY (email_queue_id) REFERENCES public.email_queue(id);


--
-- TOC entry 2216 (class 2606 OID 16869)
-- Name: email_queue email_queue_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.entidades_fiscales(id);


--
-- TOC entry 2220 (class 2606 OID 18487)
-- Name: entidad_smtp_configs entidad_smtp_configs_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_smtp_configs
    ADD CONSTRAINT entidad_smtp_configs_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.tenants(tenant_id) ON DELETE CASCADE;


--
-- TOC entry 2213 (class 2606 OID 16732)
-- Name: entidad_storage_configs entidad_storage_configs_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entidad_storage_configs
    ADD CONSTRAINT entidad_storage_configs_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.entidades_fiscales(id);


--
-- TOC entry 2225 (class 2606 OID 18621)
-- Name: financial_anomalies_logs financial_anomalies_logs_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_anomalies_logs
    ADD CONSTRAINT financial_anomalies_logs_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.tenants(tenant_id) ON DELETE CASCADE;


--
-- TOC entry 2212 (class 2606 OID 16716)
-- Name: plantillas_correo plantillas_correo_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plantillas_correo
    ADD CONSTRAINT plantillas_correo_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.entidades_fiscales(id);


--
-- TOC entry 2218 (class 2606 OID 18456)
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);


--
-- TOC entry 2224 (class 2606 OID 18531)
-- Name: usuario_entidad_acceso usuario_entidad_acceso_entidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario_entidad_acceso
    ADD CONSTRAINT usuario_entidad_acceso_entidad_id_fkey FOREIGN KEY (entidad_id) REFERENCES public.tenants(tenant_id) ON DELETE CASCADE;


--
-- TOC entry 2223 (class 2606 OID 18526)
-- Name: usuario_entidad_acceso usuario_entidad_acceso_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario_entidad_acceso
    ADD CONSTRAINT usuario_entidad_acceso_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


-- Completed on 2026-04-17 15:29:00

--
-- PostgreSQL database dump complete
--

