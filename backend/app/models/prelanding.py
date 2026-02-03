from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.scenario import Scenario


class PrelendingStatus(str, enum.Enum):
    """Status of a prelanding."""
    WINNER = "winner"
    GENERATED = "generated"
    TESTING = "testing"
    ARCHIVED = "archived"


class PrelendingFormat(str, enum.Enum):
    """Format/style of prelanding."""
    INTERVIEW = "interview"
    NEWS = "news"
    BLOG = "blog"
    REVIEW = "review"


class ElementType(str, enum.Enum):
    """Type of extracted element."""
    HEADING = "heading"
    SUBHEADING = "subheading"
    PARAGRAPH = "paragraph"
    DIALOGUE = "dialogue"
    QUOTE = "quote"
    CTA = "cta"
    IMAGE_DESC = "image_desc"


class Prelanding(Base):
    """Main prelanding model storing metadata and performance metrics."""
    
    __tablename__ = "prelandings"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), nullable=True)  # Original filename or display name
    geo = Column(String(2), nullable=False, index=True)  # Country code
    language = Column(String(5), nullable=False)  # Language code
    vertical = Column(String(50), nullable=False, index=True)  # e.g., crypto, finance
    format = Column(SQLEnum(PrelendingFormat), nullable=False)
    
    # Performance metrics
    ctr_to_landing = Column(Float, nullable=True)  # Click-through rate
    lead_rate = Column(Float, nullable=True)  # Lead conversion rate
    deposit_rate = Column(Float, nullable=True)  # Deposit conversion rate
    
    # Status and categorization
    status = Column(SQLEnum(PrelendingStatus), default=PrelendingStatus.TESTING)
    tags = Column(JSON, default=list)  # List of tags like "aggressive", "celebrity-angle"
    
    # File paths
    html_path = Column(String, nullable=False)
    screenshots_dir = Column(String, nullable=True)
    
    # Metadata
    date_added = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    elements = relationship("ExtractedElement", back_populates="prelanding", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prelanding {self.id} ({self.geo}/{self.vertical})>"


class ExtractedElement(Base):
    """Extracted structural elements from prelanding HTML."""
    
    __tablename__ = "extracted_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    prelanding_id = Column(String, ForeignKey("prelandings.id", ondelete="CASCADE"), nullable=False)
    
    element_type = Column(SQLEnum(ElementType), nullable=False)
    text_content = Column(Text, nullable=False)
    
    # For dialogue elements
    speaker = Column(String(100), nullable=True)  # e.g., "Host", "Expert"
    sentiment = Column(String(50), nullable=True)  # e.g., "skeptical", "confident"
    
    # Positioning
    order_index = Column(Integer, nullable=False)  # Order in document
    
    # Vector embedding reference (stored in Qdrant)
    embedding_id = Column(String, nullable=True)  # UUID in vector DB
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prelanding = relationship("Prelanding", back_populates="elements")
    
    def __repr__(self):
        return f"<ExtractedElement {self.id} ({self.element_type})>"


class GeneratedPrelanding(Base):
    """Tracking for AI-generated prelandings."""
    
    __tablename__ = "generated_prelandings"
    
    gen_id = Column(String, primary_key=True, index=True)
    
    # Generation parameters
    target_geo = Column(String(2), nullable=False)
    target_language = Column(String(5), nullable=False)
    target_vertical = Column(String(50), nullable=False)
    offer = Column(String(200), nullable=False)
    persona = Column(String(50), nullable=False)  # e.g., "aggressive_investigator"
    compliance_level = Column(String(50), nullable=False)
    
    # Source prelandings used
    source_prelanding_ids = Column(JSON, default=list)  # List of IDs

    # Scenario-based generation
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)

    # Three-part structure (for scenario-based generation)
    beginning_text = Column(Text, nullable=True)  # Beginning (teaser, 700-1000 chars)
    middle_text = Column(Text, nullable=True)  # Middle (main scenario)
    end_text = Column(Text, nullable=True)  # End (proofs + reviews)

    # Output
    generated_text = Column(Text, nullable=False)  # Full concatenated text
    generated_html = Column(Text, nullable=True)
    visual_brief = Column(Text, nullable=True)

    # Relationship to scenario
    scenario = relationship("Scenario")
    
    # Compliance checks
    compliance_issues = Column(JSON, default=list)
    compliance_passed = Column(Integer, default=1)  # Boolean as int
    
    # Performance tracking (filled via feedback)
    ctr_to_landing = Column(Float, nullable=True)
    lead_rate = Column(Float, nullable=True)
    deposit_rate = Column(Float, nullable=True)
    ban_rate = Column(Float, default=0.0)  # Rate of ad bans
    
    # Promotion to source
    promoted_to_source = Column(Integer, default=0)  # Boolean as int
    promoted_prelanding_id = Column(String, ForeignKey("prelandings.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<GeneratedPrelanding {self.gen_id}>"


class PatternProfile(Base):
    """Extracted pattern profile for deep analytics and RAG enhancement."""
    
    __tablename__ = "pattern_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    prelanding_id = Column(String, ForeignKey("prelandings.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Structural patterns
    structure_flow = Column(JSON, default=list)  # ["intro", "tension", "authority", "proof", "cta"]
    section_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    dialogue_count = Column(Integer, default=0)
    
    # Psychological triggers (0-1 intensity scores)
    trigger_fear = Column(Float, default=0.0)
    trigger_greed = Column(Float, default=0.0)
    trigger_urgency = Column(Float, default=0.0)
    trigger_fomo = Column(Float, default=0.0)
    trigger_social_proof = Column(Float, default=0.0)
    trigger_authority = Column(Float, default=0.0)
    trigger_curiosity = Column(Float, default=0.0)
    trigger_scarcity = Column(Float, default=0.0)
    
    # Tone and style (from GPT-4o analysis)
    tone = Column(String(50), default="neutral")  # aggressive, expert, friendly, tabloid, neutral
    persuasion_techniques = Column(JSON, default=list)  # ["objection_handling", "testimonials", ...]
    writing_style = Column(String(50), default="neutral")  # sensational, professional, conversational
    
    # CTA analysis
    cta_count = Column(Integer, default=0)
    cta_positions = Column(JSON, default=list)  # [0.3, 0.7, 0.95] - relative positions (0-1)
    cta_urgency_level = Column(Float, default=0.0)  # 0-1 how urgent are CTAs
    
    # Content metrics
    headline_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    image_desc_count = Column(Integer, default=0)
    
    # AI analysis summary (from GPT-4o)
    ai_analysis_summary = Column(Text, nullable=True)  # Full AI analysis text
    key_selling_points = Column(JSON, default=list)  # Main arguments/hooks
    target_audience = Column(String(200), nullable=True)  # Detected target audience
    
    # Embedding for pattern-based search
    profile_embedding_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    prelanding = relationship("Prelanding", backref="pattern_profile")
    
    def __repr__(self):
        return f"<PatternProfile for {self.prelanding_id} (tone={self.tone})>"
    
    def get_trigger_scores(self) -> dict:
        """Return all trigger scores as a dictionary."""
        return {
            "fear": self.trigger_fear,
            "greed": self.trigger_greed,
            "urgency": self.trigger_urgency,
            "fomo": self.trigger_fomo,
            "social_proof": self.trigger_social_proof,
            "authority": self.trigger_authority,
            "curiosity": self.trigger_curiosity,
            "scarcity": self.trigger_scarcity
        }
    
    def get_top_triggers(self, threshold: float = 0.5) -> list:
        """Return triggers above threshold, sorted by score."""
        triggers = self.get_trigger_scores()
        return sorted(
            [(k, v) for k, v in triggers.items() if v >= threshold],
            key=lambda x: x[1],
            reverse=True
        )


class PerformanceFeedback(Base):
    """Performance metrics feedback for active learning."""
    
    __tablename__ = "performance_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    gen_id = Column(String, ForeignKey("generated_prelandings.gen_id"), nullable=False, index=True)
    
    # Metrics
    ctr_to_landing = Column(Float, nullable=True)
    lead_rate = Column(Float, nullable=True)
    deposit_rate = Column(Float, nullable=True)
    ban_rate = Column(Float, default=0.0)
    
    # Sample size
    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    
    # Timestamp
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PerformanceFeedback {self.id} for {self.gen_id}>"
