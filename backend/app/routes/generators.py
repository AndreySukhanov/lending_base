from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.config import settings
from app.services.name_generator import NameGenerator
from app.services.review_generator import ReviewGenerator
from app.schemas import (
    NameGenerationRequest,
    NameResponse,
    ReviewGenerationRequest,
    ReviewResponse
)


router = APIRouter(prefix="/api/generators", tags=["generators"])


def get_openai_api_key():
    """Dependency to get OpenAI API key."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    return settings.openai_api_key


@router.post("/names", response_model=List[NameResponse])
async def generate_names(
    request: NameGenerationRequest,
    api_key: str = Depends(get_openai_api_key)
):
    """Generate realistic names for specified GEO and gender."""
    try:
        generator = NameGenerator(api_key)
        names = await generator.generate_names(
            geo=request.geo,
            gender=request.gender,
            count=request.count,
            include_nickname=request.include_nickname
        )
        return names
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate names: {str(e)}"
        )


@router.post("/reviews", response_model=List[ReviewResponse])
async def generate_reviews(
    request: ReviewGenerationRequest,
    api_key: str = Depends(get_openai_api_key)
):
    """Generate realistic reviews for investment platform."""
    try:
        generator = ReviewGenerator(api_key)
        reviews = await generator.generate_reviews(
            geo=request.geo,
            language=request.language,
            vertical=request.vertical,
            length=request.length,
            count=request.count,
            names=request.names
        )
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate reviews: {str(e)}"
        )
