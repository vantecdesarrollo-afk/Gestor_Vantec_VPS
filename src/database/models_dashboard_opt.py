from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, CHAR, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

from src.database.models import Base

class DashCfdiDocument(Base):
    """
    Vista/Tabla Materializada o Tabla Física para el Dashboard
    Unifica lo esencial con índices duros.
    """
    __tablename__ = "dash_cfdi_documents"
    
    cfdi_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"))
    uuid_fiscal = Column(String(36), unique=True, nullable=False) 
    
    # Datos de Encabezado
    serie = Column(String(25))
    folio = Column(String(40))
    fecha_emision = Column(DateTime, nullable=False)
    rfc_emisor = Column(String(13), nullable=False)
    nombre_emisor = Column(String(255))
    rfc_receptor = Column(String(13), nullable=False)
    nombre_receptor = Column(String(255))
    
    # Datos Comerciales
    tipo_comprobante = Column(CHAR(1), nullable=False)
    moneda = Column(String(10), nullable=False, default='MXN') 
    tipo_cambio = Column(Numeric(18, 6), default=1.0)
    subtotal = Column(Numeric(18, 6), nullable=False)
    total = Column(Numeric(18, 6), nullable=False)
    metodo_pago = Column(String(5)) 
    forma_pago = Column(String(5))
    
    # Control de Estado
    estatus_sat = Column(String(20)) 
    
    created_at = Column(DateTime, server_default=func.current_timestamp())

    concepts = relationship("DashCfdiConcept", back_populates="document", cascade="all, delete-orphan")


class DashCfdiConcept(Base):
    """
    Tabla de Conceptos (FÍSICA Y RELACIONAL, NO JSONB)
    """
    __tablename__ = "dash_cfdi_concepts"
    
    concept_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("dash_cfdi_documents.cfdi_id", ondelete="CASCADE"))
    
    # Claves para filtrado analítico
    clave_prod_serv = Column(String(20), nullable=False) 
    no_identificacion = Column(String(100))
    clave_unidad = Column(String(5), nullable=False)
    
    # Datos descriptivos y montos
    cantidad = Column(Numeric(18, 6), nullable=False)
    descripcion = Column(String, nullable=False) # TEXT
    valor_unitario = Column(Numeric(18, 6), nullable=False)
    importe = Column(Numeric(18, 6), nullable=False)

    document = relationship("DashCfdiDocument", back_populates="concepts")
