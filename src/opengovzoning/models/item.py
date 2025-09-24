"""Pydantic models bridging FastAPI and sqlite-utils demo storage."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ZoningDocumentBase(BaseModel):
    """Base model for ZoningDocument."""

    name: str = Field(..., description="ZoningDocument name")
    description: str = Field(..., description="ZoningDocument description")


class ZoningDocumentCreate(ZoningDocumentBase):
    """Model for creating new ZoningDocument."""


class ZoningDocument(ZoningDocumentBase):
    """Complete ZoningDocument model."""

    id: UUID = Field(default_factory=uuid4, description="Unique database identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        from_attributes = True


class PermitBase(BaseModel):
    """Base model for Permit."""

    title: str = Field(..., description="Permit title")
    content: str = Field(..., description="Permit content")


class PermitCreate(PermitBase):
    """Model for creating new Permit."""


class Permit(PermitBase):
    """Complete Permit model."""

    id: UUID = Field(default_factory=uuid4, description="Unique database identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        from_attributes = True

# Backwards-compatible aliases for storage/web layers
ItemCreate = ZoningDocumentCreate
Item = ZoningDocument