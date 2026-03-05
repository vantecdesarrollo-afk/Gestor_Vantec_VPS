from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Boolean, func
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
