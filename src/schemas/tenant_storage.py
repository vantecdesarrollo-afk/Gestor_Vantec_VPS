from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class TenantStorageConfigBase(BaseModel):
    tenant_id: UUID
    source_type: str = Field(..., description="'LEGACY_EMISION', 'N8N_INBOX', 'UPLOAD_MANUAL'")
    base_path: str = Field(..., max_length=500, example="E:\\ITC\\FAppeal\\ColorconCFDI\\Outfile")

class TenantStorageConfigCreate(TenantStorageConfigBase):
    pass

class TenantStorageConfig(TenantStorageConfigBase):
    id: int

    class Config:
        from_attributes = True
