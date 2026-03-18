from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from src.database.models import Base
import uuid

class CfdiMetadata(Base):
    __tablename__ = "cfdi_metadata"

    uuid = Column(String(36), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    rfc_emisor = Column(String(13), nullable=False)
    rfc_receptor = Column(String(13), nullable=False)
    fecha_emision = Column(DateTime(timezone=True), nullable=False)
    tipo_comprobante = Column(String(1), nullable=False) # I, E, T, N, P
    total = Column(Numeric(18, 6), nullable=False)
    estado = Column(String(20), default='VIGENTE')
    tiene_pdf = Column(Boolean, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
