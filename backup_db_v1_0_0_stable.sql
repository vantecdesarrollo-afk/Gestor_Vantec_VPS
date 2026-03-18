--
-- PostgreSQL database dump
--

\restrict secPijgWzc245aVU8LqNIPNkSCmpAO06XCggCA8mh8DAgYivXQ9jSk70aoxHauC

-- Dumped from database version 15.17
-- Dumped by pg_dump version 15.17

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cfdis; Type: TABLE; Schema: public; Owner: vantec_user
--

CREATE TABLE public.cfdis (
    cfdi_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    tenant_id uuid NOT NULL,
    uuid character varying(36) NOT NULL,
    rfc_emisor character varying(13) NOT NULL,
    rfc_receptor character varying(13) NOT NULL,
    issue_date timestamp with time zone NOT NULL,
    total numeric(18,6) NOT NULL,
    version character varying(10) NOT NULL,
    status character varying(50) DEFAULT 'VALID'::character varying,
    xml_file_path character varying(1000) NOT NULL,
    pdf_file_path character varying(1000),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.cfdis OWNER TO vantec_user;

--
-- Name: tenants; Type: TABLE; Schema: public; Owner: vantec_user
--

CREATE TABLE public.tenants (
    tenant_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    rfc character varying(13) NOT NULL,
    business_name character varying(200) NOT NULL,
    logo_path character varying(500),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tenants OWNER TO vantec_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: vantec_user
--

CREATE TABLE public.users (
    user_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    tenant_id uuid NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255),
    password_hash character varying(255),
    auth_provider character varying(50) DEFAULT 'LOCAL'::character varying,
    ldap_dn character varying(255),
    is_active boolean DEFAULT true,
    last_login timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO vantec_user;

--
-- Data for Name: cfdis; Type: TABLE DATA; Schema: public; Owner: vantec_user
--

COPY public.cfdis (cfdi_id, tenant_id, uuid, rfc_emisor, rfc_receptor, issue_date, total, version, status, xml_file_path, pdf_file_path, created_at) FROM stdin;
94aa3f0e-9df2-42d8-ab95-c6bb463c37f1	d2abb56a-8bdf-4416-bc3d-16a15d7d7c20	734F0FA3-6FD9-4E39-9892-B15C66D0E197	VCO1307234VA	EPM880422LV3	2026-03-02 12:26:10+00	31619.280000	4.0	VALID	/storage/d2abb56a-8bdf-4416-bc3d-16a15d7d7c20/2026/03/734F0FA3-6FD9-4E39-9892-B15C66D0E197.xml	\N	2026-03-05 17:56:08.295463+00
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: vantec_user
--

COPY public.tenants (tenant_id, rfc, business_name, logo_path, is_active, created_at) FROM stdin;
d2abb56a-8bdf-4416-bc3d-16a15d7d7c20	VAN010101ABC	Vantec Consultores S.A. de C.V.	\N	t	2026-03-05 16:52:02.713532+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: vantec_user
--

COPY public.users (user_id, tenant_id, username, email, password_hash, auth_provider, ldap_dn, is_active, last_login, created_at) FROM stdin;
fdb78c75-3468-48ed-8dae-76405a42d061	d2abb56a-8bdf-4416-bc3d-16a15d7d7c20	admin	admin@vantec.mx	$2b$12$eJsxAnVosd1UnFgbRDNmwe2rkB7j0C43Q07E5Z0QqDj9q/d9nMjeS	LOCAL	\N	t	2026-03-05 17:55:50.963326+00	2026-03-05 16:52:02.713532+00
\.


--
-- Name: cfdis cfdis_pkey; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.cfdis
    ADD CONSTRAINT cfdis_pkey PRIMARY KEY (cfdi_id);


--
-- Name: cfdis cfdis_tenant_id_uuid_key; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.cfdis
    ADD CONSTRAINT cfdis_tenant_id_uuid_key UNIQUE (tenant_id, uuid);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (tenant_id);


--
-- Name: tenants tenants_rfc_key; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_rfc_key UNIQUE (rfc);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: cfdis cfdis_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.cfdis
    ADD CONSTRAINT cfdis_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id) ON DELETE CASCADE;


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vantec_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id) ON DELETE CASCADE;


--
-- Name: cfdis cfdi_tenant_isolation; Type: POLICY; Schema: public; Owner: vantec_user
--

CREATE POLICY cfdi_tenant_isolation ON public.cfdis USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- Name: cfdis; Type: ROW SECURITY; Schema: public; Owner: vantec_user
--

ALTER TABLE public.cfdis ENABLE ROW LEVEL SECURITY;

--
-- Name: users; Type: ROW SECURITY; Schema: public; Owner: vantec_user
--

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

--
-- Name: users users_tenant_isolation; Type: POLICY; Schema: public; Owner: vantec_user
--

CREATE POLICY users_tenant_isolation ON public.users USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- PostgreSQL database dump complete
--

\unrestrict secPijgWzc245aVU8LqNIPNkSCmpAO06XCggCA8mh8DAgYivXQ9jSk70aoxHauC

