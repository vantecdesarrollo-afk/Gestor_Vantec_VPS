from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

# --- Original v1.0.0 Models ---

class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfc = Column(String(13), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    logo_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    cfdis = relationship("Cfdi", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    auth_provider = Column(String(50), default='LOCAL')
    ldap_dn = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")

class Cfdi(Base):
    __tablename__ = "cfdis"

    cfdi_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    uuid = Column(String(36), nullable=False)
    rfc_emisor = Column(String(13), nullable=False)
    rfc_receptor = Column(String(13), nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    total = Column(Numeric(18, 6), nullable=False)
    version = Column(String(10), nullable=False)
    status = Column(String(50), default="VALID")
    xml_file_path = Column(String(1000), nullable=False)
    pdf_file_path = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="cfdis")

class EntidadSMTPConfig(Base):
    __tablename__ = "entidad_smtp_configs"

    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), primary_key=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(String(500), nullable=False)
    from_address = Column(String(255))
    security_type = Column(String(50), default="STARTTLS")
    authentication_type = Column(String(50), default="LOGIN")
    
    tenant = relationship("Tenant")

# --- Appended Missing Models for legacy/linked APIs ---

class EntidadFiscal(Base):
    __tablename__ = "entidades_fiscales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfc = Column(String(13), unique=True, nullable=False)
    razon_social = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    logo_url = Column(String(500))

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    auth_provider = Column(String(50), default='LOCAL')
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

class Comprobante(Base):
    __tablename__ = "comprobantes"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serie = Column(String(20))
    folio = Column(String(20))
    rfc_emisor = Column(String(13), nullable=False)
    rfc_receptor = Column(String(13), nullable=False)
    version = Column(String(10))
    total = Column(Numeric(18, 6))
    ruta_resguardo = Column(String(1000))
    fecha_emision = Column(DateTime)
    ingestado_at = Column(DateTime)
    entidad_id = Column(UUID(as_uuid=True))
    tipo_comprobante = Column(String(10))
    metodo_pago = Column(String(10))
    forma_pago = Column(String(10))
    status = Column(String(50))

    relaciones = relationship("CfdiRelacionado", lazy="selectin", backref="comprobante")

class CfdiRelacionado(Base):
    __tablename__ = "cfdi_relacionados"

    id = Column(Integer, primary_key=True)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("comprobantes.uuid"))
    uuid_padre = Column(String(36))
    uuid_relacionado = Column(String(36))
    tipo_relacion = Column(String(20))
    monto_pagado = Column(Numeric(18, 6))

class UsuarioEntidadAcceso(Base):
    __tablename__ = "usuario_entidad_acceso"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("entidades_fiscales.id"), primary_key=True)
    rol = Column(String(20), nullable=False)

class BitacoraAuditoria(Base):
    __tablename__ = "bitacora_auditoria"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("entidades_fiscales.id"))
    accion = Column(String(100), nullable=False)
    detalle = Column(JSONB)
