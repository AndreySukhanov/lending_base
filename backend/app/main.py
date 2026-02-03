from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import prelandings, generation, feedback, scenarios, generators
from app.config import settings
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="AI Prelanding Copy Engine",
    description="Generate high-converting prelanding copy using AI with RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:3001",
        "http://24.199.119.198",
        "http://24.199.119.198:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prelandings.router)
app.include_router(generation.router)
app.include_router(feedback.router)
app.include_router(scenarios.router)
app.include_router(generators.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI Prelanding Copy Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
