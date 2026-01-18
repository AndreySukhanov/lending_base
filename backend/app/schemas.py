from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Prelanding schemas
class PrelendingMetrics(BaseModel):
    """Performance metrics for prelanding."""
    ctr_to_landing: Optional[float] = None
    lead_rate: Optional[float] = None
    deposit_rate: Optional[float] = None


class PrelendingResponse(BaseModel):
    """Response schema for prelanding."""
    id: str
    name: Optional[str] = None
    geo: str
    language: str
    vertical: str
    format: str
    status: str
    tags: List[str] = []
    ctr_to_landing: Optional[float] = None
    lead_rate: Optional[float] = None
    deposit_rate: Optional[float] = None
    html_path: Optional[str] = None
    screenshots_dir: Optional[str] = None
    date_added: datetime
    
    class Config:
        from_attributes = True


# Generation schemas
class GenerationRequest(BaseModel):
    """Request schema for generating new prelanding."""
    geo: str = Field(..., max_length=2, description="Target country code")
    language: str = Field(..., max_length=5, description="Target language code")
    vertical: str = Field(..., description="Vertical (crypto, finance, etc.)")
    offer: str = Field(..., description="What is being promoted")
    persona: str = Field(default="aggressive_investigator", description="Writing persona")
    compliance_level: str = Field(default="strict_facebook", description="Compliance level")
    format: str = Field(default="interview", description="Output format")
    target_length: int = Field(default=800, description="Target word count")
    use_rag: bool = Field(default=True, description="Whether to use RAG for generation")


class GenerationResponse(BaseModel):
    """Response schema for generation."""
    gen_id: str
    generated_text: str
    generated_html: Optional[str] = None

    compliance_passed: bool
    compliance_issues: List[dict] = []
    compliance_warnings: List[dict] = []
    source_prelanding_ids: List[str] = []
    tokens_used: int
    created_at: datetime


class ExportRequest(BaseModel):
    """Request schema for exporting generated copy."""
    format: str = Field(..., description="Export format: text, html")


class ExportResponse(BaseModel):
    """Response schema for export."""
    content: str
    format: str


# Feedback schemas
class FeedbackSubmission(BaseModel):
    """Schema for submitting performance feedback."""
    gen_id: str
    ctr_to_landing: Optional[float] = None
    lead_rate: Optional[float] = None
    deposit_rate: Optional[float] = None
    ban_rate: float = Field(default=0.0)
    impressions: Optional[int] = None
    clicks: Optional[int] = None


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission."""
    success: bool
    message: str
    promoted_to_source: bool = False
    promoted_prelanding_id: Optional[str] = None
