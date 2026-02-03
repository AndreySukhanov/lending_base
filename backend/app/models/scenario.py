from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from app.database import Base


class Scenario(Base):
    """Scenario model for structured prelanding generation."""

    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "Investigation", "Talk Show", etc.
    name_ru = Column(String(100), nullable=False)  # Russian name
    description = Column(Text, nullable=True)  # Description of the scenario

    # Template prompts for each part
    beginning_template = Column(Text, nullable=False)  # Prompt for beginning (700-1000 chars)
    middle_template = Column(Text, nullable=False)  # Prompt for middle (main scenario)
    end_template = Column(Text, nullable=False)  # Prompt for end (proofs + reviews)

    # Metadata
    structure_guidelines = Column(JSON, default=dict)  # Additional instructions
    active = Column(Boolean, default=True)  # Is scenario active
    order_index = Column(Integer, default=0)  # Display order

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Scenario {self.id}: {self.name_ru}>"
