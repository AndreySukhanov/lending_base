from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.database import get_db
from app.models import GeneratedPrelanding
from app.schemas import GenerationRequest, GenerationResponse, ExportRequest, ExportResponse
from app.services import CopyGenerator, OutputFormatter

router = APIRouter(prefix="/api/generate", tags=["generation"])


@router.post("/", response_model=GenerationResponse)
def generate_prelanding(
    request: GenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate new prelanding copy using AI with RAG.
    """
    try:
        print(f"Starting generation for offer: {request.offer}")
        
        # Generate copy
        generator = CopyGenerator(db)
        print("CopyGenerator created successfully")
        
        result = generator.generate_prelanding_copy(
            geo=request.geo,
            language=request.language,
            vertical=request.vertical,
            offer=request.offer,
            persona=request.persona,
            compliance_level=request.compliance_level,
            format_type=request.format,
            target_length=request.target_length,
            use_rag=request.use_rag
        )
        print("Generation completed successfully")
        
        # Create gen_id
        gen_id = f"gen_{uuid.uuid4().hex[:12]}"
        
        # Format outputs
        formatter = OutputFormatter()
        generated_html = formatter.format_as_html(result['generated_text'])
        print("Formatting completed")
        
        # Store in database
        generated_record = GeneratedPrelanding(
            gen_id=gen_id,
            target_geo=request.geo,
            target_language=request.language,
            target_vertical=request.vertical,
            offer=request.offer,
            persona=request.persona,
            compliance_level=request.compliance_level,
            source_prelanding_ids=result.get('source_prelanding_ids', []),
            generated_text=result['generated_text'],
            generated_html=generated_html,
            compliance_issues=result['compliance'].get('issues', []),
            compliance_passed=1 if result['compliance']['passed'] else 0
        )
        
        db.add(generated_record)
        db.commit()
        print("Saved to database")
        
        return GenerationResponse(
            gen_id=gen_id,
            generated_text=result['generated_text'],
            generated_html=generated_html,

            compliance_passed=result['compliance']['passed'],
            compliance_issues=result['compliance'].get('issues', []),
            compliance_warnings=result['compliance'].get('warnings', []),
            source_prelanding_ids=result.get('source_prelanding_ids', []),
            tokens_used=result.get('tokens_used', 0),
            created_at=datetime.utcnow()
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{gen_id}")
def get_generated_prelanding(gen_id: str, db: Session = Depends(get_db)):
    """Get a generated prelanding by ID."""
    generated = db.query(GeneratedPrelanding).filter(GeneratedPrelanding.gen_id == gen_id).first()
    if not generated:
        raise HTTPException(status_code=404, detail="Generated prelanding not found")
    
    return {
        "gen_id": generated.gen_id,
        "generated_text": generated.generated_text,
        "generated_html": generated.generated_html,
        "generated_html": generated.generated_html,
        "compliance_passed": bool(generated.compliance_passed),
        "created_at": generated.created_at
    }


@router.post("/{gen_id}/export", response_model=ExportResponse)
def export_generated_prelanding(
    gen_id: str,
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """Export generated prelanding in specified format."""
    generated = db.query(GeneratedPrelanding).filter(GeneratedPrelanding.gen_id == gen_id).first()
    if not generated:
        raise HTTPException(status_code=404, detail="Generated prelanding not found")
    
    if request.format == "text":
        content = generated.generated_text
    elif request.format == "html":
        content = generated.generated_html
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use: text or html")
    
    return ExportResponse(
        content=content,
        format=request.format
    )
