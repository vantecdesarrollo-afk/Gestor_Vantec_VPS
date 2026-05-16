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
    base_repository_path = Column(String(1000))
    logo_path = Column(String(500))
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    comprobantes = relationship("Comprobante", back_populates="tenant", cascade="all, delete-orphan")
    smtp_configs = relationship("EntidadSMTPConfig", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(150))
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    rol = Column(String(20), default='VISOR')
    
    tenant = relationship("Tenant", back_populates="users")

class Comprobante(Base):
    __tablename__ = "comprobantes"
    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True) 
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    serie = Column(String(25))
    folio = Column(String(40))
    fecha_emision = Column(DateTime, nullable=False)
    rfc_emisor = Column(String(13), nullable=False)
    nombre_emisor = Column(String(255))
    rfc_receptor = Column(String(13), nullable=False)
    nombre_receptor = Column(String(255))
    tipo_comprobante = Column(String(1), nullable=False) # I, E, P, N, T
    moneda = Column(String(10), default='MXN')
    subtotal = Column(Numeric(18, 6), nullable=False)
    total = Column(Numeric(18, 6), nullable=False)
    metodo_pago = Column(String(10))
    forma_pago = Column(String(5))
    estatus_sat = Column(String(20))
    version = Column(String(10))
    xml_path = Column(String(1000), nullable=False)
    pdf_path = Column(String(1000))
    regimen_fiscal_receptor = Column(String(100), nullable=True) # v4.0
    domicilio_fiscal_receptor = Column(String(5), nullable=True) # v4.0
    orphan_payment = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", back_populates="comprobantes")
    relacionados = relationship("CfdiRelacionado", back_populates="comprobante", cascade="all, delete-orphan")
    conceptos = relationship("CfdiConcepto", back_populates="comprobante", cascade="all, delete-orphan")

class CfdiRelacionado(Base):
    __tablename__ = "cfdi_relacionados"
    id = Column(Integer, primary_key=True)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("comprobantes.uuid", ondelete="CASCADE"))
    uuid_padre = Column(String(36), nullable=False)
    uuid_relacionado = Column(String(36), nullable=False)
    tipo_relacion = Column(String(10))
    monto_pagado = Column(Numeric(18, 6), default=0.0)
    num_parcialidad = Column(Integer)
    saldo_anterior = Column(Numeric(18, 6), default=0.0)
    saldo_insoluto = Column(Numeric(18, 6), default=0.0)

    comprobante = relationship("Comprobante", back_populates="relacionados")

class CfdiConcepto(Base):
    __tablename__ = "cfdi_conceptos"
    id = Column(Integer, primary_key=True)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("comprobantes.uuid", ondelete="CASCADE"), nullable=False)
    clave_prod_serv = Column(String(20))
    cantidad = Column(Numeric(15, 6))
    descripcion = Column(Text)
    valor_unitario = Column(Numeric(15, 6))
    importe = Column(Numeric(15, 6))

    comprobante = relationship("Comprobante", back_populates="conceptos")

class EntidadSMTPConfig(Base):
    __tablename__ = "entidad_smtp_configs"
    id = Column(Integer, primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"))
    host = Column(String(255))
    port = Column(Integer)
    username = Column(String(255))
    password_encrypted = Column(String(500))
    from_address = Column(String(255))
    security_type = Column(String(50), default='STARTTLS')
    authentication_type = Column(String(50), default='LOGIN')
    
    tenant = relationship("Tenant", back_populates="smtp_configs")

class SysUserRole(Base):
    __tablename__ = "usuario_entidad_acceso"
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"), primary_key=True)
    rol = Column(String(50), nullable=False) # 'ADMIN', 'OPERADOR', 'VISOR'

    user = relationship("User")
    tenant = relationship("Tenant")

class FinancialAnomalyLog(Base):
    __tablename__ = "financial_anomalies_logs"
    id = Column(Integer, primary_key=True)
    entidad_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False)
    uuid_documento = Column(UUID(as_uuid=True), nullable=False)
    tipo_anomalia = Column(String(50), nullable=False) 
    detalle = Column(Text)
    fecha_deteccion = Column(DateTime, server_default=func.now())
    estatus_anomalia = Column(String(20), default='ACTIVA')

class AuthRecoveryToken(Base):
    __tablename__ = "auth_recovery_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)