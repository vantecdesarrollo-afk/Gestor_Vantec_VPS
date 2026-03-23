from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Boolean, Integer, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfc = Column(String(13), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    logo_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    comprobantes = relationship("Comprobante", back_populates="tenant", cascade="all, delete-orphan")
    cfdis = relationship("Cfdi", back_populates="tenant", cascade="all, delete-orphan")
    smtp_configs = relationship("EntidadSMTPConfig", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    tenant = relationship("Tenant", back_populates="users")

class Comprobante(Base):
    __tablename__ = "comprobantes"
    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True) 
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    serie = Column(String(25))
    folio = Column(String(25))
    fecha_emision = Column(DateTime)
    rfc_emisor = Column(String(13))
    nombre_emisor = Column(String(255))
    rfc_receptor = Column(String(13))
    nombre_receptor = Column(String(255))
    tipo_comprobante = Column(String(1)) # I, E, P
    moneda = Column(String(3))
    total = Column(Numeric(18, 6))
    estatus_sat = Column(String(20)) # Este es el que el front pide como 'estatus'
    ruta_resguardo = Column(String(500))
    metodo_pago = Column(String(10))
    forma_pago = Column(String(2))
    version = Column(String(10))
    ingestado_at = Column(DateTime)
    status = Column(String(50))
    tipo_cambio = Column(Numeric(18, 6))
    descuento = Column(Numeric(18, 6))
    total_impuestos_trasladados = Column(Numeric(18, 6))
    total_impuestos_retenidos = Column(Numeric(18, 6))
    subtotal = Column(Numeric(18, 6))

    tenant = relationship("Tenant", back_populates="comprobantes")
    relacionados = relationship(
        "CfdiRelacionado", 
        back_populates="comprobante",
        foreign_keys="[CfdiRelacionado.cfdi_id]"
    )

class CfdiRelacionado(Base):
    __tablename__ = "cfdi_relacionados"
    id = Column(Integer, primary_key=True)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("comprobantes.uuid"))
    uuid_padre = Column(String(36), nullable=False)
    uuid_relacionado = Column(String(36), nullable=False)
    tipo_relacion = Column(String(10))
    monto_pagado = Column(Numeric(18, 6))
    saldo_insoluto = Column(Numeric(18, 6))
    num_parcialidad = Column(Integer)

    comprobante = relationship("Comprobante", back_populates="relacionados", foreign_keys=[cfdi_id])


class EntidadSMTPConfig(Base):
    __tablename__ = "entidad_smtp_configs"
    id = Column(Integer, primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"))
    host = Column(String(255))
    port = Column(Integer)
    username = Column(String(255))
    password_encrypted = Column(String(500))
    from_address = Column(String(255))
    security_type = Column(String(50))
    authentication_type = Column(String(50))
    tenant = relationship("Tenant", back_populates="smtp_configs")

class Cfdi(Base):
    __tablename__ = "cfdis"
    cfdi_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    uuid = Column(String(36), nullable=False, index=True)
    rfc_emisor = Column(String(13), nullable=False)
    rfc_receptor = Column(String(13), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    total = Column(Numeric(18, 6), nullable=False)
    version = Column(String(10), nullable=False)
    status = Column(String(50), default='VALID')
    
    xml_file_path = Column(String(1000), nullable=False)
    pdf_file_path = Column(String(1000))
    
    created_at = Column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", back_populates="cfdis")

class SysUserRole(Base):
    __tablename__ = "usuario_entidad_acceso"
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), primary_key=True)
    rol = Column(String(50), nullable=False) # 'ADMIN', 'OPERADOR', 'VISOR'

    user = relationship("User", foreign_keys=[usuario_id])
    tenant = relationship("Tenant", foreign_keys=[entidad_id])