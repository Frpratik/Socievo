"""Generic schemas for API responses, pagination, and health status."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standard success wrapper for single item or operation."""
    status: str = Field(default="success", description="Response status: success or error")
    data: Optional[DataT] = Field(default=None, description="Payload data")
    message: Optional[str] = Field(default=None, description="Human-readable informational message")
    request_id: Optional[str] = Field(default=None, description="Trace correlation ID")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total_records: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard response wrapper for paginated lists."""
    status: str = Field(default="success")
    items: List[DataT] = Field(default_factory=list)
    pagination: PaginationMeta
    request_id: Optional[str] = None


class HealthStatus(BaseModel):
    """Service health response schema."""
    app_name: str
    environment: str
    version: str
    status: str
    timestamp: str


class ServiceDependencyStatus(BaseModel):
    name: str
    status: str
    latency_ms: Optional[float] = None
    details: Optional[str] = None


class ReadinessStatus(BaseModel):
    """System readiness check response schema."""
    status: str
    dependencies: List[ServiceDependencyStatus]
    timestamp: str
