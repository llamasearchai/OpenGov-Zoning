"""SQLAlchemy database models for OpenGov Zoning API."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Enum,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    # Use 'table_metadata' instead of 'metadata' which is reserved by SQLAlchemy
    table_metadata = Column(JSON, default=dict, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @hybrid_property
    def is_active(self):
        """Check if record is active (not soft deleted)."""
        return not self.is_deleted


class User(TimestampMixin, Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="user", nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("ZoningAnalysis", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("login_attempts >= 0", name="check_login_attempts_positive"),
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_username_active", "username", "is_active"),
    )

    @hybrid_property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def is_locked(self):
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until


class Project(TimestampMixin, SoftDeleteMixin, Base):
    """Project model for zoning analysis projects."""

    __tablename__ = "projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(100), nullable=False)  # e.g., "solar-farm", "data-center"
    status = Column(String(50), default="draft", nullable=False)
    priority = Column(String(20), default="medium", nullable=False)

    # Location information
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geometry = Column(JSON, nullable=True)  # GeoJSON geometry

    # Project specifications
    size_acres = Column(Float, nullable=True)
    building_height = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    timeline_months = Column(Integer, nullable=True)

    # Metadata
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    table_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    analyses = relationship("ZoningAnalysis", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("size_acres >= 0", name="check_size_acres_positive"),
        CheckConstraint("building_height >= 0", name="check_building_height_positive"),
        CheckConstraint("estimated_cost >= 0", name="check_estimated_cost_positive"),
        CheckConstraint("timeline_months > 0", name="check_timeline_months_positive"),
        Index("ix_projects_owner_status", "owner_id", "status"),
        Index("ix_projects_location", "city", "state"),
        Index("ix_projects_type_status", "project_type", "status"),
    )


class ZoningAnalysis(TimestampMixin, Base):
    """Zoning analysis model for storing analysis results."""

    __tablename__ = "zoning_analyses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    analysis_type = Column(String(100), nullable=False)  # e.g., "permit-requirements", "zoning-compliance"

    # Analysis parameters
    jurisdiction = Column(String(255), nullable=False)
    zoning_district = Column(String(100), nullable=True)
    land_use_code = Column(String(50), nullable=True)

    # Analysis results
    status = Column(String(50), default="pending", nullable=False)
    confidence_score = Column(Float, nullable=True)
    results = Column(JSON, default=dict, nullable=False)
    recommendations = Column(JSON, default=list, nullable=False)
    warnings = Column(JSON, default=list, nullable=False)
    errors = Column(JSON, default=list, nullable=False)

    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)

    # Relationships
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    user = relationship("User", back_populates="analyses")
    project = relationship("Project", back_populates="analyses")

    __table_args__ = (
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="check_confidence_score_range"),
        CheckConstraint("processing_time_seconds >= 0", name="check_processing_time_positive"),
        CheckConstraint("input_tokens >= 0", name="check_input_tokens_positive"),
        CheckConstraint("output_tokens >= 0", name="check_output_tokens_positive"),
        Index("ix_zoning_analyses_user_status", "user_id", "status"),
        Index("ix_zoning_analyses_project_status", "project_id", "status"),
        Index("ix_zoning_analyses_jurisdiction", "jurisdiction"),
        Index("ix_zoning_analyses_type", "analysis_type"),
    )


class Document(TimestampMixin, SoftDeleteMixin, Base):
    """Document model for storing uploaded documents."""

    __tablename__ = "documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(128), nullable=False, unique=True)  # SHA-256 hash

    # Document metadata
    title = Column(String(255), nullable=True)
    document_type = Column(String(100), nullable=False)  # e.g., "zoning-code", "comprehensive-plan"
    jurisdiction = Column(String(255), nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    version = Column(String(50), nullable=True)

    # Processing status
    processing_status = Column(String(50), default="pending", nullable=False)
    extracted_text = Column(Text, nullable=True)
    table_metadata = Column(JSON, default=dict, nullable=False)
    ocr_confidence = Column(Float, nullable=True)

    # Relationships
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    user = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")

    __table_args__ = (
        CheckConstraint("file_size > 0", name="check_file_size_positive"),
        CheckConstraint("ocr_confidence >= 0 AND ocr_confidence <= 1", name="check_ocr_confidence_range"),
        Index("ix_documents_user_type", "user_id", "document_type"),
        Index("ix_documents_jurisdiction", "jurisdiction"),
        Index("ix_documents_hash", "file_hash"),
        Index("ix_documents_processing_status", "processing_status"),
    )


class APICall(TimestampMixin, Base):
    """API call logging model for monitoring and debugging."""

    __tablename__ = "api_calls"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    client_ip = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)

    # Request details
    request_headers = Column(JSON, default=dict, nullable=False)
    request_body = Column(JSON, default=dict, nullable=False)
    query_params = Column(JSON, default=dict, nullable=False)

    # Response details
    response_status = Column(Integer, nullable=False)
    response_headers = Column(JSON, default=dict, nullable=False)
    response_size = Column(Integer, nullable=True)

    # Performance metrics
    processing_time_ms = Column(Float, nullable=False)
    database_queries = Column(Integer, default=0, nullable=False)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)

    __table_args__ = (
        CheckConstraint("response_status >= 100 AND response_status <= 599", name="check_response_status_range"),
        CheckConstraint("processing_time_ms >= 0", name="check_processing_time_positive"),
        CheckConstraint("database_queries >= 0", name="check_database_queries_positive"),
        Index("ix_api_calls_user_timestamp", "user_id", "created_at"),
        Index("ix_api_calls_endpoint_method", "endpoint", "method"),
        Index("ix_api_calls_status_timestamp", "response_status", "created_at"),
        Index("ix_api_calls_error_timestamp", "error_code", "created_at"),
    )


class AuditLog(TimestampMixin, Base):
    """Audit log model for compliance and security."""

    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)

    # Audit details
    old_values = Column(JSON, default=dict, nullable=False)
    new_values = Column(JSON, default=dict, nullable=False)
    changes = Column(JSON, default=dict, nullable=False)

    # Context information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(255), nullable=True)

    # Additional metadata
    table_metadata = Column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_audit_logs_user_timestamp", "user_id", "created_at"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_action_timestamp", "action", "created_at"),
    )