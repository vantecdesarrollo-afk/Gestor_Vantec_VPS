from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List
import re

class CfdiRelacionadoRead(BaseModel):
    uuid_relacionado: str
    tipo_relacion: Optional[str] = None
    monto_pagado: Optional[float] = None
    saldo_insoluto: Optional[float] = None

    class Config:
        from_attributes = True

class REPAsociado(BaseModel):
    uuid: str
    serie: Optional[str] = None
    folio: Optional[str] = None
    issue_date: datetime
    total: float
    xml_file_path: Optional[str] = None
    pdf_file_path: Optional[str] = None

    class Config:
        from_attributes = True

class CfdiRead(BaseModel):
    cfdi_id: UUID
    uuid: str
    rfc_emisor: str
    rfc_receptor: str
    issue_date: datetime
    total: float
    version: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    metodo_pago: Optional[str] = None
    forma_pago: Optional[str] = None
    serie: Optional[str] = None
    folio: Optional[str] = None
    status: Optional[str] = None
    metadata_xml: Optional[dict] = None
    xml_file_path: Optional[str] = None
    pdf_file_path: Optional[str] = None
    relaciones: List[CfdiRelacionadoRead] = []
    reps_asociados: List[REPAsociado] = []
    saldo_pendiente: float = 0.0

    class Config:
        from_attributes = True

class CfdiCreate(BaseModel):
    uuid: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    tenant_id: UUID
    rfc_emisor: str = Field(..., min_length=12, max_length=13)
    rfc_receptor: str = Field(..., min_length=12, max_length=13)
    fecha_emision: datetime
    tipo_comprobante: str = Field(..., min_length=1, max_length=1)
    serie: Optional[str] = Field(None, max_length=25)
    folio: Optional[str] = Field(None, max_length=40)
    total: float = Field(..., ge=0)
    estado: str = Field(default='VIGENTE')
    tiene_pdf: bool = Field(default=False)
    source_type: str = Field(default='UPLOAD_MANUAL')
    xml_file_path: str = Field(..., max_length=1000)
    pdf_file_path: Optional[str] = Field(None, max_length=1000)

    @validator('rfc_emisor', 'rfc_receptor')
    def validate_rfc(cls, v):
        if not re.match(r'^[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{2}[0-9A]$', v):
            raise ValueError('Formato de RFC inválido')
        return v
    
    @validator('source_type')
    def validate_source(cls, v):
        valid_sources = ['LEGACY_EMISION', 'N8N_INBOX', 'UPLOAD_MANUAL', 'LOCAL_INDEX']
        if v not in valid_sources:
            raise ValueError(f'source_type debe ser uno de: {", ".join(valid_sources)}')
        return v

class IndexLocalRequest(BaseModel):
    xml_path: str
    pdf_path: Optional[str] = None
