from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, CHAR, DECIMAL, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

# Se asume que usa la misma Base que el módulo de configuración o una nueva
# Para que funcionen las relaciones ForeignKey, deberían estar en el mismo metadata
# o importar el Base adecuado.
# Aquí usaremos declarative_base() pero se recomienda unificar en el proyecto real.
Base = declarative_base()

class CfdiDocument(Base):
    """
    Tabla Principal de CFDI (optimizado para el Dashboard)
    """
    __tablename__ = "cfdi_documents"
    
    cfdi_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(Integer, ForeignKey("cat_entities.entity_id", ondelete="CASCADE")) # Requiere cat_entities
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
    tipo_comprobante = Column(CHAR(1), nullable=False) # I, E, T, P, N
    moneda = Column(String(3), nullable=False, default='MXN')
    tipo_cambio = Column(DECIMAL(18, 6), default=1.0)
    subtotal = Column(DECIMAL(18, 6), nullable=False)
    total = Column(DECIMAL(18, 6), nullable=False)
    metodo_pago = Column(String(3)) # PUE, PPD
    forma_pago = Column(String(2))
    
    # Control de Estado
    estatus = Column(String(20), default='PROCESADO')
    
    created_at = Column(DateTime, server_default=func.current_timestamp())

    concepts = relationship("CfdiConcept", back_populates="document", cascade="all, delete-orphan")


class CfdiConcept(Base):
    """
    Tabla de Conceptos (Normalizada)
    """
    __tablename__ = "cfdi_concepts"
    
    concept_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi_documents.cfdi_id", ondelete="CASCADE"))
    
    clave_prod_serv = Column(String(20), nullable=False)
    no_identificacion = Column(String(100))
    cantidad = Column(DECIMAL(18, 6), nullable=False)
    clave_unidad = Column(String(5), nullable=False)
    descripcion = Column(String, nullable=False) # TEXT
    valor_unitario = Column(DECIMAL(18, 6), nullable=False)
    importe = Column(DECIMAL(18, 6), nullable=False)

    document = relationship("CfdiDocument", back_populates="concepts")
