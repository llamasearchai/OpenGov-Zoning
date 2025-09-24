"""Project Data Transfer Objects."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .common import LocationInfo, MetadataInfo


class ProjectCreate(BaseModel):
    """Project creation request model."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    project_type: str = Field(..., description="Project type (e.g., solar-farm, data-center)")
    priority: str = Field(default="medium", description="Project priority")

    # Location information
    location: LocationInfo = Field(..., description="Project location")

    # Project specifications
    size_acres: Optional[float] = Field(default=None, ge=0, description="Project size in acres")
    building_height: Optional[float] = Field(default=None, ge=0, description="Building height")
    estimated_cost: Optional[float] = Field(default=None, ge=0, description="Estimated cost")
    timeline_months: Optional[int] = Field(default=None, ge=1, description="Timeline in months")

    # Metadata
    metadata: Optional[Dict] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v):
        """Validate project type."""
        valid_types = [
            "solar-farm", "wind-farm", "data-center", "telecom-tower",
            "residential", "commercial", "industrial", "mixed-use"
        ]
        if v not in valid_types:
            raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "medium", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class ProjectUpdate(BaseModel):
    """Project update request model."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    project_type: Optional[str] = Field(default=None, description="Project type")
    priority: Optional[str] = Field(default=None, description="Project priority")
    status: Optional[str] = Field(default=None, description="Project status")

    # Location information
    location: Optional[LocationInfo] = Field(default=None, description="Project location")

    # Project specifications
    size_acres: Optional[float] = Field(default=None, ge=0, description="Project size in acres")
    building_height: Optional[float] = Field(default=None, ge=0, description="Building height")
    estimated_cost: Optional[float] = Field(default=None, ge=0, description="Estimated cost")
    timeline_months: Optional[int] = Field(default=None, ge=1, description="Timeline in months")

    # Metadata
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v):
        """Validate project type."""
        if v is not None:
            valid_types = [
                "solar-farm", "wind-farm", "data-center", "telecom-tower",
                "residential", "commercial", "industrial", "mixed-use"
            ]
            if v not in valid_types:
                raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        if v is not None:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if v not in valid_priorities:
                raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate project status."""
        if v is not None:
            valid_statuses = ["draft", "active", "on-hold", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class ProjectResponse(BaseModel):
    """Project response model."""

    id: UUID
    name: str
    description: Optional[str]
    project_type: str
    status: str
    priority: str

    # Location information
    location: LocationInfo

    # Project specifications
    size_acres: Optional[float]
    building_height: Optional[float]
    estimated_cost: Optional[float]
    timeline_months: Optional[int]

    # Metadata
    owner_id: UUID
    metadata: Dict
    created_at: datetime
    updated_at: datetime

    # Computed fields
    progress_percentage: Optional[float] = Field(default=None, description="Project progress percentage")
    days_active: Optional[int] = Field(default=None, description="Days since project creation")

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Project list response model."""

    id: UUID
    name: str
    description: Optional[str]
    project_type: str
    status: str
    priority: str
    city: Optional[str]
    state: Optional[str]
    size_acres: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectSummary(BaseModel):
    """Project summary model for dashboards."""

    id: UUID
    name: str
    status: str
    project_type: str
    priority: str
    city: Optional[str]
    state: Optional[str]
    created_at: datetime
    analysis_count: int = 0
    document_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProjectStatusUpdate(BaseModel):
    """Project status update request model."""

    status: str = Field(..., description="New project status")
    notes: Optional[str] = Field(default=None, description="Status change notes")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate project status."""
        valid_statuses = ["draft", "active", "on-hold", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class ProjectFilterParams(BaseModel):
    """Project filtering parameters."""

    status: Optional[str] = Field(default=None, description="Filter by status")
    project_type: Optional[str] = Field(default=None, description="Filter by project type")
    priority: Optional[str] = Field(default=None, description="Filter by priority")
    city: Optional[str] = Field(default=None, description="Filter by city")
    state: Optional[str] = Field(default=None, description="Filter by state")
    owner_id: Optional[UUID] = Field(default=None, description="Filter by owner")
    date_from: Optional[datetime] = Field(default=None, description="Filter by creation date from")
    date_to: Optional[datetime] = Field(default=None, description="Filter by creation date to")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status filter."""
        if v is not None:
            valid_statuses = ["draft", "active", "on-hold", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v):
        """Validate project type filter."""
        if v is not None:
            valid_types = [
                "solar-farm", "wind-farm", "data-center", "telecom-tower",
                "residential", "commercial", "industrial", "mixed-use"
            ]
            if v not in valid_types:
                raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority filter."""
        if v is not None:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if v not in valid_priorities:
                raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v