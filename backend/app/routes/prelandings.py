from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import shutil
import uuid
import zipfile
import tempfile
from datetime import datetime

from app.database import get_db
from app.models import Prelanding, ExtractedElement, PrelendingStatus, PrelendingFormat, ElementType
from app.schemas import PrelendingResponse, PrelendingMetrics
from app.services import HTMLParser, VisionAnalyzer, EmbeddingService
from app.config import settings

router = APIRouter(prefix="/api/prelandings", tags=["prelandings"])


@router.post("/upload-zip")
async def upload_prelanding_zip(
    zip_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a prelanding as a ZIP archive.
    
    Expected ZIP structure:
    - index.html (required) - main HTML file
    - meta.json (required) - metadata with geo, vertical, metrics, etc.
    - screenshots/ (optional) - folder with screenshots
    - Any .png/.jpg/.jpeg/.webp files (optional) - will be treated as screenshots
    """
    if not zip_file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    
    # Extract original filename (without .zip extension)
    original_name = os.path.splitext(zip_file.filename)[0]
    
    try:
        # Create temp directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded ZIP
            zip_path = os.path.join(temp_dir, "upload.zip")
            with open(zip_path, "wb") as f:
                content = await zip_file.read()
                f.write(content)
            
            # Extract ZIP
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find HTML file
            html_content = None
            html_filename = None
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith('.html'):
                        html_path = os.path.join(root, file)
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        html_filename = file
                        break
                if html_content:
                    break
            
            if not html_content:
                raise HTTPException(status_code=400, detail="No HTML file found in ZIP")
            
            # Find meta.json
            meta = {"id": f"pl_{uuid.uuid4().hex[:8]}", "geo": "US", "language": "en", "vertical": "general", "format": "interview", "status": "testing", "tags": [], "metrics": {}}
            for root, dirs, files in os.walk(extract_dir):
                if 'meta.json' in files:
                    meta_path = os.path.join(root, 'meta.json')
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    break
            
            prelanding_id = meta.get('id', f"pl_{uuid.uuid4().hex[:8]}")
            
            # Create upload directory
            upload_path = os.path.join(settings.upload_dir, prelanding_id)
            os.makedirs(upload_path, exist_ok=True)
            screenshots_path = os.path.join(upload_path, "screenshots")
            os.makedirs(screenshots_path, exist_ok=True)
            
            # Save HTML
            final_html_path = os.path.join(upload_path, "index.html")
            with open(final_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Find and save screenshots
            screenshot_paths = []
            image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(screenshots_path, file)
                        shutil.copy2(src_path, dst_path)
                        screenshot_paths.append(dst_path)
            
            # Auto-detect vertical if not specified in meta.json
            parser = HTMLParser()
            detected_vertical = parser.detect_vertical(html_content)
            final_vertical = meta.get('vertical') or detected_vertical
            
            # Create prelanding record - all uploaded are winners (best examples)
            prelanding = Prelanding(
                id=prelanding_id,
                name=original_name,  # Save original filename
                geo=meta.get('geo', 'US'),
                language=meta.get('language', 'en'),
                vertical=final_vertical,  # Auto-detected or from meta.json
                format=PrelendingFormat(meta.get('format', 'interview')),
                ctr_to_landing=meta.get('metrics', {}).get('ctr_to_landing'),
                lead_rate=meta.get('metrics', {}).get('lead_rate'),
                deposit_rate=meta.get('metrics', {}).get('deposit_rate'),
                status=PrelendingStatus(meta.get('status', 'winner')),  # Default to winner
                tags=meta.get('tags', []),
                html_path=final_html_path,
                screenshots_dir=screenshots_path if screenshot_paths else None
            )
            
            db.add(prelanding)
            db.commit()
            
            # Parse HTML and extract elements
            parser = HTMLParser()
            extracted = parser.parse_html(html_content)
            
            # Store extracted elements with embeddings
            try:
                embedding_service = EmbeddingService()
                
                for element_type, elements in extracted.items():
                    for elem in elements:
                        db_element = ExtractedElement(
                            prelanding_id=prelanding_id,
                            element_type=ElementType(elem.get('type', element_type)),
                            text_content=elem['text'],
                            speaker=elem.get('speaker'),
                            sentiment=elem.get('sentiment'),
                            order_index=elem.get('order', 0)
                        )
                        
                        performance_score = prelanding.lead_rate or 0.0
                        try:
                            embedding_id = embedding_service.store_element_embedding(
                                text=elem['text'],
                                prelanding_id=prelanding_id,
                                element_type=str(elem.get('type', element_type)),
                                performance_score=performance_score,
                                metadata={
                                    'geo': prelanding.geo,
                                    'vertical': prelanding.vertical,
                                    'speaker': elem.get('speaker'),
                                    'sentiment': elem.get('sentiment')
                                }
                            )
                            db_element.embedding_id = embedding_id
                        except Exception as embed_err:
                            print(f"Embedding error: {embed_err}")
                        
                        db.add(db_element)
            except Exception as parse_err:
                print(f"Parsing/embedding error: {parse_err}")
            
            db.commit()
            db.refresh(prelanding)
            
            return {
                "success": True,
                "prelanding_id": prelanding_id,
                "name": original_name,  # Original ZIP filename
                "message": f"Successfully uploaded prelanding {original_name}",
                "html_found": html_filename,
                "screenshots_count": len(screenshot_paths),
                "elements_extracted": sum(len(v) for v in extracted.values()),
                "vertical_detected": final_vertical  # Show auto-detected category
            }
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_prelanding(
    html_file: UploadFile = File(...),
    meta_json: str = Form(...),
    screenshots: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    """
    Upload a new prelanding with HTML, metadata, and screenshots.
    """
    try:
        # Parse metadata
        meta = json.loads(meta_json)
        prelanding_id = meta.get('id', f"pl_{uuid.uuid4().hex[:8]}")
        
        # Create upload directory
        upload_path = os.path.join(settings.upload_dir, prelanding_id)
        os.makedirs(upload_path, exist_ok=True)
        screenshots_path = os.path.join(upload_path, "screenshots")
        os.makedirs(screenshots_path, exist_ok=True)
        
        # Save HTML file
        html_path = os.path.join(upload_path, "index.html")
        with open(html_path, "wb") as f:
            content = await html_file.read()
            f.write(content)
        
        # Save screenshots
        screenshot_paths = []
        for screenshot in screenshots:
            screenshot_path = os.path.join(screenshots_path, screenshot.filename)
            with open(screenshot_path, "wb") as f:
                f.write(await screenshot.read())
            screenshot_paths.append(screenshot_path)
        
        # Create prelanding record
        prelanding = Prelanding(
            id=prelanding_id,
            geo=meta.get('geo', 'US'),
            language=meta.get('language', 'en'),
            vertical=meta.get('vertical', 'general'),
            format=PrelendingFormat(meta.get('format', 'interview')),
            ctr_to_landing=meta.get('metrics', {}).get('ctr_to_landing'),
            lead_rate=meta.get('metrics', {}).get('lead_rate'),
            deposit_rate=meta.get('metrics', {}).get('deposit_rate'),
            status=PrelendingStatus(meta.get('status', 'testing')),
            tags=meta.get('tags', []),
            html_path=html_path,
            screenshots_dir=screenshots_path if screenshot_paths else None
        )
        
        db.add(prelanding)
        db.commit()
        
        # Parse HTML and extract elements
        parser = HTMLParser()
        html_content = content.decode('utf-8')
        extracted = parser.parse_html(html_content)
        
        # Store extracted elements
        embedding_service = EmbeddingService()
        
        for element_type, elements in extracted.items():
            for elem in elements:
                # Create database record
                db_element = ExtractedElement(
                    prelanding_id=prelanding_id,
                    element_type=ElementType(elem.get('type', element_type)),
                    text_content=elem['text'],
                    speaker=elem.get('speaker'),
                    sentiment=elem.get('sentiment'),
                    order_index=elem.get('order', 0)
                )
                
                # Create and store embedding
                performance_score = prelanding.lead_rate or 0.0
                embedding_id = embedding_service.store_element_embedding(
                    text=elem['text'],
                    prelanding_id=prelanding_id,
                    element_type=str(elem.get('type', element_type)),
                    performance_score=performance_score,
                    metadata={
                        'geo': prelanding.geo,
                        'vertical': prelanding.vertical,
                        'speaker': elem.get('speaker'),
                        'sentiment': elem.get('sentiment')
                    }
                )
                
                db_element.embedding_id = embedding_id
                db.add(db_element)
        
        # Analyze screenshots if provided
        if screenshot_paths:
            vision_analyzer = VisionAnalyzer()
            for screenshot_path in screenshot_paths:
                try:
                    analysis = vision_analyzer.analyze_screenshot(screenshot_path)
                    # Store image descriptions as elements
                    image_prompts = vision_analyzer.generate_image_prompts(analysis)
                    for i, prompt in enumerate(image_prompts):
                        db_element = ExtractedElement(
                            prelanding_id=prelanding_id,
                            element_type=ElementType.IMAGE_DESC,
                            text_content=prompt,
                            order_index=1000 + i  # High order to keep at end
                        )
                        db.add(db_element)
                except Exception as e:
                    print(f"Error analyzing screenshot: {e}")
        
        db.commit()
        db.refresh(prelanding)
        
        return {
            "success": True,
            "prelanding_id": prelanding_id,
            "message": f"Uploaded and processed prelanding {prelanding_id}"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PrelendingResponse])
def list_prelandings(
    geo: Optional[str] = None,
    vertical: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List prelandings with optional filters."""
    query = db.query(Prelanding)
    
    if geo:
        query = query.filter(Prelanding.geo == geo)
    if vertical:
        query = query.filter(Prelanding.vertical == vertical)
    if status:
        query = query.filter(Prelanding.status == status)
    
    prelandings = query.order_by(Prelanding.date_added.desc()).offset(skip).limit(limit).all()
    return prelandings


@router.get("/{prelanding_id}", response_model=PrelendingResponse)
def get_prelanding(prelanding_id: str, db: Session = Depends(get_db)):
    """Get details of a specific prelanding."""
    prelanding = db.query(Prelanding).filter(Prelanding.id == prelanding_id).first()
    if not prelanding:
        raise HTTPException(status_code=404, detail="Prelanding not found")
    return prelanding


@router.get("/top/{metric}")
def get_top_performers(
    metric: str = "lead_rate",
    geo: Optional[str] = None,
    vertical: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top performing prelandings by metric."""
    query = db.query(Prelanding).filter(Prelanding.status == PrelendingStatus.WINNER)
    
    if geo:
        query = query.filter(Prelanding.geo == geo)
    if vertical:
        query = query.filter(Prelanding.vertical == vertical)
    
    # Get metric column
    from sqlalchemy import desc
    metric_column = getattr(Prelanding, metric, Prelanding.lead_rate)
    query = query.filter(metric_column.isnot(None)).order_by(desc(metric_column))
    
    return query.limit(limit).all()


@router.delete("/{prelanding_id}")
async def delete_prelanding(
    prelanding_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a prelanding by ID.
    Also removes associated files and extracted elements.
    """
    # Find the prelanding
    prelanding = db.query(Prelanding).filter(Prelanding.id == prelanding_id).first()
    
    if not prelanding:
        raise HTTPException(status_code=404, detail=f"Prelanding {prelanding_id} not found")
    
    # Delete files from disk
    try:
        upload_path = os.path.join(settings.upload_dir, prelanding_id)
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)
    except Exception as e:
        print(f"Error deleting files for {prelanding_id}: {e}")
    
    # Delete from database (cascade will handle extracted elements)
    db.delete(prelanding)
    db.commit()
    
    return {
        "success": True,
        "message": f"Prelanding {prelanding_id} deleted successfully"
    }
