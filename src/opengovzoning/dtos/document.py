"""Document Data Transfer Objects."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DocumentMetadata(BaseModel):
    """Document metadata model."""

    title: Optional[str] = Field(default=None, description="Document title")
    author: Optional[str] = Field(default=None, description="Document author")
    subject: Optional[str] = Field(default=None, description="Document subject")
    keywords: List[str] = Field(default_factory=list, description="Document keywords")
    description: Optional[str] = Field(default=None, description="Document description")
    language: Optional[str] = Field(default=None, description="Document language")
    page_count: Optional[int] = Field(default=None, ge=0, description="Number of pages")
    word_count: Optional[int] = Field(default=None, ge=0, description="Word count")
    character_count: Optional[int] = Field(default=None, ge=0, description="Character count")
    custom_fields: Dict = Field(default_factory=dict, description="Custom metadata fields")


class DocumentCreate(BaseModel):
    """Document creation request model."""

    filename: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Document type")
    project_id: Optional[UUID] = Field(default=None, description="Associated project ID")

    # Document metadata
    metadata: Optional[DocumentMetadata] = Field(default=None, description="Document metadata")

    # Processing options
    extract_text: bool = Field(default=True, description="Extract text from document")
    generate_summary: bool = Field(default=False, description="Generate document summary")
    detect_language: bool = Field(default=True, description="Detect document language")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        """Validate document type."""
        valid_types = [
            "zoning-code", "comprehensive-plan", "permit-application",
            "environmental-report", "site-plan", "technical-specification",
            "regulatory-document", "compliance-report", "other"
        ]
        if v not in valid_types:
            raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
        return v


class DocumentUpdate(BaseModel):
    """Document update request model."""

    title: Optional[str] = Field(default=None, description="Document title")
    document_type: Optional[str] = Field(default=None, description="Document type")
    jurisdiction: Optional[str] = Field(default=None, description="Jurisdiction")
    effective_date: Optional[datetime] = Field(default=None, description="Effective date")
    version: Optional[str] = Field(default=None, description="Document version")

    # Processing status
    processing_status: Optional[str] = Field(default=None, description="Processing status")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        """Validate document type."""
        if v is not None:
            valid_types = [
                "zoning-code", "comprehensive-plan", "permit-application",
                "environmental-report", "site-plan", "technical-specification",
                "regulatory-document", "compliance-report", "other"
            ]
            if v not in valid_types:
                raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("processing_status")
    @classmethod
    def validate_processing_status(cls, v):
        """Validate processing status."""
        if v is not None:
            valid_statuses = ["pending", "processing", "completed", "failed", "skipped"]
            if v not in valid_statuses:
                raise ValueError(f"Processing status must be one of: {', '.join(valid_statuses)}")
        return v


class DocumentResponse(BaseModel):
    """Document response model."""

    id: UUID
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str

    # Document metadata
    title: Optional[str]
    document_type: str
    jurisdiction: Optional[str]
    effective_date: Optional[datetime]
    version: Optional[str]

    # Processing status
    processing_status: str
    extracted_text: Optional[str]
    ocr_confidence: Optional[float]

    # Relationships
    user_id: UUID
    project_id: Optional[UUID]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""

    id: UUID
    filename: str
    file_size: int
    document_type: str
    upload_status: str
    message: str
    processing_estimated_time: Optional[int] = None  # seconds

    model_config = ConfigDict(from_attributes=True)


class DocumentFilterParams(BaseModel):
    """Document filtering parameters."""

    document_type: Optional[str] = Field(default=None, description="Filter by document type")
    processing_status: Optional[str] = Field(default=None, description="Filter by processing status")
    jurisdiction: Optional[str] = Field(default=None, description="Filter by jurisdiction")
    user_id: Optional[UUID] = Field(default=None, description="Filter by user")
    project_id: Optional[UUID] = Field(default=None, description="Filter by project")
    date_from: Optional[datetime] = Field(default=None, description="Filter by upload date from")
    date_to: Optional[datetime] = Field(default=None, description="Filter by upload date to")
    has_text: Optional[bool] = Field(default=None, description="Filter by text extraction status")
    min_size: Optional[int] = Field(default=None, ge=0, description="Minimum file size")
    max_size: Optional[int] = Field(default=None, ge=0, description="Maximum file size")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        """Validate document type filter."""
        if v is not None:
            valid_types = [
                "zoning-code", "comprehensive-plan", "permit-application",
                "environmental-report", "site-plan", "technical-specification",
                "regulatory-document", "compliance-report", "other"
            ]
            if v not in valid_types:
                raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("processing_status")
    @classmethod
    def validate_processing_status(cls, v):
        """Validate processing status filter."""
        if v is not None:
            valid_statuses = ["pending", "processing", "completed", "failed", "skipped"]
            if v not in valid_statuses:
                raise ValueError(f"Processing status must be one of: {', '.join(valid_statuses)}")
        return v


class DocumentProcessingStatus(BaseModel):
    """Document processing status response model."""

    document_id: UUID
    status: str
    progress_percentage: Optional[float] = None
    current_step: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    error_message: Optional[str] = None
    updated_at: datetime


class DocumentSearchResult(BaseModel):
    """Document search result model."""

    id: UUID
    filename: str
    title: Optional[str]
    document_type: str
    jurisdiction: Optional[str]
    snippet: Optional[str] = None  # Text snippet with search terms
    relevance_score: float
    matched_fields: List[str]

    model_config = ConfigDict(from_attributes=True)


class DocumentVersion(BaseModel):
    """Document version model."""

    version: str
    filename: str
    file_size: int
    uploaded_by: UUID
    uploaded_at: datetime
    is_current: bool
    changes_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentStats(BaseModel):
    """Document statistics model."""

    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    total_size_bytes: int
    average_processing_time: Optional[float]
    documents_with_text: int
    documents_without_text: int
    recent_uploads: List[Dict]

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BulkDocumentUploadRequest(BaseModel):
    """Bulk document upload request model."""

    project_id: Optional[UUID] = Field(default=None, description="Project to associate documents with")
    document_type: str = Field(..., description="Default document type for all uploads")
    extract_text: bool = Field(default=True, description="Extract text from all documents")
    generate_summaries: bool = Field(default=False, description="Generate summaries for all documents")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        """Validate document type."""
        valid_types = [
            "zoning-code", "comprehensive-plan", "permit-application",
            "environmental-report", "site-plan", "technical-specification",
            "regulatory-document", "compliance-report", "other"
        ]
        if v not in valid_types:
            raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
        return v


class BulkDocumentUploadResponse(BaseModel):
    """Bulk document upload response model."""

    total_requested: int
    successfully_uploaded: int
    failed_uploads: int
    errors: List[Dict]
    message: str