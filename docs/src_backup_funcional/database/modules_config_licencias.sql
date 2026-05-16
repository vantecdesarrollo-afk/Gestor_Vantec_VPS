-- ==============================================================================
-- SCRIPT MAESTRO: MÓDULO DE CONFIGURACIÓN Y USUARIOS (PostgreSQL)
-- Objetivo: Soportar edición, deshabilitación de usuarios y licenciamiento.
-- ==============================================================================

-- 1. Catálogo de Entidades (Reemplaza al CatEntity del Legacy)
-- Soporta el esquema de licenciamiento que ya funcionaba
CREATE TABLE cat_entities (
    entity_id SERIAL PRIMARY KEY,
    rfc VARCHAR(13) NOT NULL UNIQUE,
    business_name VARCHAR(200) NOT NULL,
    is_legal_person BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Control de Licenciamiento (1 mes, 3 meses, 1 año)
    license_tier VARCHAR(20) CHECK (license_tier IN ('1_MES', '3_MESES', '1_ANIO')),
    license_issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    license_expiration_date DATE NOT NULL
);

-- 2. Tabla de Usuarios (Reemplaza a Scisa_User)
-- Contiene los campos exactos para el 2% que falta: Edición y Deshabilitación
CREATE TABLE sys_users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(150),
    
    -- Campos clave para la pantalla de configuración actual
    is_active BOOLEAN DEFAULT TRUE, -- Permite deshabilitar en lugar de borrar
    login_attempts INT DEFAULT 0,
    last_login TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Relación Usuario-Entidad y Roles (Reemplaza a Scisa_UsersRoles)
CREATE TABLE sys_user_roles (
    membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES sys_users(user_id) ON DELETE CASCADE,
    entity_id INT REFERENCES cat_entities(entity_id) ON DELETE CASCADE,
    role_name VARCHAR(50) NOT NULL, -- Ej: 'ADMIN', 'OPERADOR'
    
    UNIQUE(user_id, entity_id)
);

-- ==============================================================================
-- DATOS SEMILLA (Seed Data - Para que no inicien en blanco)
-- ==============================================================================

INSERT INTO cat_entities (rfc, business_name, license_tier, license_expiration_date) 
VALUES ('EPM880422LV3', 'EDITORIAL PLANETA MEXICANA', '1_ANIO', '2027-03-19');

INSERT INTO sys_users (username, full_name, password_hash, is_active)
VALUES ('admin_master', 'Administrador del Sistema', 'hash_temporal_aqui', TRUE);
