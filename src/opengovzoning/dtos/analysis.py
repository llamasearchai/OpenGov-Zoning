"""Analysis Data Transfer Objects."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .common import LocationInfo


class AnalysisResult(BaseModel):
    """Analysis result model."""

    category: str = Field(..., description="Result category")
    title: str = Field(..., description="Result title")
    description: str = Field(..., description="Result description")
    value: Any = Field(..., description="Result value")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score")
    source: Optional[str] = Field(default=None, description="Data source")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Additional metadata")


class Recommendation(BaseModel):
    """Analysis recommendation model."""

    type: str = Field(..., description="Recommendation type")
    priority: str = Field(..., description="Recommendation priority")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    actions: List[str] = Field(..., description="Recommended actions")
    estimated_effort: Optional[str] = Field(default=None, description="Estimated effort")
    estimated_cost: Optional[str] = Field(default=None, description="Estimated cost")
    timeline: Optional[str] = Field(default=None, description="Estimated timeline")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class ZoningAnalysisCreate(BaseModel):
    """Zoning analysis creation request model."""

    title: str = Field(..., min_length=1, max_length=255, description="Analysis title")
    analysis_type: str = Field(..., description="Analysis type")
    jurisdiction: str = Field(..., description="Jurisdiction for analysis")
    project_id: Optional[UUID] = Field(default=None, description="Associated project ID")

    # Analysis parameters
    zoning_district: Optional[str] = Field(default=None, description="Zoning district")
    land_use_code: Optional[str] = Field(default=None, description="Land use code")
    location: Optional[LocationInfo] = Field(default=None, description="Location information")

    # Analysis configuration
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_warnings: bool = Field(default=True, description="Include warnings")
    confidence_threshold: float = Field(default=0.7, ge=0, le=1, description="Confidence threshold")

    # Additional parameters
    parameters: Optional[Dict] = Field(default_factory=dict, description="Additional analysis parameters")

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        valid_types = [
            "permit-requirements", "zoning-compliance", "land-use-analysis",
            "environmental-impact", "feasibility-study", "regulatory-review"
        ]
        if v not in valid_types:
            raise ValueError(f"Analysis type must be one of: {', '.join(valid_types)}")
        return v


class ZoningAnalysisUpdate(BaseModel):
    """Zoning analysis update request model."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Analysis title")
    status: Optional[str] = Field(default=None, description="Analysis status")
    results: Optional[Dict] = Field(default=None, description="Analysis results")
    recommendations: Optional[List[Dict]] = Field(default=None, description="Analysis recommendations")
    warnings: Optional[List[str]] = Field(default=None, description="Analysis warnings")
    errors: Optional[List[str]] = Field(default=None, description="Analysis errors")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate analysis status."""
        if v is not None:
            valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class ZoningAnalysisResponse(BaseModel):
    """Zoning analysis response model."""

    id: UUID
    title: str
    analysis_type: str
    status: str
    jurisdiction: str
    zoning_district: Optional[str]
    land_use_code: Optional[str]

    # Results
    confidence_score: Optional[float]
    results: Dict
    recommendations: List[Dict]
    warnings: List[str]
    errors: List[str]

    # Processing metadata
    processing_time_seconds: Optional[float]
    model_used: Optional[str]
    model_version: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]

    # Relationships
    user_id: UUID
    project_id: Optional[UUID]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisFilterParams(BaseModel):
    """Analysis filtering parameters."""

    status: Optional[str] = Field(default=None, description="Filter by status")
    analysis_type: Optional[str] = Field(default=None, description="Filter by analysis type")
    jurisdiction: Optional[str] = Field(default=None, description="Filter by jurisdiction")
    user_id: Optional[UUID] = Field(default=None, description="Filter by user")
    project_id: Optional[UUID] = Field(default=None, description="Filter by project")
    date_from: Optional[datetime] = Field(default=None, description="Filter by date from")
    date_to: Optional[datetime] = Field(default=None, description="Filter by date to")
    min_confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Minimum confidence score")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status filter."""
        if v is not None:
            valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, v):
        """Validate analysis type filter."""
        if v is not None:
            valid_types = [
                "permit-requirements", "zoning-compliance", "land-use-analysis",
                "environmental-impact", "feasibility-study", "regulatory-review"
            ]
            if v not in valid_types:
                raise ValueError(f"Analysis type must be one of: {', '.join(valid_types)}")
        return v


class AnalysisMetricsResponse(BaseModel):
    """Analysis metrics response model."""

    total_analyses: int
    completed_analyses: int
    failed_analyses: int
    average_confidence: Optional[float]
    average_processing_time: Optional[float]
    analyses_by_type: Dict[str, int]
    analyses_by_status: Dict[str, int]
    recent_analyses: List[Dict]

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request model."""

    analyses: List[ZoningAnalysisCreate] = Field(..., description="List of analyses to run")
    priority: str = Field(default="normal", description="Batch priority")
    parallel_processing: bool = Field(default=True, description="Process analyses in parallel")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class BatchAnalysisResponse(BaseModel):
    """Batch analysis response model."""

    batch_id: UUID
    total_analyses: int
    accepted_analyses: int
    rejected_analyses: int
    message: str
    estimated_completion_time: Optional[datetime] = None


class AnalysisTemplate(BaseModel):
    """Analysis template model."""

    id: UUID
    name: str
    description: str
    analysis_type: str
    template_data: Dict
    is_default: bool = False
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)