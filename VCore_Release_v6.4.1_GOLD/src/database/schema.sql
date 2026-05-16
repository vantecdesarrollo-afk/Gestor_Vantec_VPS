-- =================================================================================
-- VANTEC CONSULTORES - FÁBRICA DE SOFTWARE
-- Proyecto: Gestor CFDI Vantec (Refactoring)
-- Motor: PostgreSQL 15+
-- Descripción: Esquema base con soporte Multi-tenant (RLS) y Auth Híbrida.
-- =================================================================================

-- 1. EXTENSIONES NECESARIAS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. TABLA: TENANTS (Sustituye a CatEntity)
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfc VARCHAR(13) UNIQUE NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    logo_path VARCHAR(500), -- Eliminado varbinary, ahora es ruta lógica
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: USERS (Sustituye a Scisa_User)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255), -- Para auth local
    auth_provider VARCHAR(50) DEFAULT 'LOCAL', -- Soporte para 'LDAP' o 'LOCAL'
    ldap_dn VARCHAR(255), -- Distinguished Name para LDAP
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABLA: CFDIS (Sustituye a TraCFDI, TraXML, TraAttachment)
CREATE TABLE cfdis (
    cfdi_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    uuid VARCHAR(36) NOT NULL,
    rfc_emisor VARCHAR(13) NOT NULL,
    rfc_receptor VARCHAR(13) NOT NULL,
    issue_date TIMESTAMP WITH TIME ZONE NOT NULL,
    total DECIMAL(18,6) NOT NULL,
    version VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'VALID',
    
    -- Rutas lógicas de almacenamiento (Reemplazo de binarios)
    -- Formato esperado: /storage/{tenant_id}/{YYYY}/{MM}/{UUID_Prefix}/archivo.xml
    xml_file_path VARCHAR(1000) NOT NULL, 
    pdf_file_path VARCHAR(1000),          
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, uuid) -- Un mismo folio no puede duplicarse en la misma empresa
);

-- =================================================================================
-- CONFIGURACIÓN DE SEGURIDAD (ROW LEVEL SECURITY - RLS)
-- =================================================================================

-- Activar RLS en las tablas sensibles
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cfdis ENABLE ROW LEVEL SECURITY;

-- Políticas para USERS (Un usuario solo ve a los usuarios de su propia empresa)
CREATE POLICY users_tenant_isolation ON users
    AS PERMISSIVE FOR ALL
    TO PUBLIC
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Políticas para CFDIS (Aislamiento absoluto de documentos)
CREATE POLICY cfdi_tenant_isolation ON cfdis
    AS PERMISSIVE FOR ALL
    TO PUBLIC
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- NOTA: El rol de PostgreSQL que use la API (FastAPI) deberá ejecutar:
-- SET LOCAL app.current_tenant_id = 'uuid-del-tenant-autenticado';
-- antes de cada transacción.
