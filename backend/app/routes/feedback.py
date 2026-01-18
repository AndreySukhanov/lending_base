from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import GeneratedPrelanding, PerformanceFeedback, Prelanding, PrelendingStatus, PrelendingFormat
from app.schemas import FeedbackSubmission, FeedbackResponse
from app.config import settings

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit performance feedback for a generated prelanding.
    Implements active learning loop with auto-promotion.
    """
    # Find generated prelanding
    generated = db.query(GeneratedPrelanding).filter(
        GeneratedPrelanding.gen_id == feedback.gen_id
    ).first()
    
    if not generated:
        raise HTTPException(status_code=404, detail="Generated prelanding not found")
    
    # Create feedback record
    feedback_record = PerformanceFeedback(
        gen_id=feedback.gen_id,
        ctr_to_landing=feedback.ctr_to_landing,
        lead_rate=feedback.lead_rate,
        deposit_rate=feedback.deposit_rate,
        ban_rate=feedback.ban_rate,
        impressions=feedback.impressions,
        clicks=feedback.clicks
    )
    
    db.add(feedback_record)
    
    # Update generated prelanding metrics
    generated.ctr_to_landing = feedback.ctr_to_landing
    generated.lead_rate = feedback.lead_rate
    generated.deposit_rate = feedback.deposit_rate
    generated.ban_rate = feedback.ban_rate
    generated.updated_at = datetime.utcnow()
    
    promoted = False
    promoted_id = None
    
    # Check for auto-promotion
    if feedback.lead_rate and feedback.lead_rate >= settings.auto_promotion_threshold:
        # Check if not already promoted
        if not generated.promoted_to_source:
            # Promote to source library
            promoted_id = f"{generated.gen_id}_promoted"
            
            new_prelanding = Prelanding(
                id=promoted_id,
                geo=generated.target_geo,
                language=generated.target_language,
                vertical=generated.target_vertical,
                format=PrelendingFormat.INTERVIEW,  # TODO: make dynamic
                ctr_to_landing=feedback.ctr_to_landing,
                lead_rate=feedback.lead_rate,
                deposit_rate=feedback.deposit_rate,
                status=PrelendingStatus.WINNER,
                tags=["ai-generated", "promoted"],
                html_path=f"generated/{generated.gen_id}.html",
                date_added=datetime.utcnow()
            )
            
            db.add(new_prelanding)
            
            # Mark as promoted
            generated.promoted_to_source = 1
            generated.promoted_prelanding_id = promoted_id
            
            promoted = True
    
    db.commit()
    
    return FeedbackResponse(
        success=True,
        message="Feedback submitted successfully",
        promoted_to_source=promoted,
        promoted_prelanding_id=promoted_id
    )


@router.get("/{gen_id}/feedback")
def get_feedback_history(gen_id: str, db: Session = Depends(get_db)):
    """Get all feedback history for a generated prelanding."""
    feedback_records = db.query(PerformanceFeedback).filter(
        PerformanceFeedback.gen_id == gen_id
    ).order_by(PerformanceFeedback.submitted_at.desc()).all()
    
    return {
        "gen_id": gen_id,
        "feedback_count": len(feedback_records),
        "feedback": [
            {
                "lead_rate": f.lead_rate,
                "ctr_to_landing": f.ctr_to_landing,
                "deposit_rate": f.deposit_rate,
                "ban_rate": f.ban_rate,
                "submitted_at": f.submitted_at
            }
            for f in feedback_records
        ]
    }
