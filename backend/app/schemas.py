from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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


# Scenario schemas
class ScenarioBase(BaseModel):
    """Base schema for Scenario."""
    name: str
    name_ru: str
    description: Optional[str] = None
    beginning_template: str
    middle_template: str
    end_template: str
    structure_guidelines: Optional[Dict[str, Any]] = None
    active: bool = True
    order_index: int = 0


class ScenarioCreate(ScenarioBase):
    """Schema for creating a new scenario."""
    pass


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario."""
    name: Optional[str] = None
    name_ru: Optional[str] = None
    description: Optional[str] = None
    beginning_template: Optional[str] = None
    middle_template: Optional[str] = None
    end_template: Optional[str] = None
    structure_guidelines: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    order_index: Optional[int] = None


class ScenarioResponse(ScenarioBase):
    """Response schema for Scenario."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Name generation schemas
class NameGenerationRequest(BaseModel):
    """Request schema for name generation."""
    geo: str = Field(..., description="Target country")
    gender: str = Field(..., description="Gender: male, female, or random")
    count: int = Field(default=10, ge=1, le=50, description="Number of names to generate")
    include_nickname: bool = Field(default=True, description="Include nickname/username")


class NameResponse(BaseModel):
    """Response schema for generated name."""
    first_name: str
    last_name: str
    nickname: Optional[str] = None
    gender: str


# Review generation schemas
class ReviewGenerationRequest(BaseModel):
    """Request schema for review generation."""
    geo: str = Field(..., description="Target country")
    language: str = Field(..., description="Target language")
    vertical: str = Field(..., description="Vertical (crypto, forex, etc.)")
    length: str = Field(..., description="Length: short (50-100) or medium (150-300)")
    count: int = Field(default=5, ge=1, le=20, description="Number of reviews to generate")
    names: Optional[List[Dict[str, str]]] = Field(default=None, description="Optional list of names to use")


class ReviewResponse(BaseModel):
    """Response schema for generated review."""
    author_name: str
    text: str
    rating: int
    amount: float
    currency: str
    screenshot_description: str


# Scenario generation schemas
class ScenarioGenerationRequest(BaseModel):
    """Request schema for scenario-based generation."""
    scenario_id: int = Field(..., description="Scenario ID to use")
    geo: str = Field(..., max_length=2, description="Target country code")
    language: str = Field(..., max_length=5, description="Target language code")
    vertical: str = Field(..., description="Vertical (crypto, finance, etc.)")
    offer: str = Field(..., description="What is being promoted")
    persona: str = Field(default="aggressive_investigator", description="Writing persona")
    compliance_level: str = Field(default="strict_facebook", description="Compliance level")
    use_rag: bool = Field(default=True, description="Whether to use RAG for generation")


class ScenarioGenerationResponse(BaseModel):
    """Response schema for scenario-based generation."""
    gen_id: str
    beginning: str
    middle: str
    end: str
    full_text: str
    generated_html: Optional[str] = None
    scenario: Dict[str, Any]
    compliance_passed: bool = True
    compliance_issues: List[dict] = []
    tokens_used: int = 0
    created_at: datetime
