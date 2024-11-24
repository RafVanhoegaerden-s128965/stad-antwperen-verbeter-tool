from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
import os

# Import routers
from routers import (
    raw_texts,
    suggestions,
    final_texts,
    elastic,
    scraper
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stad Antwerpen API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# Include all routers
app.include_router(
    raw_texts.router,
    prefix="/api",
    tags=["Raw Texts"]
)

app.include_router(
    suggestions.router,
    prefix="/api",
    tags=["Suggestions"]
)

app.include_router(
    final_texts.router,
    prefix="/api",
    tags=["Final Texts"]
)

app.include_router(
    elastic.router,
    prefix="/api",
    tags=["Elasticsearch"]
)

app.include_router(
    scraper.router,
    prefix="/api",
    tags=["Scraper"]
)

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
